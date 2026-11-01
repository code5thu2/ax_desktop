use serde::de::DeserializeOwned;
use serde::Serialize;
use std::fs::{self, File};
use std::io::{self, Cursor, Read, Write};
use std::path::{Path, PathBuf};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AxStorageError {
    #[error("IO error: {0}")]
    Io(#[from] io::Error),
    #[error("Serialization error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("Zip extraction error: {0}")]
    Zip(#[from] zip::result::ZipError),
    #[error("Security violation: Zip slip detected in path '{0}'")]
    ZipSlip(String),
}

/// Normalizes file paths according to AX Desktop behavior specification:
/// - Replaces backslashes with forward slashes
/// - Collapses redundant slashes
/// - Strips trailing slashes
pub fn normalize_path(raw: &str) -> String {
    let trimmed = raw.trim();
    let mut normalized = trimmed.replace('\\', "/");
    while normalized.contains("//") {
        normalized = normalized.replace("//", "/");
    }
    while normalized.ends_with('/') && normalized.len() > 3 {
        normalized.pop();
    }
    normalized
}

/// Atomically writes serializable object to a JSON file:
/// 1. Creates parent directory if missing.
/// 2. If target file exists, backs it up to <path>.bak.
/// 3. Writes payload to <path>.tmp and flushes.
/// 4. Atomically replaces target with .tmp file (with retry for Windows file locks).
pub fn write_json_atomic<T: Serialize>(path: &Path, value: &T) -> Result<(), AxStorageError> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }

    let bak_path = PathBuf::from(format!("{}.bak", path.to_string_lossy()));
    if path.exists() {
        let _ = fs::copy(path, &bak_path);
    }

    let tmp_path = PathBuf::from(format!("{}.tmp", path.to_string_lossy()));
    {
        let mut file = File::create(&tmp_path)?;
        let json_data = serde_json::to_string_pretty(value)?;
        file.write_all(json_data.as_bytes())?;
        file.sync_all()?;
    }

    let mut last_err = None;
    for _ in 0..5 {
        match fs::rename(&tmp_path, path) {
            Ok(_) => {
                last_err = None;
                break;
            }
            Err(e) => {
                last_err = Some(e);
                std::thread::sleep(std::time::Duration::from_millis(50));
            }
        }
    }

    if let Some(e) = last_err {
        let _ = fs::copy(&tmp_path, path);
        let _ = fs::remove_file(&tmp_path);
        return Err(AxStorageError::Io(e));
    }

    Ok(())
}

/// Safely reads and deserializes JSON from file, falling back to .bak if primary is corrupted or missing.
pub fn read_json_safe<T: DeserializeOwned>(path: &Path) -> Option<T> {
    if path.exists() {
        if let Ok(content) = fs::read_to_string(path) {
            if let Ok(val) = serde_json::from_str::<T>(&content) {
                return Some(val);
            }
        }
    }

    let bak_path = PathBuf::from(format!("{}.bak", path.to_string_lossy()));
    if bak_path.exists() {
        if let Ok(content) = fs::read_to_string(&bak_path) {
            if let Ok(val) = serde_json::from_str::<T>(&content) {
                return Some(val);
            }
        }
    }

    None
}

/// Safely extracts zip bytes into target directory with strict Zip-slip protection.
pub fn extract_zip_safe(zip_bytes: &[u8], dest_dir: &Path) -> Result<(), AxStorageError> {
    fs::create_dir_all(dest_dir)?;
    let canonical_dest = fs::canonicalize(dest_dir)?;

    let mut archive = zip::ZipArchive::new(Cursor::new(zip_bytes))?;

    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        let raw_name = file.name().replace('\\', "/");

        if raw_name.contains("..") || raw_name.starts_with('/') || (raw_name.len() > 1 && raw_name.chars().nth(1) == Some(':')) {
            return Err(AxStorageError::ZipSlip(raw_name));
        }

        let outpath = dest_dir.join(&raw_name);

        if file.is_dir() {
            fs::create_dir_all(&outpath)?;
        } else {
            if let Some(p) = outpath.parent() {
                fs::create_dir_all(p)?;
            }
            let mut outfile = File::create(&outpath)?;
            let mut buffer = Vec::new();
            file.read_to_end(&mut buffer)?;
            outfile.write_all(&buffer)?;
        }

        let canonical_out = fs::canonicalize(&outpath).unwrap_or(outpath);
        if !canonical_out.starts_with(&canonical_dest) {
            return Err(AxStorageError::ZipSlip(raw_name));
        }
    }

    Ok(())
}
