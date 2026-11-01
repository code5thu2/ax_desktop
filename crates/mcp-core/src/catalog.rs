use serde::{Deserialize, Serialize};
use shared_types::models::PluginItem;
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RawCatalog {
    pub version: Option<String>,
    #[serde(default)]
    pub servers: Vec<PluginItem>,
}

#[derive(Debug, Clone)]
pub struct CatalogManager {
    servers: Vec<PluginItem>,
}

impl CatalogManager {
    pub fn from_json_str(json_str: &str) -> Result<Self, String> {
        let raw: RawCatalog = serde_json::from_str(json_str).map_err(|e| e.to_string())?;
        Ok(Self {
            servers: raw.servers,
        })
    }

    pub fn load_from_file(path: &Path) -> Result<Self, String> {
        if !path.exists() {
            return Ok(Self { servers: vec![] });
        }
        let content = fs::read_to_string(path).map_err(|e| e.to_string())?;
        Self::from_json_str(&content)
    }

    pub fn list(&self) -> &[PluginItem] {
        &self.servers
    }

    pub fn get(&self, server_id: &str) -> Option<&PluginItem> {
        self.servers.iter().find(|s| s.id == server_id)
    }

    pub fn search(&self, query: &str, category: Option<&str>) -> Vec<PluginItem> {
        let q = query.trim().to_lowercase();
        let cat_opt = category.map(|c| c.trim().to_lowercase());

        self.servers
            .iter()
            .filter(|item| {
                let matches_cat = match &cat_opt {
                    Some(cat) if !cat.is_empty() => {
                        item.category.as_ref().map(|c| c.to_lowercase() == *cat).unwrap_or(false)
                    }
                    _ => true,
                };

                if !matches_cat {
                    return false;
                }

                if q.is_empty() {
                    return true;
                }

                let in_id = item.id.to_lowercase().contains(&q);
                let in_name = item.name.to_lowercase().contains(&q);
                let in_summary = item.summary.to_lowercase().contains(&q);
                let in_tools = item
                    .tools
                    .as_ref()
                    .map(|tools| tools.iter().any(|t| t.name.to_lowercase().contains(&q)))
                    .unwrap_or(false);

                in_id || in_name || in_summary || in_tools
            })
            .cloned()
            .collect()
    }
}
