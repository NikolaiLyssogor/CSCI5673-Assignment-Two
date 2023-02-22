import requests
import json
import time
import random
import pprint

pp = pprint.PrettyPrinter()

class SellerClient:

    def __init__(self, server_ip : str = '0.0.0.0:5000', debug : bool = True):
        self.username = ""
        self.debug = debug
        self.base_url = 'http://' + server_ip
        self.headers = {'content-type': 'application/json'}

        self.routes = {
            'create account': self.create_account,
            'login': self.login,
            'logout': self.logout,
            'get seller rating': self.get_seller_rating,
            'sell item': self.sell_item,
            'remove item': self.remove_item,
            'change item price': self.change_item_price,
            'list item': self.list_items,
            'exit': None # handled differently due to different args
        }

    def create_account(self):
         # User cannot create account if logged in
        if self.check_if_logged_in():
            print("\nYou are already logged in. You cannot create an account.\n")
        else:
            if self.debug:
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
        if self.check_if_logged_in():
            print("\nYou are already logged in.")
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
                self.username = username
            
            print('\n', response_text['status'])

    def logout(self):
        if self.username:
            data = json.dumps({'username': self.username})
            url = self.base_url + '/logout'
            response = requests.post(url, headers=self.headers, data=data)
            response_text = json.loads(response.text)

            print('\n', response_text['status'])
            if 'Success' in response_text['status']:
                self.username = ""

    def check_if_logged_in(self) -> bool:
        """
        Calls the server to check if the user is logged in.
        """
        data = json.dumps({'username': self.username})
        url = self.base_url + '/checkIfLoggedIn'
        response = requests.post(url, headers=self.headers, data=data)
        response_text = json.loads(response.text)
        return response_text['is_logged_in']

    def get_seller_rating(self):
        if not self.check_if_logged_in():
            print("\nYou must be logged in to check your rating")
            return None

        url = self.base_url + f'/getSellerRating/{self.username}'
        response = requests.get(url)
        response_text = json.loads(response.text)

        if 'Error' in response_text['status']:
                print("\n", response_text['status']),
        else:
            print(f"\nYou have {response_text['thumbs_up']} thumbs up and {response_text['thumbs_down']} thumbs down.")

    def sell_item(self):
        """
        Gather the attributes needed to list an item
        for sale.
        """
        if not self.check_if_logged_in():
            print("\nYou must be logged in to sell an item.")
        else:
            if self.debug:
                name = input("\nItem name: ")
                category = int(input("Item category: "))
                keywords = input("Item keywords: ")
                condition = input("Item condition: ")
                price = float(input("Item price: "))
                quantity = int(input("Item quantity: "))

                item = {
                    'name': name,
                    'category': category,
                    'keywords': keywords,
                    'condition': condition,
                    'price': round(price, 2),
                    'quantity': quantity,
                    'seller': self.username,
                    'status': 'For Sale',
                    'buyer': None
                }
            # else:
            #     item = {
            #         'name': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            #         'category': random.choice(range(10)),
            #         'keywords': self.benchmarker.get_keywords(),
            #         'condition': random.choice(['New', 'Used']),
            #         'price': round(random.uniform(0, 100), 2),
            #         'quantity': random.choice(range(1,6)),
            #         'seller': self.username,
            #         'status': 'For Sale',
            #         'buyer': None
            #     }

            data = json.dumps(item)
            url = self.base_url + '/sellItem'
            response = requests.post(url, data=data, headers=self.headers)
            response_text = json.loads(response.text)
            print('\n', response_text['status'])

    def list_items(self):
        if not self.check_if_logged_in():
            print("\nYou must be logged in to sell an item.")
        else:
            url = self.base_url + f'/listItems/{self.username}'
            response = requests.get(url)
            response_text = json.loads(response.text)

            if 'Error' in response_text['status']:
                print(response_text['status'])
            else:
                for item in response_text['items']:
                    pp.pprint(item)

    def remove_item(self):
        if not self.check_if_logged_in():
            print("\nPlease log in first.")
        else:
            if self.debug:
                id = int(input("\nEnter the ID of the item you would like to remove: "))
                quantity = input("How many of this item do you want to remove? ")
            else:
                # Randomly remove 2 items with ids in [0, 500]
                # ids = [random.choice(range(500)) for _ in range(2)]
                pass

            data = json.dumps({
                'username': self.username,
                'item_id': id,
                'quantity': int(quantity)
            })
            url = self.base_url + '/deleteItem'
            response = requests.put(url, headers=self.headers, data=data)
            response_text = json.loads(response.text)
            print('\n', response_text['status'])

    def change_item_price(self):
        if not self.check_if_logged_in():
            print("\nPlease log in first.")
        else:
            if self.debug:
                id = int(input("\nEnter the ID of the item whose price you wish to change: "))
                new_price = input("What shall be the new price? ")
            else:
                # Randomly remove 2 items with ids in [0, 500]
                # ids = [random.choice(range(500)) for _ in range(2)]
                pass

            data = json.dumps({
                'username': self.username,
                'item_id': id,
                'new_price': round(float(new_price), 2)
            })
            url = self.base_url + '/changeItemPrice'
            response = requests.put(url, headers=self.headers, data=data)
            response_text = json.loads(response.text)
            print('\n', response_text['status'])

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
                try:
                    # Get user input
                    actions = list(self.routes.keys())

                    # if not self.username:
                    #     actions.remove('logout')
                    # else:
                    #     actions.remove('login')

                    action = input(f"\nWhat would you like to do?\n{actions}\n")

                    # Check that action is valid
                    if action not in actions:
                        print("\nUnknown action. Please select another.\n")
                        continue

                    # Execute the action specified
                    if action == 'exit':
                        self.logout()
                        exit(130)

                    self.routes[action]()
                except KeyboardInterrupt:
                        # Logout then actually exit
                        self.logout()
                        exit(130)
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