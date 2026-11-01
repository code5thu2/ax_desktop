use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use ts_rs::TS;

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct PluginEnvRequirement {
    pub key: String,
    pub label: String,
    #[serde(default)]
    #[ts(optional)]
    pub required: Option<bool>,
    #[serde(default)]
    #[ts(optional)]
    pub default: Option<String>,
    #[serde(rename = "type", default)]
    #[ts(optional)]
    pub field_type: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct PluginTool {
    pub name: String,
    pub description: String,
    #[serde(default)]
    #[ts(optional, type = "any")]
    pub parameters: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct PluginItem {
    pub id: String,
    pub name: String,
    #[serde(rename = "type")]
    pub item_type: String,
    pub vendor: String,
    pub version: String,
    pub icon: String,
    pub rating: f64,
    pub downloads: String,
    pub summary: String,
    pub description: String,
    pub features: Vec<String>,
    pub installed: bool,
    pub enabled: bool,
    #[serde(default)]
    #[ts(optional)]
    pub install_path: Option<String>,
    #[serde(default)]
    #[ts(optional)]
    pub tools: Option<Vec<PluginTool>>,
    #[serde(default)]
    #[ts(optional)]
    pub change_notes: Option<String>,
    #[serde(default)]
    #[ts(optional)]
    pub category: Option<String>,
    #[serde(default)]
    #[ts(optional)]
    pub runtime: Option<String>,
    #[serde(default)]
    #[ts(optional)]
    pub download_url: Option<String>,
    #[serde(default)]
    #[ts(optional)]
    pub env_requirements: Option<Vec<PluginEnvRequirement>>,
    #[serde(default)]
    #[ts(optional)]
    pub configured_env: Option<HashMap<String, String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct CatalogResponse {
    pub total: usize,
    pub servers: Vec<PluginItem>,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct ToolExecuteRequest {
    pub tool_name: String,
    #[ts(type = "any")]
    pub arguments: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct ToolExecuteResponse {
    pub ok: bool,
    pub tool: String,
    #[ts(type = "any")]
    pub result: serde_json::Value,
}
