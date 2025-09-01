import json
import math
import sys

def compare_json(obj1, obj2, delta=1e-19, path=""):
    """
    Recursively compare two JSON-loaded objects (dicts, lists, numbers, etc.)
    allowing for floating-point tolerance.
    """
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        # Compare keys
        if set(obj1.keys()) != set(obj2.keys()):
            print(f"Key mismatch at {path}: {set(obj1.keys())} vs {set(obj2.keys())}")
            return False
        # Compare values
        for key in obj1:
            if not compare_json(obj1[key], obj2[key], delta, f"{path}.{key}" if path else key):
                return False
        return True

    elif isinstance(obj1, list) and isinstance(obj2, list):
        if len(obj1) != len(obj2):
            print(f"Length mismatch at {path}: {len(obj1)} vs {len(obj2)}")
            return False
        for i, (v1, v2) in enumerate(zip(obj1, obj2)):
            if not compare_json(v1, v2, delta, f"{path}[{i}]"):
                return False
        return True

    elif isinstance(obj1, (int, float)) and isinstance(obj2, (int, float)):
        if not math.isclose(obj1, obj2, rel_tol=delta, abs_tol=delta):
            print(f"Float mismatch at {path}: {obj1} vs {obj2} (delta={delta})")
            return False
        return True

    else:
        if obj1 != obj2:
            print(f"Mismatch at {path}: {obj1} vs {obj2}")
            return False
        return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_json.py file1.json file2.json")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]

    with open(file1, "r") as f1, open(file2, "r") as f2:
        json1 = json.load(f1)
        json2 = json.load(f2)

    if compare_json(json1, json2, delta=1e-6):
        print("✅ JSON files match (within tolerance).")
    else:
        print("❌ JSON files differ.")
