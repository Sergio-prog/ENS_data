from django.core.cache import cache
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ens_api.utils.client import evm_client
from ens_api.utils.ens import EnsUtils
from ens_api.utils.errors import ResolutionFailed

load_dotenv()  # take environment variables from .env.


class ResolveEns(APIView):
    def get(self, request, address_or_domain: str):
        reversed = False
        raw_ens_node = address_or_domain
        if evm_client.is_address(address_or_domain):
            raw_ens_node = address_or_domain[2:] + ".addr.reverse"
            reversed = True
        elif not address_or_domain.endswith(".eth"):
            raw_ens_node += ".eth"
        # else:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        ens_node = EnsUtils.get_ens_node(raw_ens_node)
        is_disabled_cache = request.headers.get("Cache-Control") == "no-cache"

        if not is_disabled_cache:
            cached_data = cache.get(ens_node)
            if cached_data:
                return Response(cached_data)

        resolver = EnsUtils.find_resolver(ens_node)

        try:
            if reversed:
                domain = resolver.resolve_name(ens_node)
                address = evm_client.to_checksum_address(address_or_domain)
                ens_node = EnsUtils.get_ens_node(domain)
                resolver = EnsUtils.find_resolver(
                    ens_node
                )  # This line added is because ReverseResolver doesn't have a text record function
            else:
                address = resolver.resolve_addr(ens_node)
                domain = address_or_domain

        except ResolutionFailed:
            return Response(
                {"message": "Resolve of domain/address failed. Resolution not found"}, status=status.HTTP_404_NOT_FOUND
            )

        records = resolver.get_all_records(ens_node)
        resolved_data = {"ens": domain, "address": address, "records": records}

        if not is_disabled_cache:
            cache.set(ens_node, resolved_data, timeout=300)

        return Response(resolved_data)
