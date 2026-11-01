use std::path::PathBuf;
use std::process::Command;

/// Attempts to locate AIPRO_Studio.exe in order:
/// 1. Registry HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall
/// 2. Parent directory of current exe
/// 3. Current exe directory
/// 4. %LOCALAPPDATA%\Programs\AIPRO STUDIO\AIPRO_Studio.exe
pub fn locate_aipro_studio() -> Option<PathBuf> {
    if let Ok(current_exe) = std::env::current_exe() {
        if let Some(parent) = current_exe.parent() {
            let candidate1 = parent.join("AIPRO_Studio.exe");
            if candidate1.exists() {
                return Some(candidate1);
            }
            if let Some(grandparent) = parent.parent() {
                let candidate2 = grandparent.join("AIPRO_Studio.exe");
                if candidate2.exists() {
                    return Some(candidate2);
                }
            }
        }
    }

    if let Ok(local_appdata) = std::env::var("LOCALAPPDATA") {
        let candidate = PathBuf::from(local_appdata)
            .join("Programs")
            .join("AIPRO STUDIO")
            .join("AIPRO_Studio.exe");
        if candidate.exists() {
            return Some(candidate);
        }
    }

    None
}

/// Launches AIPRO Studio if detected on machine
pub fn launch_aipro_studio() -> Result<(), String> {
    match locate_aipro_studio() {
        Some(exe_path) => {
            Command::new(exe_path)
                .spawn()
                .map_err(|e| format!("Failed to spawn AIPRO Studio: {}", e))?;
            Ok(())
        }
        None => Err("AIPRO Studio is not installed on this machine".to_string()),
    }
}
