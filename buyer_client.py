import requests
import json
import time
import random
import pprint

pp = pprint.PrettyPrinter()

class BuyerClient:

    def __init__(self, server_ip : str = '0.0.0.0:5001', debug : bool = True):
        self.username = ""
        self.cart = []
        self.debug = debug
        self.base_url = 'http://' + server_ip
        self.headers = {'content-type': 'application/json'}

        self.routes = {
            'create account': self.create_account,
            'login': self.login,
            'logout': self.logout,
            'search items': self.search,
            'add items to cart': self.add_items_to_cart,
            'remove item from cart': self.remove_item_from_cart,
            'clear cart': self.clear_cart,
            'display cart': self.display_cart,
            'make purchase': self.make_purchase,
            # 'provide feedback': self.provide_feedback,
            'get seller rating': self.get_seller_rating_by_id,
            # 'get purchase history': self.get_purchase_history,
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

    def search(self):
        """
        Results in the specified category or matching
        any of the keywords get returned.
        """
        if self.debug:
            print("Please provide the following information.")
            category = int(input("\nCategory (0-9): "))
            keywords = input("Keywords: ").split(',')
        
        data = json.dumps({
            'category': category,
            'keywords': keywords
        })
        url = self.base_url + '/search'
        response = requests.post(url, headers=self.headers, data=data)
        response_text = json.loads(response.text)

        if 'Error' in response_text['status']:
            print('\n', response_text['status'])
        elif not response_text['items']:
            print("\nYour search did not return any results.")
        else:
            for item in response_text['items']:
                print("")
                pp.pprint(item)

    def add_items_to_cart(self):
        if not self.check_if_logged_in():
            print("\nYou must log in before adding items to your cart.")
        else:
            item_id = int(input("\nID for the item you wish to add to your cart: "))
            quantity = int(input("Number of this item you wish to add to your cart: "))
            data = json.dumps({
                'item_id': item_id,
                'quantity': quantity
            })
            url = self.base_url + '/addItemsToCart'
            response = requests.post(url, headers=self.headers, data=data)
            response_text = json.loads(response.text)

            if 'Error' in response_text['status']:
                # No such item, not enough, etc.
                print('\n', response_text['status'])
            else:
                self.cart.append(response_text['items'])
                print("\nThe items have been added to your cart")

    def remove_item_from_cart(self):
        item_id = int(input("\nID for the item you wish to remove from your cart: "))
        quantity = int(input("Number of this item you wish to remove from your cart: "))

        # Find that item in the cart
        item_to_remove = None
        for item in self.cart:
            if item['id'] == item_id:
                item_to_remove = item
                break

        if item_to_remove == None:
            print("\nThe item specified is not in your cart")
        elif item_to_remove['quantity'] < quantity:
            print("\nYou have requested to remove more items than are in your cart")
        elif item_to_remove['quantity'] == quantity:
            self.cart.remove(item_to_remove)
            print("\nThe item has been deleted from your cart")
        else:
            item_to_remove['quantity'] -= quantity
            print(f"\n{quantity} of the specified item have been removed")

    def clear_cart(self):
        self.cart = []
        print("\nYour cart has been cleared.")

    def display_cart(self):
        if not self.cart:
            print("\nYour cart is empty.")
        else:
            for item in self.cart:
                print("")
                pp.pprint(item)

    def get_seller_rating_by_id(self):
        if self.debug:
            # Get seller ID from user
            seller_id = input("\nPlease provide the ID for the seller whose rating you wish to view.\n")

        url = self.base_url + '/getSellerRatingByID/' + seller_id
        response = requests.get(url)
        response_text = json.loads(response.text)

        if 'Error' in response_text['status']:
            print('\n', response_text['status'])
        else:
            tu, td = response_text['thumbs_up'], response_text['thumbs_down']
            print(f"\nSeller with ID {seller_id} has {tu} thumbs up and {td} thumbs down")

    def make_purchase(self):
        if not self.check_if_logged_in():
            print("\nYou must log in to make a purchase.")
            return None

        if not self.cart:
            print("\nPlease add items to your cart before attempting to make a purchase.")
            return None

        if self.debug:
            print("\nWe need the following payment information:")
            cc_name = input("Name on payment card: ")
            cc_number = input("Card number: ")
            cc_exp = input("Card expiration date: ")

        data = json.dumps({
            'cc_name': cc_name,
            'cc_number': cc_number,
            'cc_exp': cc_exp,
            'username': self.username,
            'items': [(item['id'], item['quantity'])
                        for item in self.cart]
        })
        url = self.base_url + '/makePurchase'
        response = requests.post(url, headers=self.headers, data=data)
        response_text = json.loads(response.text)

        print("\n", response_text['status'])
        if 'Error' not in response_text['status']:
            self.clear_cart()

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
    buyer = BuyerClient()
    buyer.serve()