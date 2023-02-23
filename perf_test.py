import concurrent.futures
from seller_client import SellerClient
from buyer_client import BuyerClient

n_client_pairs = 10
time_between_requests = 0.05

clients = [SellerClient(debug=False) for _ in range(n_client_pairs)] + \
          [BuyerClient(debug=False) for _ in range(n_client_pairs)]
response_times = []

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [executor.submit(client.test, time_between_requests) for client in clients]

    for f in concurrent.futures.as_completed(results):
        response_times.append(f.result())

print("Average response time: ", sum(response_times)/len(response_times))
