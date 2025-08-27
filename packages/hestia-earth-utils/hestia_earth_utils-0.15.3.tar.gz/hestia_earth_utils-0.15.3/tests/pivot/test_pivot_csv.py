import os
import pandas as pd
from unittest.mock import patch, call

from tests.utils import fixtures_path
from hestia_earth.utils.pivot.pivot_csv import pivot_csv, pivot_hestia_file

class_path = 'hestia_earth.utils.pivot.pivot_csv'
fixtures_folder = os.path.join(fixtures_path, 'pivot', 'pivot_csv')


@patch(
    f"{class_path}.find_term_ids_by_names",
    return_value={
        "Full tillage": "fullTillage",
        "Diesel": "diesel",
        "Inorganic Potassium fertiliser, unspecified (kg K2O)": "inorganicPotassiumFertiliserUnspecifiedKgK2O",
        "Inorganic Phosphorus fertiliser, unspecified (kg P2O5)": "inorganicPhosphorusFertiliserUnspecifiedKgP2O5",
        "Urea (kg N)": "ureaKgN",
        "Peanut, in shell": "peanutInShell",
    },
)
def test_pivot_csv_cycle(mock):
    filepath = f"{fixtures_folder}/cycle.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/cycle-pivoted.csv", index_col=None, dtype=object
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()
    mock.assert_has_calls(
        [
            call(
                [
                    "Diesel",
                    "Full tillage",
                    "Inorganic Phosphorus fertiliser, unspecified (kg P2O5)",
                    "Inorganic Potassium fertiliser, unspecified (kg K2O)",
                    "Peanut, in shell",
                    "Urea (kg N)",
                ]
            )
        ]
    )


@patch(
    f"{class_path}.find_term_ids_by_names",
    return_value={
        "Eutrophication potential, excluding fate": "eutrophicationPotentialExcludingFate",
        "GWP100": "gwp100",
        "N2O, to air, organic fertiliser, direct": "n2OToAirOrganicFertiliserDirect",
        "N2O, to air, inorganic fertiliser, direct": "n2OToAirInorganicFertiliserDirect",
    },
)
def test_pivot_csv_impact(mock):
    filepath = f"{fixtures_folder}/impact.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/impact-pivoted.csv", index_col=None, dtype=object
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()
    mock.assert_has_calls(
        [
            call(
                [
                    "Eutrophication potential, excluding fate",
                    "GWP100",
                    "N2O, to air, inorganic fertiliser, direct",
                    "N2O, to air, organic fertiliser, direct",
                ]
            )
        ]
    )


def test_pivot_csv_multinode_rows():
    filepath = f"{fixtures_folder}/multinode-rows.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/multinode-rows-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()


@patch(
    f"{class_path}.find_term_ids_by_names",
    return_value={"Urea (kg N)": "ureaKgN"},
)
def test_pivot_csv_cycle_missing_ids(mock):
    filepath = f"{fixtures_folder}/missing-ids.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/missing-ids-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()
    mock.assert_has_calls([call(["Urea (kg N)"])])


@patch(
    f"{class_path}.find_term_ids_by_names",
    return_value={"Irrigated": "irrigated"},
)
def test_pivot_csv_empty_cells(mock):
    filepath = f"{fixtures_folder}/empty-cells.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/empty-cells-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()


def test_pivot_csv_preserves_uniqueness_fields():
    filepath = f"{fixtures_folder}/uniqueness-fields-undifferentiating.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/uniqueness-fields-undifferentiating-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()


@patch(
    f"{class_path}.find_term_ids_by_names",
    return_value={
        "Helicopter use, operation unspecified": "helicopterUseOperationUnspecified",
        "Cooling, with evaporative cooling tower": "coolingWithEvaporativeCoolingTower",
        "Small tractor use, operation unspecified": "smallTractorUseOperationUnspecified",
        "Coating seeds": "coatingSeeds",
        "Buttage of vine": "buttageOfVine",
    },
)
def test_pivot_csv_uniqueness_fields_differentiating(mock):
    filepath = f"{fixtures_folder}/uniqueness-fields-differentiating.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/uniqueness-fields-differentiating-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()
    mock.assert_has_calls(
        [
            call(
                [
                    "Buttage of vine",
                    "Coating seeds",
                    "Cooling, with evaporative cooling tower",
                    "Helicopter use, operation unspecified",
                    "Small tractor use, operation unspecified",
                ]
            )
        ]
    )


@patch(
    f"{class_path}.find_term_ids_by_names",
    return_value={
        "Cooling, with evaporative cooling tower": "coolingWithEvaporativeCoolingTower",
    },
)
def test_pivot_csv_uniqueness_fields_non_matching(mock):
    filepath = f"{fixtures_folder}/uniqueness-fields-non-matching.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/uniqueness-fields-non-matching-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()
    mock.assert_has_calls([call(["Cooling, with evaporative cooling tower"])])


@patch(
    f"{class_path}.find_term_ids_by_names",
    return_value={
        "Nitrogen content": "nitrogenContent",
    },
)
def test_pivot_csv_properties(mock):
    filepath = f"{fixtures_folder}/properties-exception.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/properties-exception-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()
    mock.assert_has_calls([call(["Nitrogen content"])])


def test_pivot_csv_depth():
    filepath = f"{fixtures_folder}/depth-exception.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/depth-exception-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()


def test_pivot_csv_shuffled():
    filepath = f"{fixtures_folder}/shuffled.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/shuffled-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()


@patch(
    f"{class_path}.find_term_ids_by_names",
    return_value={"Full tillage": "fullTillage", "Urea (kg N)": "ureaKgN"},
)
def test_pivot_csv_cycle_deep(*args):
    filepath = f"{fixtures_folder}/deep.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/deep-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()


def test_pivot_csv_non_node_arrayfields(*args):
    filepath = f"{fixtures_folder}/non-node-arrayfields.csv"
    expected = pd.read_csv(
        f"{fixtures_folder}/non-node-arrayfields-pivoted.csv",
        index_col=None,
        dtype=object,
    )
    df = pivot_csv(filepath)
    assert df.to_csv() == expected.to_csv()


@patch(
    f"{class_path}.find_term_ids_by_names",
    return_value={
        "Grinding, with grinder": "grinding",
        "Motor gasoline": "motorGasoline",
        "Orchard density": "orchardDensity",
    },
)
def test_pivot_hestia_file(*args):
    filepath = f"{fixtures_folder}/nodes.hestia"
    expected = pd.read_csv(
        f"{fixtures_folder}/nodes.hestia-pivoted.csv",
        index_col=None,
        dtype=object,
    )

    with open(filepath) as fd:
        hestia_file = fd.read()

    df = pivot_hestia_file(hestia_file)
    assert df.to_csv() == expected.to_csv()
