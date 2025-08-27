import os
import json
import re
import numpy as np
import pandas as pd

from tests.utils import fixtures_path
from hestia_earth.utils.pivot.pivot_json import (
    _with_csv_formatting,
    pivot_nodes,
    pivot_hestia_file,
)
from flatten_json import unflatten_list
from hestia_earth.schema.utils.sort import SORT_CONFIG
from hestia_earth import schema

class_path = 'hestia_earth.utils.pivot.pivot_csv'
fixtures_folder = os.path.join(fixtures_path, 'pivot', 'pivot_json')

node_types = {k: getattr(schema, k)().fields for k in schema.SCHEMA_TYPES}
name_to_ids_mapping = {
    "Full tillage": "fullTillage",
    "Diesel": "diesel",
    "Motor gasoline": "motorGasoline",
    "Inorganic Potassium fertiliser, unspecified (kg K2O)": "inorganicPotassiumFertiliserUnspecifiedKgK2O",
    "Inorganic Phosphorus fertiliser, unspecified (kg P2O5)": "inorganicPhosphorusFertiliserUnspecifiedKgP2O5",
    "Urea (kg N)": "ureaKgN",
    "Peanut, in shell": "peanutInShell",
    "Eutrophication potential, excluding fate": "eutrophicationPotentialExcludingFate",
    "GWP100": "gwp100",
    "N2O, to air, organic fertiliser, direct": "n2OToAirOrganicFertiliserDirect",
    "N2O, to air, inorganic fertiliser, direct": "n2OToAirInorganicFertiliserDirect",
    "Irrigated": "irrigated",
    "Helicopter use, operation unspecified": "helicopterUseOperationUnspecified",
    "Cooling, with evaporative cooling tower": "coolingWithEvaporativeCoolingTower",
    "Small tractor use, operation unspecified": "smallTractorUseOperationUnspecified",
    "Coating seeds": "coatingSeeds",
    "Buttage of vine": "buttageOfVine",
    "Nitrogen content": "nitrogenContent",
    "Grinding, with grinder": "grinding",
    "Orchard density": "orchardDensity",
}


def _get_node_type(col):
    label = col.split(".")[0]
    return label[0].upper() + label[1:]


def _add_missing_fields(row, is_input, col, parent_type, prefix=""):
    subnode_col = re.search(r"(.+?\.\d+)\.(.+)", col)
    if not subnode_col:
        return None
    sub_node, deep_col = subnode_col.groups()
    node_type = (
        # We are not handling fields like subnode_type_A.subnode_type_B.0
        # We are always fetching type_A in this scenario.
        SORT_CONFIG.get(parent_type)
        .get(sub_node.split(".")[0])
        .get("type")
    )
    next_prefix = ".".join([el for el in (prefix, sub_node) if el])
    row[f"{next_prefix}.@type"] = node_type
    _add_missing_fields(row, is_input, deep_col, node_type, prefix=next_prefix)


def _row_to_dict(row, is_input, parent_type):
    row.dropna(inplace=True)
    if is_input:
        for col in row.index:
            _add_missing_fields(row, is_input, col, parent_type)
    return row.to_dict()


def _df_to_dict(df, is_input):
    df.index = map(lambda col: ".".join(col.split(".")[1:]), df.index)
    df.loc["@type"] = df.name
    dicts = df.apply(_row_to_dict, is_input=is_input, parent_type=df.name)
    return dicts


def _ensure_id_cols(df, name_to_ids):
    names_df = df.filter(regex=r"\.name", axis=1)
    for name_col in names_df.columns:
        id_col = name_col.replace(".name", ".@id")
        for idx, name in df[name_col].items():
            if id_col not in df:
                df[id_col] = np.nan
            if pd.isna(df.loc[idx, id_col]):
                df.loc[idx, id_col] = name_to_ids[name]


def _convert_csv_to_nodes(fixture, is_input, name_to_ids):
    """
    Gets json fixtures or creates them from corresponding csv files.
    Conversion for *-pivoted files is not perfect as we do not detect
    the difference between an empty cell which should be discarded
    (ie. header not used by a row) and a node without a value key
    (the latter are represented in csv as field.nodeId.value = None)
    """
    filepath = (
        f"{fixtures_path}/pivot/pivot_csv/{fixture}.csv"
        if is_input
        else f"{fixtures_path}/pivot/pivot_csv/{fixture}-pivoted.csv"
    )
    df = pd.read_csv(filepath, index_col=None, dtype=object)
    df.drop(columns="-", errors="ignore", inplace=True)
    df.replace("-", np.nan, inplace=True)
    df.replace(
        ["TRUE", "True", "true", "FALSE", "False", "false"],
        [True, True, True, False, False, False],
        inplace=True,
    )
    if is_input:
        df.dropna(how="all", axis=1, inplace=True)
    df.rename(lambda col: col.replace(".id", ".@id"), axis=1, inplace=True)
    if is_input:
        _ensure_id_cols(df, name_to_ids)
    df = df.T.groupby(_get_node_type).apply(_df_to_dict, is_input)
    nodes = [
        node for _node_type, nodes in df.iterrows() for node in nodes if node.get("@id")
    ]
    return nodes


