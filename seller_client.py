import requests
import json
import time
import random


class SellerClient:

    def __init__(self, server_ip : str = '0.0.0.0:5000', debug : bool = True):
        self.is_logged_in = False
        self.username = ""
        self.debug = debug
        self.base_url = 'http://' + server_ip
        self.headers = {'content-type': 'application/json'}

        self.routes = {
            'create account': self.create_account,
            'login': self.login,
            # 'logout': self.logout,
            # 'get seller rating': self.get_seller_rating,
            # 'sell item': self.sell_item,
            # 'remove item': self.remove_item,
            # 'list item': self.list_items,
            'exit': None # handled differently due to different args
        }

    def create_account(self):
         # User cannot create account if logged in
        if self.is_logged_in:
            print("You are already logged in. You cannot create an account.\n")
        else:
            if self.debug == True:
                # Get user input
                print("Please provide a username and password.")
                username = input("\nusername: ")
                password = input("password: ")
            else:
                pass
                # username, password = self.benchmarker.get_username_and_password()

            data = json.dumps({
                'username': username,
                'password': password
            })

            # Call the handler to send request and receive response
            # start = time.time()
            url = self.base_url + '/createAccount'
            response = requests.post(url, headers=self.headers, data=data)
            # end = time.time()

            if not self.debug:
                pass
                # self.benchmarker.log_response_time(end-start)

            print('\n', json.loads(response.text)['status'])

    def login(self):
        """
        Change the local state to reflect that the user
        is logged in.
        """
        if self.is_logged_in:
            print("You are already logged in.")
        else:
            if self.debug:
                # Get the username and password
                print("\nPlease provide a username and password.")
                username = input("\nusername: ")
                password = input("password: ")
            else:
                # Login with any account that's already been created
                # username, password = random.choice(self.benchmarker.accounts)
                pass

            data = json.dumps({
                'username': username,
                'password': password
            })

            # Send request to the seller server
            # start = time.time()
            url = self.base_url + '/login'
            response = requests.post(url, headers=self.headers, data=data)
            # end = time.time()

            # if not self.debug:
            #     self.benchmarker.log_response_time(end-start)

            response_text = json.loads(response.text)
            if 'Success' in response_text['status']:
                self.is_logged_in = True
                self.username = data['username']
            
            print('\n', response_text['status'])

    def logout(self):
        self.is_logged_in = False
        self.username = ""
        print("\nYou are now logged out.")

    def _get_route(self, route: str):
        return self.routes[route]

    def serve(self):
        """
        Runs the server either in an interactive mode for debugging
        or an automated mode for performance testing.
        """
        if self.debug:
            # Run in interactive terminal mode
            while True:
                # Get user input
                actions = list(self.routes.keys())
                action = input(f"\nWhat would you like to do?\n{actions}\n")

                # Check that action is valid
                if action not in actions:
                    print("\nUnknown action. Please select another.\n")
                    continue

                # Execute the action specified
                if action == 'exit':
                    exit()

                self.routes[action]()
        else:
            exit()
            # # Calls functions in a predetermined order
            # self.create_account()
            # time.sleep(0.5)
            # self.login()
            # time.sleep(0.5)
            # for _ in range(600):
            #     self.sell_item()
            #     time.sleep(0.5)
            # for _ in range(300):
            #     self.remove_item()
            #     time.sleep(0.5)
            # for _ in range(98):
            #     self.list_items()
            #     time.sleep(0.5)

            # # Print average response time
            # avg_response_time = self.benchmarker.compute_average_response_time()
            # print("#######################################")
            # print(f"Seller average response time: {avg_response_time}")
            # print("***************************************")

            # with open('art_dump.txt', 'a') as f:
            #     f.write(str(avg_response_time) + '\n')


if __name__ == "__main__":
    seller = SellerClient()
    seller.serve()

    base_url = 'http://0.0.0.0:5000'
    headers = {'content-type': 'application/json'}

    url = base_url + '/createAccount'
    data = json.dumps({
        'username': 'john',
        'password': 'purple'
    })
    response = requests.post(url, headers=headers, data=data)
    print(json.loads(response.text))