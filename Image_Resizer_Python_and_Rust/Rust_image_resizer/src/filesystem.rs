use std::fs;
use std::path::PathBuf;

pub fn list_tif_files(folder: &str) -> std::io::Result<Vec<PathBuf>> {
    let mut files = Vec::new();
    for entry in fs::read_dir(folder)? {
        let entry = entry?;
        let path = entry.path();
        if let Some(ext) = path.extension() {
            if ext.to_string_lossy().eq_ignore_ascii_case("tif") {
                files.push(path);
            }
        }
    }
    Ok(files)
}

pub fn ensure_folder_exists(folder: &str) -> std::io::Result<()> {
    fs::create_dir_all(folder)?;
    Ok(())
}
