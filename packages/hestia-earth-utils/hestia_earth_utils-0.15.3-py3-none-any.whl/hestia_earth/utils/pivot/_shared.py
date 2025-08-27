import json
import numpy as np


EXCLUDE_FIELDS = ["@type", "type", "@context"]
EXCLUDE_PRIVATE_FIELDS = ["added", "addedVersion", "updated", "updatedVersion", "_cache"]


def _with_csv_formatting(dct):
    """
    Use as object_hook when parsing a JSON node: json.loads(node, object_hook=_with_csv_formatting).
    Ensures parsed JSON has field values formatted according to hestia csv conventions.
    """
    if 'boundary' in dct:
        dct['boundary'] = json.dumps(dct['boundary'])
    for key, value in dct.items():
        if _is_scalar_list(value):
            dct[key] = ';'.join([str(el) for el in value])
    return dct


def _is_scalar_list(value):
    if not isinstance(value, list):
        return False
    all_scalar = True
    for element in value:
        if not np.isscalar(element):
            all_scalar = False
            break
    return all_scalar
