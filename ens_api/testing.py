import time

import requests


class EstimateTime:
    def __init__(self):
        self.time = None

    def __enter__(self):
        self.time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Time wasted:", time.time() - self.time)


data = {
    "jsonrpc": "2.0",
    "method": "eth_call",
    "params": [
        {
            "to": "0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e",
            "data": "0x0178b8bfe1e7bcf2ca33c28a806ee265cfedf02fedf1b124ca73b2203ca80cc7c91a02ad",
        },
        "latest",
    ],
    "id": 1,
}

url = "https://eth.llamarpc.com"


with EstimateTime():
    start = time.perf_counter()
    print(requests.post(url=url, json=data).json())
    print(time.perf_counter() - start)
