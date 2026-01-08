use image::{imageops::FilterType, RgbaImage};
use png::{Encoder, Compression, ColorType};
use std::fs;
use std::path::Path;
use std::fs::File;

pub fn resize_and_save(
    img: &image::DynamicImage,
    base_name: &str,
    width: u32,
    height: u32,
    dpi: u32,
    output_folder: &str,
    max_size_mb: f64,
) -> Result<Option<String>, Box<dyn std::error::Error>> {
    let resized = img.resize_exact(width, height, FilterType::Lanczos3);
    let out_name = format!("{}_{}x{}_{}dpi.png", base_name, width, height, dpi);
    let out_path = Path::new(output_folder).join(&out_name);

    let buffer: RgbaImage = resized.to_rgba8();
    let w = buffer.width();
    let h = buffer.height();

    // First save: low compression
    save_png_with_compression(&out_path, &buffer, w, h, Compression::Fast)?;

    // Check file size
    let size_mb = fs::metadata(&out_path)?.len() as f64 / (1024.0 * 1024.0);
    if size_mb > max_size_mb {
        // Retry with high compression
        save_png_with_compression(&out_path, &buffer, w, h, Compression::Best)?;

        let size_mb2 = fs::metadata(&out_path)?.len() as f64 / (1024.0 * 1024.0);
        if size_mb2 > max_size_mb {
            fs::remove_file(&out_path)?;
            return Ok(Some(out_name)); // skipped file
        }
    }

    Ok(None)
}

fn save_png_with_compression(
    path: &Path,
    buffer: &RgbaImage,
    width: u32,
    height: u32,
    compression: Compression,
) -> Result<(), Box<dyn std::error::Error>> {
    let file = File::create(path)?;
    let mut encoder = Encoder::new(file, width, height);
    encoder.set_compression(compression);
    encoder.set_color(ColorType::Rgba);
    encoder.set_depth(png::BitDepth::Eight);

    let mut writer = encoder.write_header()?;
    writer.write_image_data(buffer)?;
    Ok(())
}
