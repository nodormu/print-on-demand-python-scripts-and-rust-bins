# === GPT-3.5 Turbo: Product Description Cleanup (Hybrid with HTML Unescape & Empty List Cleanup) ===
import csv
import re
import time
import os
from html import unescape
import openai

# === Immutable Variables ===
INPUT_CSV: str = "descriptions_cleanup_prep.csv"
OUTPUT_CSV: str = "cleaned_descriptions_with_html_coding.csv"

OPENAI_API_KEY: str = "sk-proj-LONGSTRINGHERE" # Replace LONGSTRINGHERE with whatever is in your OpenAI account
OPENAI_ORG_ID: str = "org-SHORTSTRINGHERE" # Replace SHORTSTRINGHERE with whatever is in your OpenAI account
OPENAI_ENGINE: str = "gpt-3.5-turbo" # or choose whatever engine you want to use, but 3.5 turbo is fine for titles, descriptions, tags and product_types

WAIT_TIMER = 600 #if you hit a http/429, this will allow the script to sleep for 600 seconds till it picks back up where it left off in the PICKUP_TEXT_FILE
PICKUP_TEXT_FILE = "last_item_successfully_completed.txt" #since the descriptions can get long at times, this is in case you hit your limit while making a HUGE list of requests
SLEEP_BETWEEN_CALLS = 1 # number of seconds between calls

# === OpenAI Setup ===
openai.api_key = OPENAI_API_KEY
if OPENAI_ORG_ID:
    openai.organization = OPENAI_ORG_ID

# === Helper Functions ===
def pre_clean_description(desc: str) -> str:
    """
    Light pre-cleaning to reduce GPT tokens and improve output consistency:
    - Strip 'Product Description' labels
    - Remove duplicate <p> or <br> tags
    - Collapse multiple spaces or newlines
    - Trim broken HTML remnants
    """
    if not desc:
        return ""
    # Remove “Product Description” or “description” labels at start
    desc = re.sub(r'^\s*(Product\s*Description|description)\s*[:\-]?\s*', '', desc, flags=re.I)
    # Remove repeated <p> or <br> tags
    desc = re.sub(r'(<p>\s*){2,}', '<p>', desc, flags=re.I)
    desc = re.sub(r'(<br>\s*){2,}', '<br>', desc, flags=re.I)
    # Collapse multiple spaces/newlines
    desc = re.sub(r'\s{2,}', ' ', desc)
    return desc.strip()

def collapse_empty_lists(html: str) -> str:
    """
    Remove empty <li> and <ul> tags from HTML.
    - Empty <li> inside <ul> are deleted
    - Completely empty <ul> tags are deleted
    """
    if not html:
        return ""
    # Remove empty <li>
    html = re.sub(r'<li>\s*</li>', '', html, flags=re.I)
    # Remove empty <ul> (after <li> cleanup)
    html = re.sub(r'<ul>\s*</ul>', '', html, flags=re.I)
    return html

def gpt_generate_clean_description(title: str, raw_description: str) -> str:
    """
    Sends the product title and pre-cleaned description to GPT for cleanup.
    Returns cleaned HTML description with unescaped entities and empty lists removed.
    Retries automatically on network/rate-limit errors.
    """
    while True:
        try:
            response = openai.chat.completions.create(
                model=OPENAI_ENGINE,
                messages=[
                    {"role": "system", "content": (
                        "You are an expert e-commerce content editor."
                        " Rewrite product descriptions to be customer-friendly,"
                        " visually clean, HTML-ready, with paragraph first and bullet points"
                        " for specifications. Retain all valid data (sizes, colors, quantities)."
                        " Keep images intact at the end inside a <div class='product-images'> block."
                        " Do not invent features; use only information provided."
                    )},
                    {"role": "user", "content": (
                        f"Product Name: {title}\n"
                        f"Current Description: {raw_description}\n\n"
                        "Please output a clean, well-formatted HTML description with paragraph first,"
                        " bullet points for specifications, and any <img> tags at the end."
                    )}
                ],
                temperature=0.4,
            )
            cleaned_html = response.choices[0].message.content.strip()
            # Unescape HTML entities
            cleaned_html = unescape(cleaned_html)
            # Remove empty lists
            cleaned_html = collapse_empty_lists(cleaned_html)
            return cleaned_html

        except Exception as e:
            print(f"⚠️ API/network error: {e}\n→ Waiting {WAIT_TIMER} seconds before retry...")
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
        writer = csv.DictWriter(outfile, fieldnames=["filename", "name", "description", "clean_description"])
        if os.stat(OUTPUT_CSV).st_size == 0:
            writer.writeheader()

        start_processing = last_processed_file is None
        for row in reader:
            filename = row["filename"].strip()
            title = row["name"].strip()
            raw_description = (row.get("description") or "").strip()

            # Skip until we reach resume point
            if not start_processing:
                if filename == last_processed_file:
                    start_processing = True
                continue

            # Pre-clean the description
            cleaned_input_desc = pre_clean_description(raw_description)

            # GPT cleanup
            final_cleaned_description = gpt_generate_clean_description(title, cleaned_input_desc)

            # Write to CSV
            writer.writerow({
                "filename": filename,
                "name": title,
                "description": raw_description,
                "clean_description": final_cleaned_description
            })
            outfile.flush()

            # Update pickup file
            with open(PICKUP_TEXT_FILE, "w", encoding="utf-8") as f:
                f.write(filename)

            print(f"✅ Processed: {filename}")
            time.sleep(SLEEP_BETWEEN_CALLS)

    print("🎉 All descriptions processed successfully.")

if __name__ == "__main__":
    main()
