# === GPT-3.5 Turbo: Generate Product Type & Tags with Custom Tags ===
import csv
import time
import os
from openai import OpenAI

# ==== Immutable variables ====
INPUT_CSV = "tags_product_types_cleanup_prep.csv" # don't forget to add ,custom_tags to the end of the header list at the top before using the next script, and any custom tags separated by |, i.e. ,kitchen|living room
OUTPUT_CSV = "tags_product_types_added.csv"

OPENAI_API_KEY: str = "sk-proj-LONGSTRINGHERE" # # Replace LONGSTRINGHERE with whatever is in your OpenAI account
OPENAI_ORG_ID: str = "org-SHORTSTRINGHERE" # Replace SHORTSTRINGHERE with whatever is in your OpenAI account
OPENAI_ENGINE: str = "gpt-3.5-turbo" #you will have to change this if you want to use a newer version, 3.5 works fine for titles, descriptions, tags and product_types

WAIT_TIMER = 600
PICKUP_TEXT_FILE = "last_successful_tags_type_update_written.txt"
SLEEP_BETWEEN_CALLS = 1 # seconds, in order to be kind to the system and not get your requests dropped
# ==== Immutable variables ====

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY, organization=OPENAI_ORG_ID)

# === Helper function ===
def get_tags_product_type(name: str, description: str):
    """
    Generate product_type and tags using GPT-3.5-turbo.
    Tags returned are pipe-separated.
    """
    prompt = f"""
    You are a product classification assistant.
    Based on the following product name and description, determine:
    1) A concise product_type (e.g., "Bar Stool", "Wardrobe", "Throw Pillow").
    2) 5–10 relevant SEO-friendly tags related to the product_type, name, and description.

    Format your response strictly as:
    product_type: <type>
    tags: tag1|tag2|tag3|tag4|tag5

    Product Name: {name}
    Description: {description}
    """

    while True:
        try:
            response = client.chat.completions.create(
                model=OPENAI_ENGINE,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            content = response.choices[0].message.content.strip()

            # Parse GPT response
            product_type = ""
            tags = ""
            for line in content.splitlines():
                if line.lower().startswith("product_type:"):
                    product_type = line.split(":", 1)[1].strip()
                elif line.lower().startswith("tags:"):
                    tags = line.split(":", 1)[1].strip()

            tags_list = [t.strip() for t in tags.split("|") if t.strip()]
            return product_type, tags_list

        except Exception as e:
            print(f"⚠️ OpenAI/API error: {e}\n→ Waiting {WAIT_TIMER} seconds before retry...")
            time.sleep(WAIT_TIMER)

# === Main Processing ===
def main():
    last_processed_file = None
    if os.path.exists(PICKUP_TEXT_FILE):
        with open(PICKUP_TEXT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                last_processed_file = content
                print(f"⏸️ Resuming after last processed filename: {last_processed_file}")

    with open(INPUT_CSV, "r", encoding="utf-8", newline="") as infile, \
         open(OUTPUT_CSV, "a", encoding="utf-8", newline="") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ['filename', 'name', 'description', 'product_type', 'tags']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        if os.stat(OUTPUT_CSV).st_size == 0:
            writer.writeheader()

        start_processing = last_processed_file is None

        for row in reader:
            filename = row["filename"].strip()
            name = row["name"].strip()
            description = (row.get("description") or "").strip()
            custom_tags_raw = row.get("custom_tags", "")
            custom_tags_list = [t.strip() for t in custom_tags_raw.split("|") if t.strip()]

            # Skip until we reach resume point
            if not start_processing:
                if filename == last_processed_file:
                    start_processing = True
                continue

            # Generate GPT product_type and tags
            product_type, gpt_tags = get_tags_product_type(name, description)

            # Combine GPT tags with custom tags
            all_tags = gpt_tags + custom_tags_list

            # Write row to OUTPUT_CSV
            writer.writerow({
                "filename": filename,
                "name": name,
                "description": description,
                "product_type": product_type,
                "tags": "|".join(all_tags)
            })
            outfile.flush()

            # Update PICKUP_TEXT_FILE
            with open(PICKUP_TEXT_FILE, "w", encoding="utf-8") as f:
                f.write(filename)

            print(f"✅ Processed: {filename}")
            time.sleep(SLEEP_BETWEEN_CALLS)

    print("🎉 All rows processed successfully.")

if __name__ == "__main__":
    main()
