import json
import csv
import os

# Immutable variable holding the directory with JSON files
json_dumps = "./01_RAW_JSON_DUMPS"  # replace with your folder path for wherever your dumps are if you don't want to use what I provided'

# Output CSV file
output_csv = "name_cleanup_prep.csv"

# Open CSV for writing
with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["filename", "name"])  # header

    # Loop through all JSON files in the directory, one at a time
    for filename in os.listdir(json_dumps):
        if filename.startswith("zendrop_product_") and filename.endswith(".json"):
            filepath = os.path.join(json_dumps, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Safely get the product name
                    product_name = data.get("data", {}).get("product", {}).get("name", "")
                    writer.writerow([filename, product_name])
            except Exception as e:
                print(f"Failed to read {filename}: {e}")

print(f"CSV exported to {output_csv}.")
