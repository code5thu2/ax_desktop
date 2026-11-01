pub mod commands;

use commands::AppState;
use tauri::menu::{Menu, MenuItem};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::Manager;

pub fn run() {
    // 1. Single Instance Named Mutex Guard (spec: AX_DESKTOP_SINGLE_INSTANCE_MUTEX)
    let _guard = match win11_platform::single_instance::SingleInstanceGuard::acquire(
        "AX_DESKTOP_SINGLE_INSTANCE_MUTEX",
    ) {
        Ok(g) => g,
        Err(_) => {
            eprintln!("Another instance of AX Desktop is already running.");
            std::process::exit(0);
        }
    };

    // 2. Tauri application builder
    tauri::Builder::default()
        .setup(|app| {
            app.manage(AppState::new());

            // Setup System Tray
            let show_item = MenuItem::with_id(app, "show", "Mở AX Desktop", true, None::<&str>)?;
            let autostart_item = MenuItem::with_id(
                app,
                "autostart",
                "Khởi động cùng Windows",
                true,
                None::<&str>,
            )?;
            let quit_item = MenuItem::with_id(app, "quit", "Thoát ứng dụng", true, None::<&str>)?;
            let tray_menu = Menu::with_items(app, &[&show_item, &autostart_item, &quit_item])?;

            if let Some(icon) = app.default_window_icon() {
                let _tray = TrayIconBuilder::new()
                    .icon(icon.clone())
                    .menu(&tray_menu)
                    .show_menu_on_left_click(false)
                    .on_menu_event(|app, event| match event.id.as_ref() {
                        "show" => {
                            if let Some(w) = app.get_webview_window("main") {
                                let _ = w.show();
                                let _ = w.unminimize();
                                let _ = w.set_focus();
                            }
                        }
                        "autostart" => {
                            let curr = win11_platform::autostart::is_run_at_startup_configured("AX Desktop");
                            let _ = win11_platform::autostart::set_run_at_startup("AX Desktop", !curr);
                        }
                        "quit" => {
                            app.exit(0);
                        }
                        _ => {}
                    })
                    .on_tray_icon_event(|tray, event| {
                        if let TrayIconEvent::Click {
                            button: MouseButton::Left,
                            button_state: MouseButtonState::Up,
                            ..
                        } = event
                        {
                            let app = tray.app_handle();
                            if let Some(w) = app.get_webview_window("main") {
                                let _ = w.show();
                                let _ = w.unminimize();
                                let _ = w.set_focus();
                            }
                        }
                    })
                    .build(app)?;
            }

            // DWM dark titlebar & Close-to-Tray event hook
            if let Some(window) = app.get_webview_window("main") {
                #[cfg(target_os = "windows")]
                {
                    if let Ok(hwnd) = window.hwnd() {
                        let _ = win11_platform::dwm::apply_dark_titlebar(hwnd.0 as isize, true);
                    }
                }

                // Intercept close button [X] to minimize to tray
                let win_clone = window.clone();
                window.on_window_event(move |event| {
                    if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                        api.prevent_close();
                        let _ = win_clone.hide();
                    }
                });
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // Auth
            commands::login,
            commands::request_register_otp,
            commands::verify_register_otp,
            commands::register,
            commands::request_forgot_otp,
            commands::verify_forgot_otp,
            commands::reset_password,
            commands::logout,
            // Status & Marketplace
            commands::get_status,
            commands::fetch_skills,
            commands::get_skill_detail,
            commands::get_skill_versions,
            // Lifecycle
            commands::install,
            commands::uninstall,
            commands::toggle,
            commands::clone_skill,
            // Integration & System
            commands::open_studio,
            commands::select_folder,
            commands::check_for_update,
            commands::set_theme,
            commands::is_autostart_enabled,
            commands::set_autostart,
            commands::remember_project_path,
            commands::save_recent_project,
            commands::remove_recent_project,
            commands::show_window,
            commands::get_app_info,
            // MCP Protocol Studio
            commands::get_catalog,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
