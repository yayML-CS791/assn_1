import json
import sys
import math

def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)

def compare_marginals(json1, json2, tol=1e-6):
    diffs = []
    
    n1, n2 = len(json1), len(json2)
    if n1 != n2:
        diffs.append(f"Different number of entries: {n1} vs {n2}")
    
    for i in range(min(n1, n2)):
        m1, m2 = json1[i]["Marginals"], json2[i]["Marginals"]
        if len(m1) != len(m2):
            diffs.append(f"[Entry {i}] Different marginal length: {len(m1)} vs {len(m2)}")
            continue
        
        for j in range(len(m1)):
            if len(m1[j]) != len(m2[j]):
                diffs.append(f"[Entry {i}, Row {j}] Different vector size: {len(m1[j])} vs {len(m2[j])}")
                continue
            
            for k in range(len(m1[j])):
                v1, v2 = m1[j][k], m2[j][k]
                if abs(v1 - v2) > tol:
                    diffs.append(
                        f"[Entry {i}, Row {j}, Index {k}] {v1:.9f} vs {v2:.9f} "
                        f"(diff={abs(v1-v2):.2e})"
                    )
    return diffs

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_json.py file1.json file2.json")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]
    json1, json2 = load_json(file1), load_json(file2)
    
    differences = compare_marginals(json1, json2)
    if differences:
        print("Differences found:")
        for d in differences:
            print("  -", d)
    else:
        print("No differences (within tolerance).")
