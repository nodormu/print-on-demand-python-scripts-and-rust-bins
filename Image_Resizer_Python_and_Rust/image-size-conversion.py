import os
from PIL import Image

WATCH_FOLDER = "/home/invent/watch/"
OUTPUT_FOLDER = "/home/invent/file-outputs/"
SKIPPED_LOG = os.path.join(OUTPUT_FOLDER, "skipped_files.txt")
MAX_SIZE_MB = 100
#Towels, Polycotton Face and Hand Towels are duped in bathroom stuff script or kitchen stuff script, but file names are identical on W H DPI
#Pillow>10.0.0 is the only python package needed for this script to work
#In order for the resizing to product good images for you, I recommend you start with a larger image file than your largest image required at 600 DPI, scaling does not become pixelated
RESIZE_SETTINGS = [
    (4725, 9225, 150), #Polycotton Towel Small 30x60
    (5625, 11025, 150), #Polycotton Towel Large 36x72
    (7238, 3638, 150), #Youth Hooded Towel
    (18900, 9900, 300), #Beach Towel Horizontal Template 60x30, but printify calls it 30x60
    (3630, 5730, 300), #Rally Towel 11x18
    (4800, 9300, 150), #Mink Cotton Towel 30x60
    (3600, 4800, 150), #Tea Towel 28x28
    (4500, 4500, 300), #Face Towel 13x13
    (5693, 9154, 300), #Hand Towel 16x28
    (5374, 8102, 300), #Beach Towel 18x27
    (7163, 13205, 300), #Beach Towel 24x44
    (9579, 18390, 300), #Beach Towel Vertical Template 30x60
    (3000, 4800, 150), #Tea Towels Cotton Poly 18x30
    (5043, 7350, 300), #Golf Towel 16x24
    (6000, 12450, 150) #Boho Beach Cloth
]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def is_file_too_large(path):
    size_mb = os.path.getsize(path) / (1024 * 1024)
    return size_mb > MAX_SIZE_MB

with open(SKIPPED_LOG, "w") as skipped_log:
    for filename in os.listdir(WATCH_FOLDER):
        if filename.lower().endswith(".tif"): #this can be substituted with .webp, .jpg, .png, no vector files such as svg's, just 2D images only.
            input_path = os.path.join(WATCH_FOLDER, filename)
            base_name = os.path.splitext(filename)[0]

            with Image.open(input_path) as img:
                for width, height, dpi in RESIZE_SETTINGS:
                    resized = img.resize((width, height), Image.LANCZOS)
                    resized.info['dpi'] = (dpi, dpi)
                    out_name = f"{base_name}_{width}x{height}_{dpi}dpi.png"
                    out_path = os.path.join(OUTPUT_FOLDER, out_name)

                    # Save with no compression
                    resized.save(out_path, format="PNG", compress_level=0)

                    # Check file size
                    if is_file_too_large(out_path):
                        # Try saving again with high compression
                        resized.save(out_path, format="PNG", compress_level=2)

                        # Re-check file size
                        if is_file_too_large(out_path):
                            os.remove(out_path)
                            skipped_log.write(out_name + "\n")
                            print(f"⚠️ Skipped {out_name}: file still too large after compression.")

print("✅ Done: Converted and saved images to", OUTPUT_FOLDER)
print("📝 Skipped files logged in:", SKIPPED_LOG)
