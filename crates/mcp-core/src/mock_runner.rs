use shared_types::models::{PluginItem, PluginTool};
use std::fs;
use std::path::Path;

pub struct MockServerScanner;

impl MockServerScanner {
    /// Scans an external directory (outside of this repository) to discover mock servers.
    /// Checks for manifest.json in each child directory.
    pub fn scan_external_dir(dir: &Path) -> Vec<PluginItem> {
        let mut results = Vec::new();
        if !dir.exists() || !dir.is_dir() {
            return results;
        }

        let entries = match fs::read_dir(dir) {
            Ok(e) => e,
            Err(_) => return results,
        };

        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let manifest_path = path.join("manifest.json");
                if manifest_path.exists() {
                    if let Ok(content) = fs::read_to_string(&manifest_path) {
                        if let Ok(mut item) = serde_json::from_str::<PluginItem>(&content) {
                            item.install_path = Some(path.to_string_lossy().to_string());
                            results.push(item);
                            continue;
                        }

                        // Try partial JSON with fallback defaults
                        if let Ok(val) = serde_json::from_str::<serde_json::Value>(&content) {
                            let id = val["id"].as_str().unwrap_or("unknown_mock").to_string();
                            let name = val["name"].as_str().unwrap_or(&id).to_string();
                            let summary = val["summary"].as_str().unwrap_or("External Mock MCP").to_string();
                            let tools: Vec<PluginTool> = val["tools"]
                                .as_array()
                                .map(|arr| {
                                    arr.iter()
                                        .filter_map(|t| {
                                            let name = t["name"].as_str()?.to_string();
                                            let desc = t["description"].as_str().unwrap_or("").to_string();
                                            Some(PluginTool {
                                                name,
                                                description: desc,
                                                parameters: None,
                                            })
                                        })
                                        .collect()
                                })
                                .unwrap_or_default();

                            results.push(PluginItem {
                                id,
                                name,
                                item_type: "mcp".to_string(),
                                vendor: "External Mock".to_string(),
                                version: "1.0.0".to_string(),
                                icon: "pi pi-box".to_string(),
                                rating: 5.0,
                                downloads: "Mock".to_string(),
                                summary,
                                description: "Mock server running outside repository".to_string(),
                                features: vec!["Mock Testing".to_string()],
                                installed: true,
                                enabled: true,
                                install_path: Some(path.to_string_lossy().to_string()),
                                tools: Some(tools),
                                change_notes: None,
                                category: Some("Mock Tools".to_string()),
                                runtime: Some("python".to_string()),
                                download_url: None,
                                env_requirements: None,
                                configured_env: None,
                            });
                        }
                    }
                }
            }
        }

        results
    }
}
