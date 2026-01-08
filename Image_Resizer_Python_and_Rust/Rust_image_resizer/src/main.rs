mod config;
mod filesystem;
mod images;
mod logger;

use config::*;
use filesystem::*;
use images::*;
use logger::Logger;
use image::DynamicImage;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Ensure output folder exists
    ensure_folder_exists(OUTPUT_FOLDER)?;

    // Open skipped log
    let mut log = Logger::new(OUTPUT_FOLDER, SKIPPED_LOG_FILE)?;

    // Get list of .tif files
    let tif_files = list_tif_files(WATCH_FOLDER)?;
    for path in tif_files {
        println!("Processing file: {}", path.display());
        let img: DynamicImage = image::open(&path)?;
        let base_name = path.file_stem().unwrap().to_string_lossy();

        // Iterate all resize settings
        for &(width, height, dpi) in RESIZE_SETTINGS {
            if let Ok(result) =
                resize_and_save(&img, &base_name, width, height, dpi, OUTPUT_FOLDER, MAX_SIZE_MB)
            {
                // If the file was skipped, log and print
                if let Some(skipped) = result {
                    log.log(&skipped)?;
                    eprintln!("⚠️ Skipped {}", skipped);
                }
            }
        }
    }

    // Final messages
    println!("✅ Done: Resized images saved to {}", OUTPUT_FOLDER);
    println!("📝 Skipped files logged in {}", SKIPPED_LOG_FILE);

    Ok(())
}
