#!/usr/bin/env python3
"""Convert Feather file to JSON"""

import sys
import json

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: convert_feather.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        import pandas as pd
        
        # Read feather file
        df = pd.read_feather(file_path)
        
        # Convert to JSON
        if len(df) > 1000:
            data_records = df.head(1000).to_dict(orient='records')
            note = f"DataFrame truncated. Showing first 1000 of {len(df)} rows"
        else:
            data_records = df.to_dict(orient='records')
            note = None
        
        result = {
            "file_type": "feather",
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
            "error": f"Failed to load Feather file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
