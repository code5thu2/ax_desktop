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

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct AuthUser {
    pub id: u64,
    pub name: String,
    pub email: String,
    #[serde(default)]
    #[ts(optional)]
    pub avatar: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct AuthTokens {
    pub access_token: String,
    pub refresh_token: String,
    #[serde(default)]
    #[ts(optional)]
    pub user: Option<AuthUser>,
    #[serde(default)]
    #[ts(optional)]
    pub updated_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct InstalledPlugin {
    pub id: u64,
    pub name: String,
    pub version: u32,
    pub enabled: bool,
    pub installed_at: String,
    pub scope: String, // "global" | "project"
    #[serde(default)]
    #[ts(optional)]
    pub project_path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct SkillFileItem {
    pub id: u64,
    pub file_name: String,
    pub file_size: u64,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct SkillItem {
    pub id: u64,
    pub name: String,
    pub description: String,
    pub creator_name: String,
    pub created_at: String,
    pub status: String,
    pub scope: String,
    pub categories: Vec<String>,
    pub stages: Vec<String>,
    pub view_count: u64,
    #[serde(default)]
    #[ts(optional)]
    pub avg_rating: Option<f64>,
    pub rating_count: u64,
    pub subscribed: bool,
    pub installed: bool,
    pub enabled: bool,
    #[serde(default)]
    #[ts(optional)]
    pub install_scope: Option<String>,
    #[serde(default)]
    pub installed_projects: Vec<String>,
    #[serde(default)]
    pub project_states: HashMap<String, bool>,
    #[serde(default)]
    #[ts(optional)]
    pub install_path: Option<String>,
    #[serde(default)]
    #[ts(optional)]
    pub installed_version: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct SkillDetail {
    pub id: u64,
    pub name: String,
    pub description: String,
    pub creator_name: String,
    pub created_at: String,
    pub status: String,
    pub scope: String,
    pub categories: Vec<String>,
    pub stages: Vec<String>,
    pub view_count: u64,
    #[serde(default)]
    #[ts(optional)]
    pub avg_rating: Option<f64>,
    pub rating_count: u64,
    pub subscribed: bool,
    pub installed: bool,
    pub enabled: bool,
    #[serde(default)]
    #[ts(optional)]
    pub install_scope: Option<String>,
    #[serde(default)]
    pub installed_projects: Vec<String>,
    #[serde(default)]
    pub project_states: HashMap<String, bool>,
    #[serde(default)]
    #[ts(optional)]
    pub install_path: Option<String>,
    #[serde(default)]
    #[ts(optional)]
    pub installed_version: Option<u32>,
    pub version: u32,
    pub hashtags: Vec<String>,
    pub files: Vec<SkillFileItem>,
    pub is_creator: bool,
    pub can_edit: bool,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct SkillVersionItem {
    pub version: u32,
    pub name: String,
    pub description: String,
    pub public_scope: String,
    pub hashtags: Vec<String>,
    pub creator_name: String,
    pub created_at: String,
    pub files: Vec<SkillFileItem>,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct PortalStatus {
    pub logged_in: bool,
    #[serde(default)]
    #[ts(optional)]
    pub user: Option<AuthUser>,
    pub theme: String,
    pub installed: Vec<InstalledPlugin>,
    pub recent_projects: Vec<String>,
    #[serde(default)]
    #[ts(optional)]
    pub remembered_email: Option<String>,
    pub remember_account: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct Settings {
    pub theme: String,
    pub recent_projects: Vec<String>,
    #[serde(default)]
    #[ts(optional)]
    pub remembered_email: Option<String>,
    pub remember_account: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct GithubAsset {
    pub name: String,
    #[serde(alias = "browser_download_url")]
    pub browser_download_url: String,
    pub size: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct GithubRelease {
    #[serde(alias = "tag_name")]
    pub tag_name: String,
    #[serde(default)]
    #[ts(optional)]
    pub name: Option<String>,
    #[serde(default)]
    #[ts(optional)]
    pub body: Option<String>,
    #[serde(default)]
    pub prerelease: bool,
    #[serde(default, alias = "published_at")]
    #[ts(optional)]
    pub published_at: Option<String>,
    #[serde(default)]
    pub assets: Vec<GithubAsset>,
}
