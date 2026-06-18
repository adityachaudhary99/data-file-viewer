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
