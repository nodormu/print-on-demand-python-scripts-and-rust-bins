import csv
import json
import os
import time

# === Immutable variables ===
INPUT_JSON_FOLDER = "./03_JSON_DUMPS_CLEANED_DESCRIPTIONS"
INPUT_CSV = "tags_product_types_added.csv"
OUTPUT_JSON_FOLDER = "./04_JSON_DUMPS_CLEANED_TAGS_PRODUCT_TYPES"
LOG_FILE = "json_tags_type_update_log.txt"
SLEEP_BETWEEN_FILES = 0.1  # Adjust if needed
# === Immutable variables ===

# Ensure output folder exists
os.makedirs(OUTPUT_JSON_FOLDER, exist_ok=True)

# Load list of already processed files from log
processed_files = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        processed_files = set(line.strip() for line in f if line.strip())

# Process CSV
with open(INPUT_CSV, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        filename = row["filename"].strip()

        # Skip already processed files
        if filename in processed_files:
            continue

        input_json_path = os.path.join(INPUT_JSON_FOLDER, filename)
        output_json_path = os.path.join(OUTPUT_JSON_FOLDER, filename)

        if not os.path.exists(input_json_path):
            print(f"⚠️ JSON file not found: {input_json_path}")
            continue

        try:
            # Load JSON
            with open(input_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Navigate to product data
            product = data.get("data", {}).get("product", {})
            if not product:
                print(f"⚠️ No product data in {filename}")
                continue

            # Update product_type
            product_type = row.get("product_type", "").strip()
            if product_type:
                product["product_type"] = product_type

                # Update all variant_product_type fields
                variants = product.get("product_variant", [])
                for variant in variants:
                    variant["variant_product_type"] = product_type

            # Update tags (split by pipe)
            tags_str = row.get("tags", "").strip()
            if tags_str:
                product["tags"] = [tag.strip() for tag in tags_str.split("|") if tag.strip()]

            # Write updated JSON to output folder
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Log success
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(filename + "\n")

            print(f"✅ Updated JSON: {filename}")
            time.sleep(SLEEP_BETWEEN_FILES)

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")
