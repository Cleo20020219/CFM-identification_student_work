"""Program-owned short source aliases, shared by fact-reading contracts."""
from copy import deepcopy
from hashlib import sha256
import json
from cfm_id.source_locations import build_catalog


def catalog(bundle, documents, *, binding, version):
    if type(binding) is not str or not binding:
        raise ValueError('QUERY_REFERENCE_BINDING_REQUIRED')
    original = build_catalog(documents)
    if len(original) > 9999:
        raise ValueError('QUERY_SOURCE_CATALOG_LIMIT')
    payload = dict(version=version, bundle=bundle, binding=binding, catalog=original)
    digest = sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode('utf8')).hexdigest()
    return dict(context='c'+digest[:12], context_sha256=digest,
                aliases={f's{i:04d}':row for i,row in enumerate(original.values(),1)})


def expand(value, references):
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            if key.endswith('source_ids'):
                if len(set(child)) != len(child) or any(x not in references['aliases'] for x in child):
                    raise ValueError('UNKNOWN_OR_DUPLICATE_SHORT_SOURCE')
                out[key] = [references['aliases'][x]['source_id'] for x in child]
            else:
                out[key] = expand(child, references)
        return out
    if isinstance(value, list):
        return [expand(v,references) for v in value]
    return deepcopy(value)
