#!/usr/bin/env python3
"""Convert NumPy .npy/.npz file to JSON"""

import sys
import json
import numpy as np
import os

def convert_array(arr, max_elements=1000):
    """Convert numpy array to JSON-serializable format"""
    if arr.size > max_elements:
        return {
            "_type": "numpy.ndarray",
            "dtype": str(arr.dtype),
            "shape": arr.shape,
            "size": int(arr.size),
            "preview": arr.flatten()[:max_elements].tolist(),
            "_note": f"Array truncated. Showing first {max_elements} of {arr.size} elements"
        }
    return {
        "_type": "numpy.ndarray",
        "dtype": str(arr.dtype),
        "shape": arr.shape,
        "data": arr.tolist()
    }

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: convert_npy.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.npz':
            # Handle .npz (compressed archive of multiple arrays)
            data = np.load(file_path)
            arrays = {}
            
            for key in data.files:
                arrays[key] = convert_array(data[key])
            
            result = {
                "file_type": "npz",
                "num_arrays": len(data.files),
                "arrays": list(data.files),
                "data": arrays
            }
        else:
            # Handle .npy (single array)
            data = np.load(file_path)
            result = {
                "file_type": "npy",
                "data": convert_array(data)
            }
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load NumPy file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
