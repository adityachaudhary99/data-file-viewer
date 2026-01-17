#!/usr/bin/env python3
"""Convert Parquet file to JSON"""

import sys
import json
import pyarrow.parquet as pq
import numpy as np

def convert_value(val):
    """Convert numpy/arrow types to JSON-serializable format"""
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    if isinstance(val, (np.floating, np.float64, np.float32)):
        return float(val)
    if isinstance(val, np.ndarray):
        return val.tolist()
    if isinstance(val, bytes):
        try:
            return val.decode('utf-8')
        except:
            return f"<bytes: {len(val)} bytes>"
    if pd.isna(val):
        return None
    return val

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: convert_parquet.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        import pandas as pd
        
        # Read parquet file
        df = pd.read_parquet(file_path)
        
        # Get metadata
        parquet_file = pq.ParquetFile(file_path)
        metadata = parquet_file.metadata
        
        # Convert to JSON
        if len(df) > 1000:
            data_records = df.head(1000).to_dict(orient='records')
            note = f"DataFrame truncated. Showing first 1000 of {len(df)} rows"
        else:
            data_records = df.to_dict(orient='records')
            note = None
        
        result = {
            "file_type": "parquet",
            "metadata": {
                "num_rows": metadata.num_rows,
                "num_columns": metadata.num_columns,
                "num_row_groups": metadata.num_row_groups,
                "format_version": metadata.format_version,
                "created_by": metadata.created_by
            },
            "schema": {
                "columns": df.columns.tolist(),
                "dtypes": {k: str(v) for k, v in df.dtypes.items()}
            },
            "shape": df.shape,
            "data": data_records
        }
        
        if note:
            result["_note"] = note
        
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load Parquet file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
