import json
import csv
import os
import re

# === Input/Output paths ===
INPUT_JSON_FOLDER = "./02_JSON_DUMPS_CLEANED_TITLES"
INPUT_CSV = "cleaned_descriptions_with_html_coding.csv"
OUTPUT_JSON_FOLDER = "./03_JSON_DUMPS_CLEANED_DESCRIPTIONS"
LOG_FILE = "cleaned_descriptions_update_log.txt"

os.makedirs(OUTPUT_JSON_FOLDER, exist_ok=True)

# === Read CSV into a dictionary: filename -> clean_description ===
csv_lookup = {}
with open(INPUT_CSV, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_lookup[row["filename"]] = row["clean_description"]

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

    # Extract original <img> tags from the old description
    try:
        original_desc = data["data"]["product"]["description"]
        img_tags = re.findall(r'<img [^>]+>', original_desc)
    except KeyError:
        log_entries.append(f"{filename}: ERROR - 'data.product.description' path not found")
        skipped_count += 1
        continue

    # Replace the product description with the cleaned version
    clean_desc = csv_lookup[filename].strip()

    # Append original <img> tags at the end if not already present
    for img in img_tags:
        if img not in clean_desc:
            clean_desc += "\n" + img

    try:
        data["data"]["product"]["description"] = clean_desc
    except KeyError:
        log_entries.append(f"{filename}: ERROR - 'data.product.description' path not found during assignment")
        skipped_count += 1
        continue

    # Write updated JSON
    output_path = os.path.join(OUTPUT_JSON_FOLDER, filename)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        log_entries.append(f"{filename}: DESCRIPTION UPDATED successfully")
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
