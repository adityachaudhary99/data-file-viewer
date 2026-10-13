import math
import numpy as np
import pandas as pd
from python.jsonsafe import to_jsonable


def test_nan_and_inf_become_none():
    assert to_jsonable(float("nan")) is None
    assert to_jsonable(float("inf")) is None
    assert to_jsonable(np.float64("nan")) is None


def test_nat_becomes_none():
    assert to_jsonable(pd.NaT) is None


def test_numpy_scalars_become_python_scalars():
    assert to_jsonable(np.int64(5)) == 5 and isinstance(to_jsonable(np.int64(5)), int)
    assert to_jsonable(np.bool_(True)) is True


def test_passthrough_plain_values():
    assert to_jsonable("hi") == "hi"
    assert to_jsonable(3) == 3
    assert to_jsonable(None) is None


def test_complex_scalar_serializes():
    import json
    assert to_jsonable(np.complex128(1+2j)) == "1+2j"
    assert json.dumps(to_jsonable(np.complex128(3-4j)))  # must not raise
    assert to_jsonable(complex(0, 1)) == "0+1j"


def test_array_cells_become_json_lists():
    import json
    assert to_jsonable(np.array([0.1, 0.2, 0.3], dtype=np.float32)) == [0.1, 0.2, 0.3]
    assert to_jsonable(np.array([[1, 2], [3, 4]])) == [[1, 2], [3, 4]]
    assert to_jsonable({"a": np.array([1.5, np.nan])}) == {"a": [1.5, None]}
    assert to_jsonable((1, np.int64(2))) == [1, 2]
    assert json.dumps(to_jsonable(np.arange(3)))  # must not raise


def test_float32_scalar_uses_shortest_repr():
    assert to_jsonable(np.float32(0.1)) == 0.1
    assert to_jsonable(np.float32("nan")) is None


def test_datetime_values_become_strings():
    import datetime
    assert to_jsonable(pd.Timestamp("2026-01-01 08:30")) == "2026-01-01 08:30:00"
    assert to_jsonable(np.datetime64("2026-01-01T08:30:00.000000000")) == "2026-01-01 08:30:00"
    assert to_jsonable(np.datetime64("NaT")) is None
    assert to_jsonable(pd.Timedelta(seconds=90)) == "0 days 00:01:30"
    assert to_jsonable(datetime.date(2026, 1, 2)) == "2026-01-02"


def test_unknown_objects_fall_back_to_str():
    from decimal import Decimal
    assert to_jsonable(Decimal("1.50")) == "1.50"
