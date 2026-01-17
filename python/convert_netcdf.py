#!/usr/bin/env python3
"""Convert NetCDF file to JSON"""

import sys
import json
import numpy as np

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
        print(json.dumps({"error": "Usage: convert_netcdf.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        from netCDF4 import Dataset
        
        nc = Dataset(file_path, 'r')
        
        # Get dimensions
        dimensions = {
            name: len(dim) for name, dim in nc.dimensions.items()
        }
        
        # Get global attributes
        attributes = {
            name: nc.getncattr(name) for name in nc.ncattrs()
        }
        
        # Get variables
        variables = {}
        for var_name in nc.variables:
            var = nc.variables[var_name]
            variables[var_name] = {
                "dimensions": var.dimensions,
                "dtype": str(var.dtype),
                "shape": var.shape,
                "attributes": {
                    name: var.getncattr(name) for name in var.ncattrs()
                },
                "data": convert_array(var[:])
            }
        
        # Get groups (if any)
        groups = list(nc.groups.keys()) if hasattr(nc, 'groups') else []
        
        result = {
            "file_type": "netcdf",
            "dimensions": dimensions,
            "attributes": attributes,
            "variables": variables,
            "groups": groups
        }
        
        nc.close()
        
        print(json.dumps(result, indent=2, default=str))
    except ImportError:
        print(json.dumps({
            "error": "Missing Python package: netCDF4\n\nInstall with: pip install netCDF4",
            "error_type": "ImportError"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load NetCDF file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
