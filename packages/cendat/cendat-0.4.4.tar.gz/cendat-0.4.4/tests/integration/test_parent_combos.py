import polars as pl
import os
from dotenv import load_dotenv
import pytest

load_dotenv()
from cendat.client import CenDatHelper

confirm_src = {
    type: pl.read_csv(f"tests/data/{type}.txt", separator=delim)
    for type, delim in zip(
        [
            "block_groups",
            "tracts",
            "counties",
            "county_subs",
            "places",
            "places_by_county",
        ],
        [
            ",",
            ",",
            ",",
            "|",
            "|",
            "|",
        ],
    )
}

states = (
    confirm_src["counties"]
    .filter(pl.col.STATEFP != 9)
    .select(pl.col.STATEFP.cast(str).str.zfill(2).alias("STATEFP"))
    .get_column("STATEFP")
    .unique()
    .to_list()
)

c = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))
c.list_products(2020, r"\(2020/dec/dhc\)", False)
c.set_products()
c.set_variables("H9_001N")


@pytest.mark.integration
def test_n_calls_counties():

    check_calls = confirm_src["counties"].height

    c.set_geos("050")
    response = c.get_data()
    n_rows = response.to_polars(concat=True).height

    assert c["n_calls"] == 1
    assert n_rows == check_calls


@pytest.mark.integration
def test_n_calls_county_subs():

    check_calls = (
        confirm_src["county_subs"]
        .filter(pl.col.STATEFP.is_in([60, 66, 69, 74, 78]).not_())
        .height
    )

    c.set_geos("060")
    response = c.get_data()
    n_rows = response.to_polars(concat=True).height

    assert c["n_calls"] == 52
    assert n_rows == check_calls


@pytest.mark.integration
def test_n_calls_tracts():

    check_calls = confirm_src["tracts"].height

    c.set_geos("140")
    response = c.get_data()
    n_rows = response.to_pandas(concat=True).shape[0]

    assert c["n_calls"] == 52
    assert n_rows == check_calls


@pytest.mark.integration
def test_n_calls_block_groups():

    check_calls = confirm_src["block_groups"].height

    c.set_geos("150")
    response = c.get_data(timeout=60, max_workers=25)
    n_rows = response.to_polars(concat=True).height

    assert c["n_calls"] == 52
    assert n_rows == check_calls


@pytest.mark.integration
def test_n_calls_places():

    check_calls = (
        confirm_src["places"]
        .filter(pl.col.STATEFP.is_in([60, 66, 69, 74, 78]).not_())
        .height
    )

    c.set_geos("160")
    response = c.get_data()
    n_rows = response.to_polars(concat=True).height

    assert c["n_calls"] == 1
    assert n_rows == check_calls


@pytest.mark.integration
def test_n_calls_places_by_county():

    check_calls = (
        confirm_src["places_by_county"]
        .filter(
            pl.col.STATEFP.is_in([60, 66, 69, 74, 78]).not_(),
        )
        .height
    )

    c.set_geos("159")
    response = c.get_data()
    n_rows = response.to_polars(concat=True).height

    # there are three counties that don't contain places
    assert c["n_calls"] == 3221
    assert n_rows == check_calls
