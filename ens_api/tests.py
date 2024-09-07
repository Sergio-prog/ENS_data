import pytest
from django.test import Client, TestCase

from ens_api.namehash import namehash
from ens_api.utils.ens import EnsUtils
from ens_api.utils.errors import ResolutionFailed, WrongResolverUsed


@pytest.mark.parametrize(
    "name,expected_namehash",
    [
        ("", bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000")),
        ("ens.eth", bytes.fromhex("4e34d3a81dc3a20f71bbdf2160492ddaa17ee7e5523757d47153379c13cb46df")),
        ("vitalik.eth", bytes.fromhex("ee6c4522aab0003e8d14cd40a6af439055fd2577951148c14b6cea9a53475835")),
        (
            "481f50a5bdccc0bc4322c4dca04301433ded50f0.addr.reverse",
            bytes.fromhex("58354ffdde6ac279f3a058aafbeeb14059bcb323a248fb338ee41f95fa544c86"),
        ),
    ],
)
def test_namehash(name, expected_namehash):
    assert namehash(name) == expected_namehash


@pytest.mark.parametrize(
    "name,expected_node",
    [
        ("ens.eth", bytes.fromhex("4e34d3a81dc3a20f71bbdf2160492ddaa17ee7e5523757d47153379c13cb46df")),
        ("vitalik.eth", bytes.fromhex("ee6c4522aab0003e8d14cd40a6af439055fd2577951148c14b6cea9a53475835")),
        (
            "481f50a5bdccc0bc4322c4dca04301433ded50f0.addr.reverse",
            bytes.fromhex("58354ffdde6ac279f3a058aafbeeb14059bcb323a248fb338ee41f95fa544c86"),
        ),
    ],
)
def test_ens_node(name, expected_node):
    assert EnsUtils.get_ens_node(name) == expected_node


@pytest.mark.parametrize(
    "node,expected_resolver",
    [
        (
            bytes.fromhex("ee6c4522aab0003e8d14cd40a6af439055fd2577951148c14b6cea9a53475835"),
            "0x231b0Ee14048e9dCcD1d247744d114a4EB5E8E63",
        ),
        (
            bytes.fromhex("58354ffdde6ac279f3a058aafbeeb14059bcb323a248fb338ee41f95fa544c86"),
            "0xA2C122BE93b0074270ebeE7f6b7292C7deB45047",
        ),
    ],
)
def test_find_resolver(node, expected_resolver):
    assert EnsUtils.find_resolver(node).address == expected_resolver


def test_normalize_node():
    assert EnsUtils.get_ens_node("ens.eth") == EnsUtils.get_ens_node("EnS.ETh")


def test_resolver():
    domain = "vitalik.eth"
    node = EnsUtils.get_ens_node(domain)

    resolver = EnsUtils.find_resolver(node)
    addr = resolver.resolve_addr(node)
    assert addr == "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    assert resolver.text_record(node, "url") == "https://vitalik.ca"

    addr_reverse = addr[2:] + ".addr.reverse"
    reverse_node = EnsUtils.get_ens_node(addr_reverse)
    reverse_resolver = EnsUtils.find_resolver(reverse_node)

    assert reverse_resolver.resolve_name(reverse_node) == domain


def test_address_without_domain_in_resolver():
    reverse_address = "fe89cc7abb2c4183683ab71653c4cdc9b02d44b7.addr.reverse"
    reverse_node = EnsUtils.get_ens_node(reverse_address)
    reverse_resolver = EnsUtils.find_resolver(reverse_node)
    with pytest.raises(ResolutionFailed):
        reverse_resolver.resolve_name(reverse_node)


def test_resolve_domain_endpoint(client: Client):
    domain = "ens.eth"
    response = client.get(f"/api/resolve/{domain}/")
    assert response.status_code == 200
    response_body = response.json()

    assert response_body["address"] == "0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7"
    assert response_body["ens"] == "ens.eth"
    assert response_body["records"]["url"] == "https://ens.domains/"
    assert response_body["records"]["github"] == "ensdomains"


def test_resolve_address_endpoint(client: Client):
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    response = client.get(f"/api/resolve/{address}/")
    assert response.status_code == 200
    response_body = response.json()

    assert response_body["address"] == "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    assert response_body["ens"] == "vitalik.eth"
    assert response_body["records"]["url"] == "https://vitalik.ca"


# TODO: Crate tests for get_all_records and text_record
def test_get_text_record():
    domain = "vitalik.eth"
    node = EnsUtils.get_ens_node(domain)
    resolver = EnsUtils.find_resolver(node)
    assert resolver.text_record(node, "url") == "https://vitalik.ca"


def test_get_text_record_with_wrong_resolver():
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    node = EnsUtils.get_ens_node(address)
    resolver = EnsUtils.find_resolver(node)

    with pytest.raises(WrongResolverUsed):
        resolver.text_record(node, "url")