def get_nodes_from_fixture(fixture, name_to_ids={}):
    try:
        with open(f"{fixtures_folder}/{fixture}.json") as file:
            input = json.load(file, object_hook=_with_csv_formatting)["nodes"]
        with open(f"{fixtures_folder}/{fixture}-pivoted.json") as file:
            expected = json.load(file, object_hook=_with_csv_formatting)["nodes"]
    except FileNotFoundError:
        print(f"\n{fixture} not found: attempting to create from csv.\n")
        name_to_ids.update({np.nan: np.nan})
        input = _convert_csv_to_nodes(fixture, True, name_to_ids)
        expected = _convert_csv_to_nodes(fixture, False, name_to_ids)

        input, expected = (
            [unflatten_list(node, ".") for node in input],
            [unflatten_list(node, ".") for node in expected],
        )
        with open(f"{fixtures_folder}/{fixture}.json", "w") as file:
            file.write(json.dumps({"nodes": input}, sort_keys=True, indent=2))
        with open(
            f"{fixtures_folder}/{fixture}-pivoted.json", "w"
        ) as file:
            file.write(json.dumps({"nodes": expected}, sort_keys=True, indent=2))

    return (input, expected)


def test_pivot_json_cycle():
    input, expected = get_nodes_from_fixture("cycle", name_to_ids_mapping)
    actual = pivot_nodes(input)
    assert expected == actual


def test_pivot_json_impact():
    input, expected = get_nodes_from_fixture("impact", name_to_ids_mapping)
    actual = pivot_nodes(input)
    assert expected == actual


def test_pivot_json_multinode_rows():
    input, expected = get_nodes_from_fixture("multinode-rows")
    actual = pivot_nodes(input)
    assert expected == actual


def test_pivot_json_preserves_uniqueness_fields():
    input, expected = get_nodes_from_fixture(
        "uniqueness-fields-undifferentiating", name_to_ids_mapping
    )
    actual = pivot_nodes(input)
    assert expected == actual


def test_pivot_json_uniqueness_fields_differentiating():
    input, expected = get_nodes_from_fixture(
        "uniqueness-fields-differentiating", name_to_ids_mapping
    )
    actual = pivot_nodes(input)
    assert expected == actual


# Output differs from CSV pivoter (see https://gitlab.com/hestia-earth/hestia-utils/-/issues/32)
def test_pivot_json_uniqueness_fields_non_matching():
    input, expected = get_nodes_from_fixture("uniqueness-fields-non-matching", name_to_ids_mapping)
    actual = pivot_nodes(input)
    assert expected == actual


def test_pivot_json_properties():
    input, expected = get_nodes_from_fixture("properties-exception", name_to_ids_mapping)
    actual = pivot_nodes(input)
    assert expected == actual


def test_pivot_json_depth():
    input, expected = get_nodes_from_fixture("depth-exception")
    actual = pivot_nodes(input)
    assert expected == actual


# Output differs from CSV pivoter (see https://gitlab.com/hestia-earth/hestia-utils/-/issues/32)
def test_pivot_json_cycle_deep():
    input, expected = get_nodes_from_fixture("deep", name_to_ids_mapping)
    actual = pivot_nodes(input)
    assert expected == actual


def test_pivot_json_node_arrayfields_merged():
    input, expected = get_nodes_from_fixture("node-arrayfields-merged")
    actual = pivot_nodes(input)

    assert expected == actual


def test_pivot_json_unindexed_node():
    input, expected = get_nodes_from_fixture("unindexed-node")
    actual = pivot_nodes(input)

    assert expected == actual


def test_pivot_hestia_file():
    _input, expected = get_nodes_from_fixture("nodes.hestia", name_to_ids_mapping)
    actual = pivot_hestia_file(
        open(f"{fixtures_folder}/nodes.hestia.json", "r").read()
    )
    assert expected == actual
