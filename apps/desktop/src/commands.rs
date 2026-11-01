use mcp_core::catalog::CatalogManager;
use mcp_core::mock_runner::MockServerScanner;
use shared_types::models::{CatalogResponse, PluginItem};
use std::path::PathBuf;
use std::sync::Mutex;
use tauri::{State, Window};

pub struct AppState {
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

        Self {
            catalog_path,
            external_mock_dir,
            cached_catalog: Mutex::new(None),
        }
    }
}

#[tauri::command]
pub fn get_catalog(
    state: State<'_, AppState>,
    query: Option<String>,
    category: Option<String>,
) -> Result<CatalogResponse, String> {
    let mut catalog_opt = state.cached_catalog.lock().unwrap();
    if catalog_opt.is_none() {
        let cm = CatalogManager::load_from_file(&state.catalog_path)?;
        *catalog_opt = Some(cm);
    }

    let cm = catalog_opt.as_ref().unwrap();
    let q = query.unwrap_or_default();
    let mut servers: Vec<PluginItem> = cm.search(&q, category.as_deref());

    // Also merge external mock servers if the directory exists
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

#[tauri::command]
pub fn set_theme(window: Window, is_dark: bool) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        if let Ok(hwnd) = window.hwnd() {
            let _ = win11_platform::dwm::apply_dark_titlebar(hwnd.0 as isize, is_dark);
        }
    }
    Ok(())
}

#[tauri::command]
pub fn is_autostart_enabled() -> bool {
    win11_platform::autostart::is_run_at_startup_configured("MCP Protocol Studio")
}

#[tauri::command]
pub fn set_autostart(enable: bool) -> Result<(), String> {
    win11_platform::autostart::set_run_at_startup("MCP Protocol Studio", enable)
}

#[tauri::command]
pub fn get_app_info() -> serde_json::Value {
    serde_json::json!({
        "name": "MCP Protocol Studio",
        "version": "1.0.0",
        "platform": "Tauri v2 Native Rust",
        "engine": "Rust 1.90.0 + Edge WebView2"
    })
}
