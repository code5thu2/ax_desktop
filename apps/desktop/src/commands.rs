use ax_core::client::AxClient;
use ax_core::skill_manager::SkillManager;
use ax_core::storage::{normalize_path, read_json_safe, write_json_atomic};
use ax_core::updater::check_github_release_available;
use mcp_core::catalog::CatalogManager;
use mcp_core::mock_runner::MockServerScanner;
use serde::Deserialize;
use shared_types::models::{
    AuthTokens, CatalogResponse, PluginItem, PortalStatus, Settings, SkillDetail,
    SkillVersionItem,
};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Mutex;
use tauri::{State, Window};

pub struct AppState {
    pub client: AxClient,
    pub skill_manager: SkillManager,
    pub appdata_dir: PathBuf,
    pub auth_path: PathBuf,
    pub settings_path: PathBuf,
    pub catalog_path: PathBuf,
    pub external_mock_dir: PathBuf,
    pub cached_catalog: Mutex<Option<CatalogManager>>,
}

impl AppState {
    pub fn new() -> Self {
        let root = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
        let catalog_path = root.join("storage").join("catalog.json");
        let external_mock_dir = std::env::var("MCP_SERVERS_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(|_| PathBuf::from("D:/AI_MCP/servers"));

        let appdata = std::env::var("APPDATA")
            .map(PathBuf::from)
            .unwrap_or_else(|_| root.join("storage"));
        let ax_dir = appdata.join("ax-desktop");
        let _ = std::fs::create_dir_all(&ax_dir);

        let user_profile = std::env::var("USERPROFILE")
            .map(PathBuf::from)
            .unwrap_or_else(|_| root.clone());
        let aipro_dir = user_profile.join(".aipro");
        let _ = std::fs::create_dir_all(aipro_dir.join("skills"));

        let auth_path = ax_dir.join("auth.json");
        let installed_path = ax_dir.join("installed.json");
        let settings_path = ax_dir.join("settings.json");
        let global_config = aipro_dir.join("config.json");

        let skill_mgr = SkillManager::new(
            aipro_dir.join("skills"),
            installed_path,
            global_config,
        );

        let client = AxClient::new(
            "http://ax-portal.gafc.vn/api/v1".to_string(),
            true, // Default to MockEngine offline mode for instant dev testing
        );

        Self {
            client,
            skill_manager: skill_mgr,
            appdata_dir: ax_dir,
            auth_path,
            settings_path,
            catalog_path,
            external_mock_dir,
            cached_catalog: Mutex::new(None),
        }
    }
}

// ==========================================
// 1. Auth IPC Commands
// ==========================================

#[derive(Deserialize)]
pub struct LoginPayload {
    pub email: String,
    pub password: String,
}

#[tauri::command]
pub fn login(state: State<'_, AppState>, payload: LoginPayload) -> Result<serde_json::Value, String> {
    let tokens = state.client.login(&payload.email, &payload.password)?;
    write_json_atomic(&state.auth_path, &tokens).map_err(|e| e.to_string())?;

    // Auto remember email if rememberAccount is enabled in settings
    let mut settings = read_json_safe::<Settings>(&state.settings_path).unwrap_or(Settings {
        theme: "dark".to_string(),
        recent_projects: vec![],
        remembered_email: None,
        remember_account: true,
    });
    if settings.remember_account {
        settings.remembered_email = Some(payload.email);
        let _ = write_json_atomic(&state.settings_path, &settings);
    }

    Ok(serde_json::json!({
        "ok": true,
        "user": tokens.user
    }))
}

#[tauri::command]
pub fn request_register_otp(state: State<'_, AppState>, email: String) -> Result<serde_json::Value, String> {
    state.client.request_otp(&email)?;
    Ok(serde_json::json!({ "ok": true }))
}

#[tauri::command]
pub fn verify_register_otp(state: State<'_, AppState>, email: String, otp: String) -> Result<serde_json::Value, String> {
    state.client.verify_otp(&email, &otp)?;
    Ok(serde_json::json!({ "ok": true }))
}

#[tauri::command]
pub fn register(state: State<'_, AppState>, payload: serde_json::Value) -> Result<serde_json::Value, String> {
    let email = payload.get("email").and_then(|v| v.as_str()).unwrap_or("user@example.com");
    let tokens = state.client.login(email, "secret")?;
    write_json_atomic(&state.auth_path, &tokens).map_err(|e| e.to_string())?;
    Ok(serde_json::json!({ "ok": true }))
}

#[tauri::command]
pub fn request_forgot_otp(state: State<'_, AppState>, email: String) -> Result<serde_json::Value, String> {
    state.client.request_otp(&email)?;
    Ok(serde_json::json!({ "ok": true }))
}

#[tauri::command]
pub fn verify_forgot_otp(state: State<'_, AppState>, email: String, otp: String) -> Result<serde_json::Value, String> {
    state.client.verify_otp(&email, &otp)?;
    Ok(serde_json::json!({ "ok": true }))
}

#[tauri::command]
pub fn reset_password(state: State<'_, AppState>, payload: serde_json::Value) -> Result<serde_json::Value, String> {
    let email = payload.get("email").and_then(|v| v.as_str()).unwrap_or("user@example.com");
    let tokens = state.client.login(email, "newpass")?;
    write_json_atomic(&state.auth_path, &tokens).map_err(|e| e.to_string())?;
    Ok(serde_json::json!({ "ok": true }))
}

#[tauri::command]
pub fn logout(state: State<'_, AppState>) -> Result<serde_json::Value, String> {
    if state.auth_path.exists() {
        let _ = std::fs::remove_file(&state.auth_path);
    }
    Ok(serde_json::json!({ "ok": true }))
}

// ==========================================
// 2. Status & Marketplace IPC Commands
// ==========================================

#[tauri::command]
pub fn get_status(state: State<'_, AppState>) -> PortalStatus {
    let auth = read_json_safe::<AuthTokens>(&state.auth_path);
    let settings = read_json_safe::<Settings>(&state.settings_path).unwrap_or(Settings {
        theme: "dark".to_string(),
        recent_projects: vec![],
        remembered_email: None,
        remember_account: true,
    });
    let installed = state.skill_manager.list_installed();

    PortalStatus {
        logged_in: auth.is_some(),
        user: auth.and_then(|a| a.user),
        theme: settings.theme,
        installed,
        recent_projects: settings.recent_projects,
        remembered_email: settings.remembered_email,
        remember_account: settings.remember_account,
    }
}

#[tauri::command]
pub fn fetch_skills(
    state: State<'_, AppState>,
    query: Option<String>,
    page: Option<usize>,
    page_size: Option<usize>,
) -> serde_json::Value {
    let p = page.unwrap_or(1);
    let ps = page_size.unwrap_or(40);
    let mut skills = state.client.fetch_skills(query.as_deref(), p, ps);

    // Merge local installed status
    let installed_list = state.skill_manager.list_installed();
    for s in skills.iter_mut() {
        let matched: Vec<_> = installed_list.iter().filter(|i| i.id == s.id).collect();
        if !matched.is_empty() {
            s.installed = true;
            s.enabled = matched.iter().any(|i| i.enabled);
            s.installed_projects = matched
                .iter()
                .filter_map(|i| i.project_path.clone())
                .collect();
            let mut pstates = HashMap::new();
            for m in matched {
                if let Some(ref p) = m.project_path {
                    pstates.insert(p.clone(), m.enabled);
                }
            }
            s.project_states = pstates;
        }
    }

    serde_json::json!({
        "items": skills,
        "totalCount": skills.len()
    })
}

#[tauri::command]
pub fn get_skill_detail(state: State<'_, AppState>, id: u64) -> Result<SkillDetail, String> {
    let mut detail = state.client.get_skill_detail(id)?;
    let installed_list = state.skill_manager.list_installed();
    let matched: Vec<_> = installed_list.iter().filter(|i| i.id == id).collect();

    if !matched.is_empty() {
        detail.installed = true;
        detail.enabled = matched.iter().any(|i| i.enabled);
        detail.installed_projects = matched
            .iter()
            .filter_map(|i| i.project_path.clone())
            .collect();
        let mut pstates = HashMap::new();
        for m in matched {
            if let Some(ref p) = m.project_path {
                pstates.insert(p.clone(), m.enabled);
            }
        }
        detail.project_states = pstates;
    }

    Ok(detail)
}

#[tauri::command]
pub fn get_skill_versions(state: State<'_, AppState>, id: u64) -> Vec<SkillVersionItem> {
    state.client.get_skill_versions(id)
}

// ==========================================
// 3. Skill Lifecycle Commands (Install/Uninstall/Toggle/Clone)
// ==========================================

#[derive(Deserialize)]
pub struct InstallSkillPayload {
    pub skill_id: u64,
    pub name: Option<String>,
    pub version: Option<u32>,
    pub scope: Option<String>,
    pub project_path: Option<String>,
}

#[tauri::command]
pub fn install(state: State<'_, AppState>, payload: InstallSkillPayload) -> Result<serde_json::Value, String> {
    let scope = payload.scope.as_deref().unwrap_or("global");
    let name = payload.name.as_deref().unwrap_or("custom-skill");
    let ver = payload.version.unwrap_or(1);

    let zip_bytes = state.client.download_skill_zip(payload.skill_id, name)?;
    let code = state.skill_manager.install(
        payload.skill_id,
        name,
        ver,
        scope,
        payload.project_path.as_deref(),
        &zip_bytes,
    )?;

    Ok(serde_json::json!({ "ok": true, "code": code }))
}

#[derive(Deserialize)]
pub struct UninstallSkillPayload {
    pub skill_id: u64,
    pub scope: Option<String>,
    pub project_path: Option<String>,
}

#[tauri::command]
pub fn uninstall(state: State<'_, AppState>, payload: UninstallSkillPayload) -> Result<serde_json::Value, String> {
    let scope = payload.scope.as_deref().unwrap_or("global");
    state.skill_manager.uninstall(
        payload.skill_id,
        scope,
        payload.project_path.as_deref(),
    )?;
    Ok(serde_json::json!({ "ok": true }))
}

#[derive(Deserialize)]
pub struct ToggleSkillPayload {
    pub skill_id: u64,
    pub enabled: bool,
    pub scope: Option<String>,
    pub project_path: Option<String>,
}

#[tauri::command]
pub fn toggle(state: State<'_, AppState>, payload: ToggleSkillPayload) -> Result<serde_json::Value, String> {
    let scope = payload.scope.as_deref().unwrap_or("global");
    state.skill_manager.toggle(
        payload.skill_id,
        payload.enabled,
        scope,
        payload.project_path.as_deref(),
    )?;
    Ok(serde_json::json!({ "ok": true }))
}

#[derive(Deserialize)]
pub struct CloneSkillPayload {
    pub skill_id: u64,
    pub source_project_path: String,
    pub target_project_path: String,
}

#[tauri::command]
pub fn clone_skill(state: State<'_, AppState>, payload: CloneSkillPayload) -> Result<serde_json::Value, String> {
    state.skill_manager.clone_skill(
        payload.skill_id,
        &payload.source_project_path,
        &payload.target_project_path,
    )?;
    Ok(serde_json::json!({ "ok": true }))
}

// ==========================================
// 4. System & Integration Commands
// ==========================================

#[tauri::command]
pub fn open_studio() -> Result<serde_json::Value, String> {
    win11_platform::studio_launcher::launch_aipro_studio()
        .map(|_| serde_json::json!({ "ok": true }))
        .map_err(|e| e)
}

#[tauri::command]
pub fn select_folder() -> Result<serde_json::Value, String> {
    // Open Windows native FolderBrowserDialog via PowerShell
    let output = std::process::Command::new("powershell")
        .args([
            "-NoProfile",
            "-Command",
            "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description = 'Chọn thư mục dự án'; if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $d.SelectedPath }",
        ])
        .output()
        .map_err(|e| format!("Folder picker failed: {}", e))?;

    let path_str = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if path_str.is_empty() {
        Ok(serde_json::json!({ "ok": false, "cancelled": true }))
    } else {
        Ok(serde_json::json!({ "ok": true, "path": normalize_path(&path_str) }))
    }
}

#[tauri::command]
pub async fn check_for_update() -> Result<serde_json::Value, String> {
    let releases = ax_core::updater::fetch_github_releases("code5thu2/ax_desktop").await
        .unwrap_or_default();

    let update = check_github_release_available(&releases, "1.0.0");
    match update {
        Some(rel) => Ok(serde_json::json!({
            "status": "success",
            "updateAvailable": true,
            "latestVersion": rel.tag_name,
            "currentVersion": "1.0.0",
            "downloadUrl": rel.assets.first().map(|a| a.browser_download_url.clone())
        })),
        None => Ok(serde_json::json!({
            "status": "success",
            "updateAvailable": false,
            "currentVersion": "1.0.0"
        })),
    }
}

#[tauri::command]
pub fn set_theme(window: Window, state: State<'_, AppState>, theme: String) -> Result<(), String> {
    let is_dark = theme == "dark" || theme == "system";
    #[cfg(target_os = "windows")]
    {
        if let Ok(hwnd) = window.hwnd() {
            let _ = win11_platform::dwm::apply_dark_titlebar(hwnd.0 as isize, is_dark);
        }
    }

    let mut settings = read_json_safe::<Settings>(&state.settings_path).unwrap_or(Settings {
        theme: "dark".to_string(),
        recent_projects: vec![],
        remembered_email: None,
        remember_account: true,
    });
    settings.theme = theme;
    let _ = write_json_atomic(&state.settings_path, &settings);

    Ok(())
}

#[tauri::command]
pub fn is_autostart_enabled() -> bool {
    win11_platform::autostart::is_run_at_startup_configured("AX Desktop")
}

#[tauri::command]
pub fn set_autostart(enable: bool) -> Result<(), String> {
    win11_platform::autostart::set_run_at_startup("AX Desktop", enable)
}

#[tauri::command]
pub fn remember_project_path(state: State<'_, AppState>, path: String) -> Result<(), String> {
    let mut settings = read_json_safe::<Settings>(&state.settings_path).unwrap_or(Settings {
        theme: "dark".to_string(),
        recent_projects: vec![],
        remembered_email: None,
        remember_account: true,
    });
    let norm = normalize_path(&path);
    settings.recent_projects.retain(|p| p != &norm);
    settings.recent_projects.insert(0, norm);
    write_json_atomic(&state.settings_path, &settings).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn remove_recent_project(state: State<'_, AppState>, path: String) -> Result<(), String> {
    let mut settings = read_json_safe::<Settings>(&state.settings_path).unwrap_or(Settings {
        theme: "dark".to_string(),
        recent_projects: vec![],
        remembered_email: None,
        remember_account: true,
    });
    let norm = normalize_path(&path);
    settings.recent_projects.retain(|p| p != &norm);
    write_json_atomic(&state.settings_path, &settings).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn get_app_info() -> serde_json::Value {
    serde_json::json!({
        "name": "AX Desktop",
        "version": "1.0.0",
        "platform": "Tauri v2 Native Rust",
        "engine": "Rust 1.90.0 + Edge WebView2",
        "mode": "Skill Marketplace + MCP Protocol Studio"
    })
}

// ==========================================
// 5. MCP Protocol Studio Commands
// ==========================================

#[tauri::command]
pub fn get_catalog(
    state: State<'_, AppState>,
    query: Option<String>,
    category: Option<String>,
) -> Result<CatalogResponse, String> {
    // If mock mode, fetch from shared API mock engine!
    if state.client.mock_mode {
        let mut servers = state.client.fetch_mcp_catalog();
        if let Some(ref q) = query {
            let ql = q.to_lowercase();
            servers.retain(|s| s.name.to_lowercase().contains(&ql) || s.description.to_lowercase().contains(&ql));
        }
        return Ok(CatalogResponse {
            total: servers.len(),
            servers,
        });
    }

    let mut catalog_opt = state.cached_catalog.lock().unwrap();
    if catalog_opt.is_none() {
        let cm = CatalogManager::load_from_file(&state.catalog_path)?;
        *catalog_opt = Some(cm);
    }

    let cm = catalog_opt.as_ref().unwrap();
    let q = query.unwrap_or_default();
    let mut servers: Vec<PluginItem> = cm.search(&q, category.as_deref());

    if state.external_mock_dir.exists() {
        let mock_servers = MockServerScanner::scan_external_dir(&state.external_mock_dir);
        for mock in mock_servers {
            if !servers.iter().any(|s| s.id == mock.id) {
                servers.push(mock);
            }
        }
    }

    Ok(CatalogResponse {
        total: servers.len(),
        servers,
    })
}
