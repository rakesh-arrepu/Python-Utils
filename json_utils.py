import json

def compare_json(json1, json2, path=""):
    """
    Recursively compare two JSON-compatible Python objects.
    Returns a list of human-readable differences.
    """
    differences = []

    if isinstance(json1, dict) and isinstance(json2, dict):
        print(f"🔎 Comparing dicts at path: '{path}'")
        for key in json1:
            current_path = f"{path}.{key}" if path else key
            if key not in json2:
                print(f"⚠️  Key '{current_path}' missing in second JSON")
                differences.append(f"Key '{current_path}' is missing in json2")
            else:
                differences.extend(compare_json(json1[key], json2[key], current_path))
        for key in json2:
            current_path = f"{path}.{key}" if path else key
            if key not in json1:
                print(f"⚠️  Key '{current_path}' missing in first JSON")
                differences.append(f"Key '{current_path}' is missing in json1")
    elif isinstance(json1, list) and isinstance(json2, list):
        print(f"🔎 Comparing lists at path: '{path}'")
        min_length = min(len(json1), len(json2))
        max_length = max(len(json1), len(json2))
        for i in range(min_length):
            current_path = f"{path}[{i}]"
            differences.extend(compare_json(json1[i], json2[i], current_path))
        if len(json1) > len(json2):
            for i in range(min_length, max_length):
                print(f"⚠️  Extra element at '{path}[{i}]' in first JSON: {json1[i]}")
                differences.append(f"Extra element at '{path}[{i}]' in json1: {json1[i]}")
        elif len(json2) > len(json1):
            for i in range(min_length, max_length):
                print(f"⚠️  Extra element at '{path}[{i}]' in second JSON: {json2[i]}")
                differences.append(f"Extra element at '{path}[{i}]' in json2: {json2[i]}")
    else:
        if json1 != json2:
            print(f"❗ Value mismatch at '{path}': '{json1}' (json1) vs '{json2}' (json2)")
            differences.append(
                f"Value mismatch at '{path}': json1 has '{json1}' but json2 has '{json2}'"
            )
    return differences

def load_json_file(filepath):
    """
    Loads a JSON file and returns the parsed data.
    """
    print(f"📂 Loading JSON file: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
    print(f"✅ Successfully loaded: {filepath}")
    return data