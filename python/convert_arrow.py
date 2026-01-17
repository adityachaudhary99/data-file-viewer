#!/usr/bin/env python3
"""Convert Apache Arrow file to JSON"""

import sys
import json
import pyarrow as pa

def convert_array(arr, max_elements=1000):
    """Convert Arrow array to JSON-serializable format"""
    if len(arr) > max_elements:
        return {
            "_type": "arrow.array",
            "type": str(arr.type),
            "length": len(arr),
            "preview": arr[:max_elements].to_pylist(),
            "_note": f"Array truncated. Showing first {max_elements} of {len(arr)} elements"
        }
    return {
        "_type": "arrow.array",
        "type": str(arr.type),
        "data": arr.to_pylist()
    }

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: convert_arrow.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Read Arrow IPC file
        with pa.memory_map(file_path, 'r') as source:
            reader = pa.ipc.open_file(source)
            
            # Get schema
            schema_dict = {
                "fields": [
                    {"name": field.name, "type": str(field.type)}
                    for field in reader.schema
                ]
            }
            
            # Read table
            table = reader.read_all()
            
            # Convert to pandas for easier JSON conversion
            try:
                import pandas as pd
                df = table.to_pandas()
                
                if len(df) > 1000:
                    data_records = df.head(1000).to_dict(orient='records')
                    note = f"Table truncated. Showing first 1000 of {len(df)} rows"
                else:
                    data_records = df.to_dict(orient='records')
                    note = None
                
                result = {
                    "file_type": "arrow",
                    "schema": schema_dict,
                    "num_rows": len(table),
                    "num_columns": len(table.columns),
                    "data": data_records
                }
                
                if note:
                    result["_note"] = note
                    
            except ImportError:
                # Fallback without pandas
                result = {
                    "file_type": "arrow",
                    "schema": schema_dict,
                    "num_rows": len(table),
                    "num_columns": len(table.columns),
                    "columns": {
                        col: convert_array(table[col])
                        for col in table.column_names
                    }
                }
        
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load Arrow file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
