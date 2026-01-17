#!/usr/bin/env python3
"""Convert Apache Avro file to JSON"""

import sys
import json

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: convert_avro.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        from avro.datafile import DataFileReader
        from avro.io import DatumReader
        
        records = []
        with open(file_path, 'rb') as f:
            reader = DataFileReader(f, DatumReader())
            
            # Get schema
            schema = json.loads(str(reader.schema))
            
            # Read records
            for i, record in enumerate(reader):
                if i >= 1000:  # Limit to 1000 records
                    break
                records.append(record)
            
            total_records = i + 1
            reader.close()
        
        result = {
            "file_type": "avro",
            "schema": schema,
            "num_records": total_records,
            "data": records
        }
        
        if total_records >= 1000:
            result["_note"] = f"Records truncated. Showing first 1000 records"
        
        print(json.dumps(result, indent=2, default=str))
    except ImportError:
        print(json.dumps({
            "error": "Missing Python package: avro\n\nInstall with: pip install avro-python3",
            "error_type": "ImportError"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load Avro file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
