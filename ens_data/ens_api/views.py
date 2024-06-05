import asyncio
import os

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from web3 import Web3
from ens import ENS

from dotenv import load_dotenv
from ens_normalize import ens_normalize
from web3.contract import Contract

from .namehash import namehash
from . import abis
from .resolver import Resolver

load_dotenv()  # take environment variables from .env.

w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
ns = ENS.from_web3(w3)
assert w3.is_connected() is True

registry_contract = w3.eth.contract(os.getenv("ENS_CONTRACT"), abi=abis.ens_registry_abi)
NULL_NODE = "0x0000000000000000000000000000000000000000000000000000000000000000"


def get_ens_node(domain: str) -> bytes:
    return namehash(ens_normalize(domain))


def find_resolver(node: bytes) -> Resolver:
    resolver_address = registry_contract.functions.resolver(node).call()
    resolver = Resolver(resolver_address, w3)

    return resolver


@api_view(['GET'])
def resolve_ens(request, address_or_domain: str):
    reversed = False
    raw_ens_node = address_or_domain
    if w3.is_address(address_or_domain):
        raw_ens_node = address_or_domain[2:] + ".addr.reverse"
        reversed = True
    elif not address_or_domain.endswith(".eth"):
        raw_ens_node += ".eth"

    ens_node = get_ens_node(raw_ens_node)
    # print("0x" + ens_node.hex(), raw_ens_node)

    resolver = find_resolver(ens_node)

    if reversed:
        domain = resolver.resolve_name(ens_node)
        address = w3.to_checksum_address(address_or_domain)
    else:
        address = resolver.resolve_addr(ens_node)
        domain = address_or_domain

    records = resolver.get_all_records(ens_node)

    return Response({"ens": domain, "address": address, **records})
