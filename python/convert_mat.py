#!/usr/bin/env python3
"""Convert MATLAB .mat file to JSON"""

import sys
import json
import numpy as np
from datetime import datetime, date

def convert_to_serializable(obj, max_depth=10, current_depth=0):
    """Convert MATLAB objects to JSON-serializable format"""
    
    if current_depth > max_depth:
        return f"<Max depth reached: {type(obj).__name__}>"
    
    # Handle None
    if obj is None:
        return None
    
    # Handle basic types
    if isinstance(obj, (bool, int, float, str)):
        return obj
    
    # Handle numpy types
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        if obj.size > 1000:
            return {
                "_type": "matlab.array",
                "dtype": str(obj.dtype),
                "shape": obj.shape,
                "size": int(obj.size),
                "preview": obj.flatten()[:100].tolist(),
                "_note": f"Array truncated. Showing first 100 of {obj.size} elements"
            }
        return {
            "_type": "matlab.array",
            "dtype": str(obj.dtype),
            "shape": obj.shape,
            "data": obj.tolist()
        }
    
    # Handle bytes
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8')
        except:
            return f"<bytes: {len(obj)} bytes>"
    
    # Handle dict (MATLAB structures)
    if isinstance(obj, dict):
        return {
            str(k): convert_to_serializable(v, max_depth, current_depth + 1)
            for k, v in obj.items()
            if not k.startswith('__')  # Skip MATLAB metadata fields
        }
    
    # Handle list, tuple
    if isinstance(obj, (list, tuple)):
        result = [convert_to_serializable(item, max_depth, current_depth + 1) for item in obj]
        return result
    
    # Handle scipy sparse matrices
    try:
        from scipy import sparse
        if sparse.issparse(obj):
            return {
                "_type": "matlab.sparse",
                "format": obj.format,
                "shape": obj.shape,
                "nnz": obj.nnz,
                "data": convert_to_serializable(obj.toarray())
            }
    except ImportError:
        pass
    
    # Fallback
    return f"<{type(obj).__name__}: {str(obj)[:100]}>"

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: convert_mat.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        from scipy.io import loadmat
        
        # Load MATLAB file
        mat_data = loadmat(file_path, squeeze_me=True, struct_as_record=False)
        
        # Remove MATLAB metadata
        filtered_data = {
            k: v for k, v in mat_data.items()
            if not k.startswith('__')
        }
        
        result = {
            "file_type": "matlab",
            "variables": list(filtered_data.keys()),
            "data": convert_to_serializable(filtered_data)
        }
        
        print(json.dumps(result, indent=2))
    except ImportError:
        print(json.dumps({
            "error": "Missing Python package: scipy\n\nInstall with: pip install scipy",
            "error_type": "ImportError"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load MATLAB file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
