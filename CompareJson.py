from json_utils import compare_json, load_json_file

def main(source_json_path, destination_json_path):
    print(f"🔍 Loading source JSON file: {source_json_path}")
    data1 = load_json_file(source_json_path)
    print(f"🔍 Loading destination JSON file: {destination_json_path}")
    data2 = load_json_file(destination_json_path)
    print("🔄 Comparing JSON files...")
    differences = compare_json(data1, data2)
    if not differences:
        print("✅ Both JSONs are identical.")
    else:
        print("❌ Differences found:")
        for diff in differences:
            print("-", diff)
    print("🏁 Comparison complete.")

if __name__ == "__main__":
    print("🚀 JSON Comparison Utility Started")
    main("Example1.json", "Example2.json")
    print("✅ Comparison utility finished.")
