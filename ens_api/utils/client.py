import os

from web3 import Web3

from ens_api import abis

evm_client = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
# ns = ENS.from_web3(evm_client)
assert evm_client.is_connected() is True

registry_contract = evm_client.eth.contract(os.getenv("ENS_CONTRACT"), abi=abis.ens_registry_abi)
