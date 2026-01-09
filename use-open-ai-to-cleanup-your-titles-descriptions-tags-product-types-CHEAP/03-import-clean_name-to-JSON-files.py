import json
import csv
import os

# === Input/Output paths ===
INPUT_JSON_FOLDER = "./01_RAW_JSON_DUMPS"
INPUT_CSV = "cleaned_name_outputs.csv"
OUTPUT_JSON_FOLDER = "./02_JSON_DUMPS_CLEANED_TITLES"
LOG_FILE = "cleaned_names_update_log.txt"

os.makedirs(OUTPUT_JSON_FOLDER, exist_ok=True)

# === Read CSV into a dictionary: filename -> clean_name ===
csv_lookup = {}
with open(INPUT_CSV, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_lookup[row["filename"]] = row["clean_name"]

# === Prepare logging ===
log_entries = []

# === Process each JSON file ===
processed_count = 0
skipped_count = 0

for filename in os.listdir(INPUT_JSON_FOLDER):
    if not filename.lower().endswith(".json"):
        continue

    json_path = os.path.join(INPUT_JSON_FOLDER, filename)
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_entries.append(f"{filename}: ERROR reading JSON - {e}")
        skipped_count += 1
        continue

    if filename not in csv_lookup:
        log_entries.append(f"{filename}: NOT FOUND in CSV, skipped")
        skipped_count += 1
        continue

    # Replace the product name
    clean_name = csv_lookup[filename]
    try:
        data["data"]["product"]["name"] = clean_name
    except KeyError:
        log_entries.append(f"{filename}: ERROR - 'data.product.name' path not found")
        skipped_count += 1
        continue

    # Write updated JSON
    output_path = os.path.join(OUTPUT_JSON_FOLDER, filename)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        log_entries.append(f"{filename}: UPDATED successfully")
        processed_count += 1
    except Exception as e:
        log_entries.append(f"{filename}: ERROR writing JSON - {e}")
        skipped_count += 1

# === Write log file ===
with open(LOG_FILE, "w", encoding="utf-8") as f:
    for entry in log_entries:
        f.write(entry + "\n")

# === Summary ===
print(f"Processing complete. {processed_count} files updated, {skipped_count} files skipped.")
print(f"Log written to {LOG_FILE}")
