import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from web3 import Web3
from web3.utils.address import to_checksum_address

from . import abis


class Resolver:
    def __init__(self, address: str, client: Web3):
        self._resolver = client.eth.contract(to_checksum_address(address), abi=abis.public_resolver_abi)

    def resolve_name(self, node: bytes):
        return self._resolver.functions.name(node).call()

    def resolve_addr(self, node: bytes):
        return self._resolver.functions.addr(node).call()

    def text_record(self, node: bytes, text: str):
        return self._resolver.functions.text(node, text).call()

    def get_all_records(self, node: bytes):
        records = {
            "avatar": "avatar",
            "description": "description",
            "email": "email",
            "keywords": "keywords",
            "mail": "mail",
            "notice": "notice",
            "location": "location",
            "phone": "phone",
            "url": "url",
            "com.github": "github"
        }

        # result = {}
        # tasks = []
        # for record in records.items():
        #     result[record[1]] = self.text_record(node, record[0])
        #     # tasks.append(self.text_record(node, record[0])
        #
        # return result

        # tasks = {key: loop.run_in_executor(None, self.text_record, node, key) for key in records.keys()}
        # results = await asyncio.gather(*tasks.values())
        # return dict(zip(records.values(), results))
        result = {}

        with ThreadPoolExecutor() as executor:
            future_to_record = {executor.submit(self.text_record, node, key): value for key, value in records.items()}

            for future in as_completed(future_to_record):
                record_name = future_to_record[future]
                text_record = future.result()
                if text_record:
                    result[record_name] = text_record

        print(result, type(result))

        return result
