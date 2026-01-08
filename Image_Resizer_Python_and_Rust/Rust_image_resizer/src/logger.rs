use std::fs::OpenOptions;
use std::io::Write;
use std::path::Path;

pub struct Logger {
    file: std::fs::File,
}

impl Logger {
    pub fn new(folder: &str, filename: &str) -> std::io::Result<Self> {
        let path = Path::new(folder).join(filename);
        let file = OpenOptions::new()
            .append(true)
            .create(true)
            .open(path)?;
        Ok(Self { file })
    }

    pub fn log(&mut self, message: &str) -> std::io::Result<()> {
        writeln!(self.file, "{}", message)?;
        Ok(())
    }
}
