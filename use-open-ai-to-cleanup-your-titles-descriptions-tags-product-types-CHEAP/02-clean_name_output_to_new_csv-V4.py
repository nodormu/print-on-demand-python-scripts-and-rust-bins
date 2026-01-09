# === Final Version: CSV Normalizer with Polished Cleanup, JSON-Safe Escaping, and Clean Numeric Ranges ===
import csv
import re
import time
import openai
import os

# === Immutable Variables ===
INPUT_CSV: str = "name_cleanup_prep.csv"
OUTPUT_CSV: str = "cleaned_name_outputs.csv"
MAX_INPUT_LENGTH = 250  # read at most 250 chars, or change accordingly for your product title/name
MAX_TITLE_LENGTH = 90   # final title limit, or change accordingly for your product title/name

OPENAI_API_KEY: str = "sk-proj-LONGSTRINGHERE" # Replace LONGSTRINGHERE with whatever is in your OpenAI account
OPENAI_ORG_ID: str = "org-SHORTSTRINGHERE" # Replace SHORTSTRINGHERE with whatever is in your OpenAI account
OPENAI_ENGINE: str = "gpt-3.5-turbo"

WAIT_TIMER = 600 # if you hit a 429 due to hitting request limitations, it will auto sleep for 600 seconds and pick back up where it left off
PICKUP_TEXT_FILE = "last_attempted_tags_product_type_completed_successfully.txt" # this is a failsafe in case your script fails, or you hit 429 or need to just break out of it, and still pick up where you left off
SLEEP_BETWEEN_CALLS = 1 # seconds, in order to play friendly with openAI's platform and not get your account block for pounding their servers with too many requests

# === OpenAI Setup ===
openai.api_key = OPENAI_API_KEY
if OPENAI_ORG_ID:
    openai.organization = OPENAI_ORG_ID

# === Helper Functions ===
def truncate_input(name: str, max_length: int) -> str:
    """Truncate input without cutting words."""
    if len(name) <= max_length:
        return name
    truncated = name[:max_length].rsplit(" ", 1)[0]
    return truncated.strip()

def clean_title(title: str) -> str:
    """Comprehensive cleanup, JSON-safe, and clean numeric ranges."""
    # Remove gendered terms
    title = re.sub(r'\b(teen boy|teen girl|boys|girls|boy|girl)\b', '', title, flags=re.I)  # pay attention to this string and substitute as you see fit depending on your product
    title = re.sub(r'\s{2,}', ' ', title).strip()

    # Remove duplicated keywords
    title = re.sub(
        r'\b(Bedspread Coverlet Bedding|Quilt Bedding Set|Bedspread Coverlet|Bedspread|Coverlet|Bedding)\b', #pay attention to this string and substitute as you see fit depending on your product name/titles listings
        lambda m: m.group(0).split()[0],
        title,
        flags=re.I
    )

    # Normalize quotes
    title = title.replace('""', '"')

    # Fix fractions: ensure space before units (e.g., 5/8cm → 5/8 cm)
    title = re.sub(r'(\d+/\d+)([a-zA-Z]+)', r'\1 \2', title)

    # --- Clean numeric ranges ---
    # Convert 14x14/15*15/12*12 → 14x14, 15x15, 12x12
    def normalize_range(match):
        parts = re.split(r'[/\*]', match.group(0))
        cleaned_parts = [p.replace(' ', '').replace('X', 'x') for p in parts]
        return ', '.join(cleaned_parts)

    title = re.sub(r'(\d+\s*[xX]\s*\d+(?:[/\*]\s*\d+\s*[xX]\s*\d+)+)', normalize_range, title)

    # Remove trailing punctuation
    title = re.sub(r"[-–/:;,.\s]+$", "", title)

    # Enforce consistent title casing
    title = " ".join(word.capitalize() if not word.isupper() else word for word in title.split())

    # Clean spacing and punctuation
    title = re.sub(r"\s{2,}", " ", title)
    title = re.sub(r"\s+([,.:;!?])", r"\1", title)

    # JSON-safe escape
    title = title.replace('"', r'\"')

    return title.strip()

# === Main Script ===
last_processed_file = None
if os.path.exists(PICKUP_TEXT_FILE):
    with open(PICKUP_TEXT_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content:
            last_processed_file = content

# Open CSVs
with open(INPUT_CSV, "r", encoding="utf-8", newline="") as infile, \
     open(OUTPUT_CSV, "a", encoding="utf-8", newline="") as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=["filename", "name", "clean_name"])

    # Write header if file is empty
    if os.stat(OUTPUT_CSV).st_size == 0:
        writer.writeheader()

    start_processing = last_processed_file is None
    for row in reader:
        filename = row["filename"]
        original_name = row["name"]

        # Resume logic only if last_processed_file is set
        if not start_processing:
            if filename == last_processed_file:
                start_processing = True
            continue  # skip until we reach last processed file

        # Smart truncate input
        input_name = truncate_input(original_name, MAX_INPUT_LENGTH)

        # Retry logic for API/network errors
        while True:
            try:
                response = openai.chat.completions.create(
                    model=OPENAI_ENGINE,
                    messages=[
                        {"role": "system", "content": (
                            "You are an expert e-commerce content editor."
                            " Rewrite product titles to be ultra-concise, professional, neutral."
                            " Avoid gendered terms unless present in the original."
                            " Collapse redundant descriptors into one clear term."
                            " Keep essential details: size, color, material, quantity."
                            " Prefer titles under 90 characters. Capitalize properly."
                            " Never invent details or output partial words."
                        )},
                        {"role": "user", "content": f"Normalize this product title: {input_name}"}
                    ],
                    temperature=0.4,
                )

                normalized_name = response.choices[0].message.content.strip()

                # Enforce MAX_TITLE_LENGTH
                if len(normalized_name) > MAX_TITLE_LENGTH:
                    normalized_name = normalized_name[:MAX_TITLE_LENGTH].rsplit(" ", 1)[0].strip()

                # Post-process
                normalized_name = clean_title(normalized_name)
                break  # success

            except Exception as e:
                print(f"API/network error: {e}. Backing off for {WAIT_TIMER} seconds...")
                time.sleep(WAIT_TIMER)

        # Write to output CSV
        writer.writerow({
            "filename": filename,
            "name": original_name,
            "clean_name": normalized_name
        })
        outfile.flush()

        # Update pickup file
        with open(PICKUP_TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(filename)

        print(f"Processed: {filename} -> {normalized_name}")
        time.sleep(SLEEP_BETWEEN_CALLS)

print("All titles processed successfully.")
