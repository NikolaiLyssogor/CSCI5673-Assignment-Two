import grpc
import database_pb2
import database_pb2_grpc

import pickle
import json
from flask import Flask, request, Response

# Define Flask service
app = Flask(__name__)
# Stub for communicating with customer database
customer_channel = grpc.insecure_channel('localhost:50051')
customer_stub = database_pb2_grpc.databaseStub(customer_channel)
# Stub for communicating with product database
product_channel = grpc.insecure_channel('localhost:50052')
product_stub = database_pb2_grpc.databaseStub(product_channel)

@app.route('/createAccount', methods=['POST'])
def createAccount():
    data = json.loads(request.data)
    unm, pwd = data['username'], data['password']

    # Check if username is already taken
    try:
        sql = f"SELECT * FROM buyers WHERE username = '{unm}'"
        db_response = query_database(sql, 'customer')
    except:
        response = json.dumps({'status': 'Error: Failed to connect to database'})
        return Response(response=response, status=500)
    else:
        if isinstance(db_response, dict):
            return Response(response=db_response, status=500)
        if db_response:
            # Username taken
            response = json.dumps({'status': 'Error: Username already taken'})
            return Response(response=response, status=400)

    # Create new account
    try:
        sql = f"""
            INSERT INTO buyers ('username', 'password') VALUES
            ('{unm}', '{pwd}')
        """
        db_response = query_database(sql, 'customer')
    except:
        response = json.dumps({'status': 'Error: Failed to connect to database'})
        return Response(response=response, status=500)
    else:
        # Check for database error
        if 'Error' in db_response['status']:
            response = json.dumps(db_response)
        else:
            response = json.dumps({'status': 'Success: Account created successfully'})

        return Response(response=response, status=200)
    

@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    unm, pwd = data['username'], data['password']

    try:
        sql = f"SELECT * FROM buyers WHERE username = '{unm}'"
        db_response = query_database(sql, 'customer')
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
                    # Found user, need to update DB that they are logged in
                    response = json.dumps({'status': 'Success: Login successful'})
                    sql = f"""
                        UPDATE buyers SET is_logged_in = 'true'
                        WHERE username = '{unm}' AND password = '{pwd}'
                    """
                    try:
                        db_response2 = query_database(sql, 'customer')
                    except:
                        response = json.dumps({'status': 'Error: Failed to connect to database'})
                        return Response(response=response, status=500)
                    else:
                        if 'Error' in db_response2['status']:
                            return Response(response=db_response2, status=500)
                        else:
                            break

        return Response(response=response, status=200)

@app.route('/logout', methods=['POST'])
def logout():
    data = json.loads(request.data)
    unm = data['username']
    sql = f"""
        UPDATE buyers SET is_logged_in = 'false'
        WHERE username = '{unm}'
    """

    try:
        db_response = query_database(sql, 'customer')
    except:
        response = json.dumps({'status': 'Error: Failed to connect to database'})
        return Response(response=response, status=500)
    else:
        if 'Error' in db_response['status']:
            return Response(response=db_response, status=500)
        else:
            response = json.dumps({'status': 'Success: You have logged out'})
            return Response(response=response, status=200)


@app.route('/checkIfLoggedIn', methods=['POST'])
def check_if_logged_in():
    data = json.loads(request.data)
    unm = data['username']

    try:
        # Check the DB if the user is logged in
        sql = f"SELECT is_logged_in FROM buyers WHERE username = '{unm}'"
        db_response = query_database(sql, 'customer')
    except:
        # Return database connection error
        response = json.dumps({'status': 'Error: Failed to connect to database'})
        return Response(response=response, status=500)
    else:
        # DB server couldn't connect to DB
        if isinstance(db_response, dict):
            return Response(response=db_response, status=500)
        
        if not db_response:
            # No such account so not logged in
            response = json.dumps({'is_logged_in': False})
        else:
            # Account exists: Check if logged in or not
            is_logged_in = True if db_response[0][0] == 'true' else False
            response = json.dumps({'is_logged_in': is_logged_in})

        return Response(response=response, status=200)

def query_database(sql: str, db: str):
    """
    Sends a query over gRPC to the database and returns 
    the object that the database returns.
    """
    if db == 'product':
        stub = product_stub
    elif db == 'customer':
        stub = customer_stub

    query = database_pb2.databaseRequest(query=sql)
    db_response = stub.queryDatabase(request=query)
    return pickle.loads(db_response.db_response)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)