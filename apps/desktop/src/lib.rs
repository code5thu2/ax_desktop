pub mod commands;

use commands::AppState;
use tauri::Manager;

pub fn run() {
    // 1. Single Instance check
    let _guard = match win11_platform::single_instance::SingleInstanceGuard::acquire(
        "MCP_Protocol_Studio_SingleInstance_Mutex",
    ) {
        Ok(g) => g,
        Err(_) => {
            eprintln!("Another instance of MCP Protocol Studio is already running.");
            std::process::exit(0);
        }
    };

    // 2. Tauri application builder
    tauri::Builder::default()
        .setup(|app| {
            app.manage(AppState::new());

            if let Some(window) = app.get_webview_window("main") {
                #[cfg(target_os = "windows")]
                {
                    if let Ok(hwnd) = window.hwnd() {
                        let _ = win11_platform::dwm::apply_dark_titlebar(hwnd.0 as isize, true);
                    }
                }
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::get_catalog,
            commands::set_theme,
            commands::is_autostart_enabled,
            commands::set_autostart,
            commands::get_app_info,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
