use crate::storage::{read_json_safe, write_json_atomic};
use serde_json::{json, Value};
use std::fs;
use std::io::Read;
use std::path::Path;

/// Reads skill name from YAML frontmatter in SKILL.md (reads first 4KB).
/// If frontmatter name is missing, falls back to directory name.
pub fn read_skill_name_from_md(skill_dir: &Path) -> String {
    let skill_md_path = skill_dir.join("SKILL.md");
    if skill_md_path.exists() {
        if let Ok(mut file) = fs::File::open(&skill_md_path) {
            let mut buf = [0u8; 4096];
            if let Ok(bytes_read) = file.read(&mut buf) {
                let content = String::from_utf8_lossy(&buf[..bytes_read]);
                if content.starts_with("---") {
                    let parts: Vec<&str> = content.split("---").collect();
                    if parts.len() >= 3 {
                        let yaml_block = parts[1];
                        for line in yaml_block.lines() {
                            let trimmed = line.trim();
                            if trimmed.starts_with("name:") {
                                let val = trimmed["name:".len()..].trim();
                                let clean = val.trim_matches('"').trim_matches('\'').trim();
                                if !clean.is_empty() {
                                    return clean.to_string();
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    skill_dir
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("unknown-skill")
        .to_string()
}

/// Synchronizes a skill's disabled state into an AIPRO Studio config.json file
pub fn sync_disabled_skills(config_path: &Path, skill_name: &str, disabled: bool) -> Result<(), String> {
    let mut config: Value = read_json_safe(config_path).unwrap_or_else(|| json!({}));

    if !config.is_object() {
        config = json!({});
    }

    let mut disabled_list: Vec<String> = config
        .get("disabledSkills")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|item| item.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();

    if disabled {
        if !disabled_list.contains(&skill_name.to_string()) {
            disabled_list.push(skill_name.to_string());
        }
    } else {
        disabled_list.retain(|item| item != skill_name);
    }

    if disabled_list.is_empty() {
        if let Some(obj) = config.as_object_mut() {
            obj.remove("disabledSkills");
        }
    } else {
        config["disabledSkills"] = json!(disabled_list);
    }

    write_json_atomic(config_path, &config).map_err(|e| e.to_string())
}
