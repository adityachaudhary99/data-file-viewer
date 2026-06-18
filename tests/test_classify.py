import pytest
from python.classify import classify, UnsupportedFile


def test_parquet_is_tabular():
    assert classify("/some/path/data.parquet") == "tabular"


def test_unknown_extension_raises():
    with pytest.raises(UnsupportedFile):
        classify("/some/path/data.unknownext")


def test_feather_and_arrow_are_tabular():
    assert classify("/x/data.feather") == "tabular"
    assert classify("/x/data.arrow") == "tabular"
