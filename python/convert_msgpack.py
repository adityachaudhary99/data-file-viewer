#!/usr/bin/env python3
"""Convert MessagePack file to JSON"""

import sys
import json
import msgpack
from datetime import datetime, date

def convert_to_serializable(obj, max_depth=10, current_depth=0):
    """Convert objects to JSON-serializable format"""
    
    if current_depth > max_depth:
        return f"<Max depth reached: {type(obj).__name__}>"
    
    # Handle None
    if obj is None:
        return None
    
    # Handle basic types
    if isinstance(obj, (bool, int, float, str)):
        return obj
    
    # Handle bytes
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8')
        except:
            return f"<bytes: {len(obj)} bytes>"
    
    # Handle datetime
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    
    # Handle dict
    if isinstance(obj, dict):
        return {
            str(k): convert_to_serializable(v, max_depth, current_depth + 1)
            for k, v in obj.items()
        }
    
    # Handle list, tuple
    if isinstance(obj, (list, tuple)):
        result = [convert_to_serializable(item, max_depth, current_depth + 1) for item in obj]
        if isinstance(obj, tuple):
            return {"_type": "tuple", "data": result}
        return result
    
    # Fallback
    return str(obj)

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: convert_msgpack.py <file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'rb') as f:
            data = msgpack.unpack(f, raw=False, strict_map_key=False)
        
        result = {
            "file_type": "msgpack",
            "data": convert_to_serializable(data)
        }
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load MessagePack file: {str(e)}",
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
