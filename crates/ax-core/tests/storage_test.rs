use ax_core::storage::{normalize_path, read_json_safe, write_json_atomic, extract_zip_safe};
use serde::{Deserialize, Serialize};
use std::io::Write;
use tempfile::tempdir;
use zip::write::SimpleFileOptions;

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
struct SampleConfig {
    name: String,
    counter: u32,
}

#[test]
fn test_normalize_path() {
    assert_eq!(normalize_path("C:\\Users\\dev\\project\\"), "C:/Users/dev/project");
    assert_eq!(normalize_path("  D:/code/my_app/  "), "D:/code/my_app");
    assert_eq!(normalize_path("folder\\\\subfolder\\\\"), "folder/subfolder");
}

#[test]
fn test_atomic_write_and_read() {
    let dir = tempdir().unwrap();
    let file_path = dir.path().join("config.json");

    let val1 = SampleConfig {
        name: "First".to_string(),
        counter: 1,
    };
    write_json_atomic(&file_path, &val1).expect("Failed write 1");
    let loaded: Option<SampleConfig> = read_json_safe(&file_path);
    assert_eq!(loaded, Some(val1.clone()));

    // Second write creates .bak
    let val2 = SampleConfig {
        name: "Second".to_string(),
        counter: 2,
    };
    write_json_atomic(&file_path, &val2).expect("Failed write 2");
    let loaded2: Option<SampleConfig> = read_json_safe(&file_path);
    assert_eq!(loaded2, Some(val2));

    let bak_path = dir.path().join("config.json.bak");
    assert!(bak_path.exists());
    let loaded_bak: Option<SampleConfig> = read_json_safe(&bak_path);
    assert_eq!(loaded_bak, Some(val1));
}

#[test]
fn test_safe_zip_extraction_valid() {
    let dir = tempdir().unwrap();
    let dest = dir.path().join("out");

    let mut buf = Vec::new();
    {
        let mut zip = zip::ZipWriter::new(std::io::Cursor::new(&mut buf));
        zip.start_file("SKILL.md", SimpleFileOptions::default()).unwrap();
        zip.write_all(b"---\nname: my-skill\n---\nHello").unwrap();
        zip.finish().unwrap();
    }

    extract_zip_safe(&buf, &dest).expect("Should extract valid zip");
    let extracted_skill = dest.join("SKILL.md");
    assert!(extracted_skill.exists());
    let content = std::fs::read_to_string(extracted_skill).unwrap();
    assert!(content.contains("name: my-skill"));
}

#[test]
fn test_safe_zip_extraction_rejects_zip_slip() {
    let dir = tempdir().unwrap();
    let dest = dir.path().join("out");

    let mut buf = Vec::new();
    {
        let mut zip = zip::ZipWriter::new(std::io::Cursor::new(&mut buf));
        zip.start_file("../outside.txt", SimpleFileOptions::default()).unwrap();
        zip.write_all(b"Hacked").unwrap();
        zip.finish().unwrap();
    }

    let result = extract_zip_safe(&buf, &dest);
    assert!(result.is_err(), "Must reject Zip-slip attempt");
}
