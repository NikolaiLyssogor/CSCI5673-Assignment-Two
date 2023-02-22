import grpc
import database_pb2
import database_pb2_grpc

import pickle
import json
from flask import Flask, request, Response
from suds.client import Client


# Define Flask service
app = Flask(__name__)
# Stub for communicating with customer database
customer_channel = grpc.insecure_channel('localhost:50051')
customer_stub = database_pb2_grpc.databaseStub(customer_channel)
# Stub for communicating with product database
product_channel = grpc.insecure_channel('localhost:50052')
product_stub = database_pb2_grpc.databaseStub(product_channel)
# Stub for communicating with the SOAP transactions database
soap_client = Client('http://localhost:7789/?wsdl')


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
@app.route('/search', methods=['POST'])
def search():
    data = json.loads(request.data)
    sql = f"SELECT rowid, * FROM products WHERE category = {data['category']}"
    for keyword in data['keywords']:
        sql += f" OR keywords LIKE '%{keyword}%'"

    try:
        db_response = query_database(sql, 'product')
    except:
        response = json.dumps({'status': 'Error: Failed to connect to database'})
        return Response(response=response, status=500)
    else:
        if isinstance(db_response, dict):
            return Response(response=db_response, status=500)

    # Return result as json
    items = products_query_to_json(db_response)
    response = json.dumps({
        'status': 'Success: Items queried successfully',
        'items': items
    })
    return Response(response=response, status=200)

@app.route('/addItemsToCart', methods=['POST'])
def add_items_to_cart():
    data = json.loads(request.data)
    sql = f"SELECT rowid, * FROM products WHERE rowid = {data['item_id']}"

    try:
        db_response = query_database(sql, 'product')
    except:
        response = json.dumps({'status': 'Error: Failed to connect to database'})
        return Response(response=response, status=500)
    else:
        if isinstance(db_response, dict):
            return Response(response=db_response, status=500)

    # Check if that item isn't in the DB
    if not db_response:
        response = json.dumps({'status': 'Error: This item is not in inventory'})
        return Response(response=response, status=400)
    
    items = products_query_to_json(db_response)[0]

    # Check if the user is requesting more than is available
    if (data['quantity']) > items['quantity']:
        response = json.dumps({'status': 'Error: You requested more items than are in our inventory'})
        return Response(response=response, status=400)
    else:
        items['quantity'] = data['quantity']

    # Good request, return items
    response = json.dumps({
        'status': 'Success: Items queried successfully',
        'items': items
    })
    return Response(response=response, status=200)

@app.route('/getSellerRatingByID/<string:seller_id>', methods=['GET'])
def get_seller_rating_by_id(seller_id):
    sql = f"SELECT rowid, * from sellers WHERE rowid = {seller_id}"
    try:
        db_response = query_database(sql, 'customer')
    except:
        response = json.dumps({'status': 'Error: Failed to connect to database'})
        return Response(response=response, status=500)
    else:
        if isinstance(db_response, dict):
            return Response(response=db_response, status=500)

    if not db_response:
        response = json.dumps({'status': 'Error: The user you are trying to find does not exist'})
        return Response(response=response, status=400)
    
    thumbs_up, thumbs_down = db_response[0][3], db_response[0][4]
    response = json.dumps({
        'status': 'Success: Seller queried without error',
        'thumbs_up': thumbs_up,
        'thumbs_down': thumbs_down
    })
    return Response(response=response, status=200)

# @app.route('/makePurchase', methods=['POST'])
# def 

def products_query_to_json(db_response):
    items = []
    for db_item in db_response:
        item = {
            'id': db_item[0],
            'name': db_item[1],
            'category': db_item[2],
            'keywords': db_item[3].split(','),
            'condition': db_item[4],
            'price': db_item[5],
            'quantity': db_item[6],
            'seller': db_item[7],
            'status': db_item[8],
        }
        items.append(item)

    return items

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