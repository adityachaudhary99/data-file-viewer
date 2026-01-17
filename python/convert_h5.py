#!/usr/bin/env python3
"""Convert HDF5 file to JSON"""

import sys
import json
import math
import h5py
import numpy as np

def convert_dataset(dataset, max_elements=1000):
    """Convert HDF5 dataset to JSON-serializable format"""
    data = dataset[()]
    
    # Handle numpy arrays
    if isinstance(data, np.ndarray):
        # Handle complex arrays
        if np.iscomplexobj(data):
            if data.size > max_elements:
                preview = data.flatten()[:max_elements]
                return {
                    "_type": "hdf5.dataset",
                    "dtype": str(data.dtype),
                    "shape": data.shape,
                    "size": int(data.size),
                    "preview": [{"real": float(x.real), "imag": float(x.imag)} for x in preview],
                    "_note": f"Complex dataset truncated. Showing first {max_elements} of {data.size} elements"
                }
            return {
                "_type": "hdf5.dataset",
                "dtype": str(data.dtype),
                "shape": data.shape,
                "data": [{"real": float(x.real), "imag": float(x.imag)} for x in data.flatten()]
            }
        
        # Handle regular arrays
        if data.size > max_elements:
            return {
                "_type": "hdf5.dataset",
                "dtype": str(data.dtype),
                "shape": data.shape,
                "size": int(data.size),
                "preview": data.flatten()[:max_elements].tolist(),
                "_note": f"Dataset truncated. Showing first {max_elements} of {data.size} elements"
            }
        return {
            "_type": "hdf5.dataset",
            "dtype": str(data.dtype),
            "shape": data.shape,
            "data": data.tolist()
        }
    
    # Handle scalar values
    if isinstance(data, (np.integer, np.floating)):
        return {
            "_type": "hdf5.dataset",
            "dtype": str(dataset.dtype),
            "value": float(data) if isinstance(data, np.floating) else int(data)
        }
    
    # Handle strings
    if isinstance(data, (str, bytes)):
        return {
            "_type": "hdf5.dataset",
            "dtype": str(dataset.dtype),
            "value": data.decode('utf-8') if isinstance(data, bytes) else data
        }
    
    return str(data)

def explore_group(group, max_depth=10, current_depth=0):
    """Recursively explore HDF5 group structure"""
    
    if current_depth > max_depth:
        return {"_note": "Max depth reached"}
    
    result = {
        "_type": "hdf5.group",
        "_attributes": {k: str(v) for k, v in group.attrs.items()} if group.attrs else {}
    }
    
    for key in group.keys():
        item = group[key]
        
        if isinstance(item, h5py.Group):
            result[key] = explore_group(item, max_depth, current_depth + 1)
        elif isinstance(item, h5py.Dataset):
            try:
                result[key] = convert_dataset(item)
            except Exception as e:
                result[key] = {
                    "_type": "hdf5.dataset",
                    "_error": f"Failed to read dataset: {str(e)}",
                    "dtype": str(item.dtype),
                    "shape": item.shape
                }
    
    return result

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: convert_h5.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with h5py.File(file_path, 'r') as f:
            result = {
                "file_type": "hdf5",
                "_attributes": {k: str(v) for k, v in f.attrs.items()} if f.attrs else {},
                "data": explore_group(f)
            }
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load HDF5 file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
