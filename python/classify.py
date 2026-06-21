import os


class UnsupportedFile(Exception):
    pass


_EXT_TO_KIND = {
    ".parquet": "tabular",
    ".feather": "tabular",
    ".arrow": "tabular",
    ".avro": "tabular",
    ".npy": "array",
    ".npz": "array",
    ".h5": "hierarchical",
    ".hdf5": "hierarchical",
    ".nc": "hierarchical",
    ".nc4": "hierarchical",
    ".netcdf": "hierarchical",
    ".mat": "hierarchical",
    ".pkl": "auto",
    ".pickle": "auto",
    ".joblib": "auto",
    ".msgpack": "auto",
    ".mp": "auto",
}


def classify(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    kind = _EXT_TO_KIND.get(ext)
    if kind is None:
        raise UnsupportedFile(f"No explorer support yet for '{ext}'")
    return kind
