from functools import lru_cache
import json

from .lookup import _download_lookup_data, download_lookup, get_table_value, column_name
from .api import download_hestia
from .tools import non_empty_list

_ALLOW_ALL = 'all'


@lru_cache()
def _allowed_mapping_data():
    data = _download_lookup_data('allowed-mapping.json')
    data = json.loads(data) if data else {}
    return data


def _is_site(site: dict):
    return site.get('@type', site.get('type')) == 'Site' if site else None


def _get_sites(node: dict):
    site = node.get('site', node.get('cycle', {}).get('site'))
    other_sites = node.get('otherSites', node.get('cycle', {}).get('otherSites', []))
    return non_empty_list([site] + other_sites)


def _get_site_types(node: dict):
    sites = [node] if _is_site(node) else _get_sites(node)
    return non_empty_list([site.get('siteType') for site in sites])


@lru_cache()
def _allowed_model_mapping(model: str, term_id: str, column: str):
    mapping = _allowed_mapping_data()
    value = mapping.get(term_id, {}).get(model, {}).get(column) if mapping else get_table_value(
        download_lookup(f"{(download_hestia(term_id) or {}).get('termType')}-model-{column}.csv"),
        'termid', term_id, column_name(column)
    )
    return (value or _ALLOW_ALL).split(';') if isinstance(value, str) else _ALLOW_ALL


def is_model_siteType_allowed(model: str, term_id: str, data: dict):
    site_types = _get_site_types(data)
    allowed_values = _allowed_model_mapping(model, term_id, 'siteTypesAllowed')
    return True if _ALLOW_ALL in allowed_values or not site_types else any([
        (site_type in allowed_values) for site_type in site_types
    ])


def is_model_product_id_allowed(model: str, term_id: str, data: dict):
    products = data.get('products', [])
    values = non_empty_list([p.get('term', {}).get('@id') for p in products])
    allowed_values = _allowed_model_mapping(model, term_id, 'productTermIdsAllowed')
    return True if any([
        _ALLOW_ALL in allowed_values,
        len(values) == 0
    ]) else any([value in allowed_values for value in values])


@lru_cache()
def _allowed_mapping(term_id: str, column: str):
    mapping = _allowed_mapping_data()
    value = mapping.get(term_id, {}).get(column) if mapping else get_table_value(
        download_lookup(f"{(download_hestia(term_id) or {}).get('termType')}.csv"),
        'termid', term_id, column_name(column)
    )
    return (value or _ALLOW_ALL).split(';') if isinstance(value, str) else _ALLOW_ALL


def is_siteType_allowed(data: dict, term_id: str):
    site_types = _get_site_types(data)
    allowed_values = _allowed_mapping(term_id, 'siteTypesAllowed')
    return True if _ALLOW_ALL in allowed_values or not site_types else any([
        (site_type in allowed_values) for site_type in site_types
    ])


def is_product_termType_allowed(data: dict, term_id: str):
    products = data.get('products', [])
    values = non_empty_list([p.get('term', {}).get('termType') for p in products])
    allowed_values = _allowed_mapping(term_id, 'productTermTypesAllowed')
    return True if any([
        _ALLOW_ALL in allowed_values,
        len(values) == 0
    ]) else any([value in allowed_values for value in values])


def is_product_id_allowed(data: dict, term_id: str):
    products = data.get('products', [])
    values = non_empty_list([p.get('term', {}).get('@id') for p in products])
    allowed_values = _allowed_mapping(term_id, 'productTermIdsAllowed')
    return True if any([
        _ALLOW_ALL in allowed_values,
        len(values) == 0
    ]) else any([value in allowed_values for value in values])


def is_input_termType_allowed(data: dict, term_id: str):
    inputs = data.get('inputs', [])
    values = non_empty_list([p.get('term', {}).get('termType') for p in inputs])
    allowed_values = _allowed_mapping(term_id, 'inputTermTypesAllowed')
    return True if any([
        _ALLOW_ALL in allowed_values,
        len(values) == 0
    ]) else any([value in allowed_values for value in values])


def is_input_id_allowed(data: dict, term_id: str):
    inputs = data.get('inputs', [])
    values = non_empty_list([p.get('term', {}).get('@id') for p in inputs])
    allowed_values = _allowed_mapping(term_id, 'inputTermIdsAllowed')
    return True if any([
        _ALLOW_ALL in allowed_values,
        len(values) == 0
    ]) else any([value in allowed_values for value in values])


def is_node_type_allowed(data: dict, term_id: str):
    node_type = data.get('@type', data.get('type'))
    allowed_types = _allowed_mapping(term_id, 'typesAllowed')
    return True if _ALLOW_ALL in allowed_types or not node_type else node_type in allowed_types


@lru_cache()
def is_in_system_boundary(term_id: str) -> bool:
    """
    Check if the term is included in the HESTIA system boundary.

    Parameters
    ----------
    term_id : str
        The term ID

    Returns
    -------
    bool
        True if the Term is included in the HESTIA system boundary, False otherwise.
    """
    mapping = _allowed_mapping_data()
    column = 'inHestiaDefaultSystemBoundary'
    value = mapping.get(term_id, {}).get(column) if mapping else get_table_value(
        download_lookup(f"{(download_hestia(term_id) or {}).get('termType')}.csv"),
        'termid', term_id, column_name(column)
    )
    # handle numpy bool from table value
    return not (not value)
