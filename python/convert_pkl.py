#!/usr/bin/env python3
"""Convert pickle file to JSON"""

import sys
import json
import pickle
import math
import numpy as np
from datetime import datetime, date

def convert_to_serializable(obj, max_depth=10, current_depth=0):
    """Convert Python objects to JSON-serializable format"""
    
    if current_depth > max_depth:
        return f"<Max depth reached: {type(obj).__name__}>"
    
    # Handle None
    if obj is None:
        return None
    
    # Handle basic types
    if isinstance(obj, (bool, int, str)):
        return obj
    
    # Handle float with NaN/Infinity
    if isinstance(obj, float):
        if math.isnan(obj):
            return None  # Convert NaN to null
        elif math.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
        return obj
    
    # Handle numpy types
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        val = float(obj)
        if math.isnan(val):
            return None  # Convert NaN to null
        elif math.isinf(val):
            return "Infinity" if val > 0 else "-Infinity"
        return val
    if isinstance(obj, (complex, np.complexfloating)):
        return {
            "_type": "complex",
            "real": float(obj.real),
            "imag": float(obj.imag)
        }
    if isinstance(obj, np.ndarray):
        # Handle complex arrays
        if np.iscomplexobj(obj):
            if obj.size > 1000:
                preview = obj.flatten()[:100]
                return {
                    "_type": "numpy.ndarray",
                    "dtype": str(obj.dtype),
                    "shape": obj.shape,
                    "size": int(obj.size),
                    "preview": [{"real": float(x.real), "imag": float(x.imag)} for x in preview],
                    "_note": f"Complex array truncated. Showing first 100 of {obj.size} elements"
                }
            return {
                "_type": "numpy.ndarray",
                "dtype": str(obj.dtype),
                "shape": obj.shape,
                "data": [{"real": float(x.real), "imag": float(x.imag)} for x in obj.flatten()]
            }
        
        # Handle regular arrays
        if obj.size > 1000:
            preview = obj.flatten()[:100]
            # Convert each element to handle NaN/Infinity
            preview_list = [convert_to_serializable(x, max_depth, current_depth + 1) for x in preview]
            return {
                "_type": "numpy.ndarray",
                "dtype": str(obj.dtype),
                "shape": obj.shape,
                "size": int(obj.size),
                "preview": preview_list,
                "_note": f"Array truncated. Showing first 100 of {obj.size} elements"
            }
        # Convert each element to handle NaN/Infinity
        data_list = [convert_to_serializable(x, max_depth, current_depth + 1) for x in obj.flatten()]
        return {
            "_type": "numpy.ndarray",
            "dtype": str(obj.dtype),
            "shape": obj.shape,
            "data": data_list
        }
    
    # Handle datetime
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    
    # Handle bytes
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8')
        except:
            return f"<bytes: {len(obj)} bytes>"
    
    # Handle dict
    if isinstance(obj, dict):
        return {
            str(k): convert_to_serializable(v, max_depth, current_depth + 1)
            for k, v in obj.items()
        }
    
    # Handle list, tuple, set
    if isinstance(obj, (list, tuple, set)):
        result = [convert_to_serializable(item, max_depth, current_depth + 1) for item in obj]
        if isinstance(obj, tuple):
            return {"_type": "tuple", "data": result}
        elif isinstance(obj, set):
            return {"_type": "set", "data": result}
        return result
    
    # Handle pandas DataFrame
    try:
        import pandas as pd
        if isinstance(obj, pd.DataFrame):
            # Replace NaN with None for JSON compatibility
            obj_clean = obj.replace({np.nan: None, np.inf: "Infinity", -np.inf: "-Infinity"})
            if len(obj) > 1000:
                return {
                    "_type": "pandas.DataFrame",
                    "shape": obj.shape,
                    "columns": obj.columns.tolist(),
                    "dtypes": {k: str(v) for k, v in obj.dtypes.items()},
                    "preview": obj_clean.head(100).to_dict(orient='records'),
                    "_note": f"DataFrame truncated. Showing first 100 of {len(obj)} rows"
                }
            return {
                "_type": "pandas.DataFrame",
                "shape": obj.shape,
                "columns": obj.columns.tolist(),
                "data": obj_clean.to_dict(orient='records')
            }
        if isinstance(obj, pd.Series):
            # Replace NaN with None for JSON compatibility
            series_clean = obj.replace({np.nan: None, np.inf: "Infinity", -np.inf: "-Infinity"})
            return {
                "_type": "pandas.Series",
                "name": obj.name,
                "data": series_clean.tolist()
            }
    except ImportError:
        pass
    
    # Handle custom objects
    if hasattr(obj, '__dict__'):
        return {
            "_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "_attributes": convert_to_serializable(obj.__dict__, max_depth, current_depth + 1)
        }
    
    # Fallback
    return f"<{type(obj).__name__}: {str(obj)[:100]}>"

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: convert_pkl.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        result = {
            "file_type": "pickle",
            "data": convert_to_serializable(data)
        }
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load pickle file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
