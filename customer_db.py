# gRPC-related dependencies
import grpc
import database_pb2_grpc
import database_pb2

# Other dependencies
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import pickle

class databaseServicer(database_pb2_grpc.databaseServicer):

    def __init__(self):
        """
        Reinitializes the tables, creates the cursor
        and connection objects.
        """
        with sqlite3.connect('customers.db') as con:
            cur = con.cursor()

            # Create sellers table
            cur.execute("DROP TABLE IF EXISTS sellers")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sellers (
                username TEXT NOT NULL, 
                password TEXT NOT NULL, 
                thumbs_up INTEGER DEFAULT 0, 
                thumbs_down INTEGER DEFAULT 0, 
                items_sold INTEGER DEFAULT 0
                )
            """)

            # Create buyers table
            cur.execute("DROP TABLE IF EXISTS buyers")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS buyers (
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                items_purchased INTEGER DEFAULT 0
                )
            """)

    def queryDatabase(self, request, context):
        """
        Implements the gRPC route for querying the database. All
        other operations go through updateDatabase.
        """
        print(request.query)
        with sqlite3.connect('customers.db') as con:
            try:
                cur = con.cursor()
                db_resp = cur.execute(request.query)
                serv_resp = pickle.dumps(db_resp.fetchall())
            except:
                serv_resp = pickle.dumps({'status': 'Error: Bad query or unable to connect'})
            finally:
                return database_pb2.databaseResponse(db_response=serv_resp)

    def changeDatabase(self, request, context):
        """
        Implements gRPC route that deals with making changes to the 
        database such as creating, updating, or deleting records.
        """
        print(request.query)
        with sqlite3.connect('customers.db') as con:
            try:
                cur = con.cursor()
                cur.execute(request.query)
                con.commit()
                serv_resp = pickle.dumps({'status': 'success'})
            except:
                serv_resp = pickle.dumps({'status': 'Error: Bad query or unable to connect'})
            finally:
                return database_pb2.databaseResponse(db_response=serv_resp)
        


if __name__ == "__main__":
    # Start the server
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    database_pb2_grpc.add_databaseServicer_to_server(databaseServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()