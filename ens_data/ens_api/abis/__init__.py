import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent

with open(base_dir / 'public_resolver_abi.json') as _f:
    public_resolver_abi = json.loads(_f.read())

with open(base_dir / 'ens_registry.json') as _f:
    ens_registry_abi = json.loads(_f.read())
