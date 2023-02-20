import grpc
import database_pb2
import database_pb2_grpc

import pickle
import json
from flask import Flask, request, Response


app = Flask(__name__)
channel = grpc.insecure_channel('localhost:50051')
stub = database_pb2_grpc.databaseStub(channel)

@app.route('/createAccount', methods=['POST'])
def createAccount():
    data = json.loads(request.data)
    unm, pwd = data['username'], data['password']
    try:
        # Form the database query
        query = database_pb2.databaseRequest(query= f"""
            INSERT INTO sellers ('username', 'password') VALUES
            ('{unm}', '{pwd}')
        """)
        # Query the DB and decode the response
        db_response = stub.changeDatabase(request=query)
        db_response = pickle.loads(db_response.db_response)
    except:
        response = json.dumps({'status': 'Error: Failed to connect to database'})
        return Response(response=response, status=500)
    else:
        # Check for database error
        if isinstance(db_response, dict):
            response = json.dumps(db_response)
        else:
            response = json.dumps({'status': 'Success: Account created successfully'})

        return Response(response=response, status=200)
    

@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    unm, pwd = data['username'], data['password']

    try:
        query = database_pb2.databaseRequest(query= f"""
            SELECT * FROM sellers
            WHERE username = '{unm}'
        """)
        db_response = stub.queryDatabase(request=query)
        db_response = pickle.loads(db_response.db_response)
        print("db_response", db_response)
    except:
        response = json.dumps({'status': 'Error: Failed to connect to database'})
        return Response(response=response, status=500)
    else:
        # Check for database error
        if isinstance(db_response, dict):
            response = json.dumps(db_response)
        elif not db_response:
            # Username not found
            response = json.dumps({'status': 'Error: Username not found'})
        else:
            # Check if username is in database
            response = json.dumps({'status': 'Error: Incorrect password'})
            for user in db_response:
                if user[1] == pwd:
                    response = json.dumps({'status': 'Login successful'})
                    break

        return Response(response=response, status=200)
        

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    # channel = grpc.insecure_channel('localhost:50051')
    # stub = database_pb2_grpc.databaseStub(channel)
    # query = \
    # """
    # INSERT INTO sellers VALUES
    #     ('mike', 4, 'blanket')
    # """
    # data = database_pb2.databaseRequest(query=query)
    # response = stub.changeDatabase(request=data)
    # print(pickle.loads(response.db_response))

    # q1 = "SELECT * FROM sellers"
    # data = database_pb2.databaseRequest(query=q1)
    # response = stub.queryDatabase(request=data)
    # print(pickle.loads(response.db_response))