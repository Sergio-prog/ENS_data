import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from ens_normalize import ens_normalize
from eth_utils import to_checksum_address
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput

from ens_api import abis
from ens_api.namehash import namehash
from ens_api.utils.client import evm_client, registry_contract
from ens_api.utils.errors import ResolutionFailed, WrongResolverUsed

NULL_NODE = "0x0000000000000000000000000000000000000000000000000000000000000000"


class EstimateTime:
    def __init__(self):
        self.time = None

    def __enter__(self):
        self.time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Time wasted:", time.time() - self.time)


class Resolver:
    def __init__(self, address: str, client: Web3):
        self._resolver = client.eth.contract(to_checksum_address(address), abi=abis.public_resolver_abi)
        self.address = address

    def resolve_name(self, node: bytes):
        try:
            return self._resolver.functions.name(node).call()
        except BadFunctionCallOutput:
            raise ResolutionFailed()

    def resolve_addr(self, node: bytes):
        try:
            return self._resolver.functions.addr(node).call()
        except BadFunctionCallOutput:
            raise ResolutionFailed()

    def text_record(self, node: bytes, text: str):
        try:
            return self._resolver.functions.text(node, text).call()
        except BadFunctionCallOutput:
            raise WrongResolverUsed()

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
            "com.github": "github",
        }

        result = {}
        # tasks = []
        # for record in records.items():
        #     result[record[1]] = self.text_record(node, record[0])
        #     # tasks.append(self.text_record(node, record[0])
        #
        # return result

        # tasks = {key: loop.run_in_executor(None, self.text_record, node, key) for key in records.keys()}
        # results = await asyncio.gather(*tasks.values())
        # return dict(zip(records.values(), results))

        with ThreadPoolExecutor() as executor:
            # TODO: Maybe create two lists instead of dict with fututres as keys??
            future_to_record = {executor.submit(self.text_record, node, key): value for key, value in records.items()}

            for future in as_completed(future_to_record):
                record_name = future_to_record[future]
                text_record = future.result()
                if text_record:
                    result[record_name] = text_record

        return result


class EnsUtils:
    @staticmethod
    def get_ens_node(domain: str) -> bytes:
        return namehash(ens_normalize(domain))

    @staticmethod
    def find_resolver(node: bytes) -> Resolver:
        if not isinstance(node, bytes) or len(node) != 32:
            raise TypeError("Invalid type")

        with EstimateTime():
            resolver_address = registry_contract.functions.resolver(node).call()
            resolver = Resolver(resolver_address, evm_client)

        return resolver
