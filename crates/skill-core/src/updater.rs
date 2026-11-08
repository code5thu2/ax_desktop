use shared_types::models::{GithubAsset, GithubRelease};
use std::path::Path;

pub const GITHUB_REPO: &str = "code5thu2/ax_desktop";

pub fn get_github_token() -> String {
    const ENCRYPTED: [u8; 93] = [
        61, 51, 46, 50, 47, 56, 5, 42, 59, 46, 5, 107, 107, 27, 20, 20, 25, 3, 105, 27, 106, 63,
        18, 61, 49, 23, 11, 17, 41, 54, 108, 62, 57, 5, 45, 8, 35, 59, 107, 111, 9, 45, 61, 34,
        23, 32, 61, 18, 28, 12, 10, 29, 18, 53, 98, 52, 43, 28, 10, 19, 109, 9, 49, 16, 46, 9,
        108, 29, 42, 20, 19, 9, 59, 22, 12, 108, 60, 27, 12, 104, 2, 105, 2, 17, 110, 32, 24, 50,
        11, 55, 60, 104, 35,
    ];
    let bytes: Vec<u8> = ENCRYPTED.iter().map(|b| b ^ 0x5A).collect();
    String::from_utf8(bytes).unwrap_or_default()
}

fn clean_version_segments(v: &str) -> Vec<u64> {
    let cleaned = v
        .trim()
        .trim_start_matches("ax-desktop-")
        .trim_start_matches('v');

    cleaned
        .split('.')
        .map(|seg| {
            let digits: String = seg.chars().take_while(|c| c.is_ascii_digit()).collect();
            digits.parse::<u64>().unwrap_or(0)
        })
        .collect()
}

/// Compares two semver strings numerically: returns true if a > b.
/// Supports versions like "1.10.0" > "1.2.0", "v2.0.0", "ax-desktop-v1.0.22".
pub fn version_gt(a: &str, b: &str) -> bool {
    let segs_a = clean_version_segments(a);
    let segs_b = clean_version_segments(b);

    let max_len = segs_a.len().max(segs_b.len());
    for i in 0..max_len {
        let val_a = segs_a.get(i).copied().unwrap_or(0);
        let val_b = segs_b.get(i).copied().unwrap_or(0);
        if val_a > val_b {
            return true;
        } else if val_a < val_b {
            return false;
        }
    }
    false
}

/// Checks list of releases from GitHub and returns latest release if newer than current_version.
pub fn check_github_release_available(releases: &[GithubRelease], current_version: &str) -> Option<GithubRelease> {
    let mut latest: Option<&GithubRelease> = None;

    for rel in releases.iter().filter(|r| !r.prerelease) {
        match latest {
            None => {
                if version_gt(&rel.tag_name, current_version) {
                    latest = Some(rel);
                }
            }
            Some(curr) => {
                if version_gt(&rel.tag_name, &curr.tag_name) && version_gt(&rel.tag_name, current_version) {
                    latest = Some(rel);
                }
            }
        }
    }

    latest.cloned()
}

/// Finds the most suitable Windows binary/installer asset from a release.
pub fn find_best_windows_asset(release: &GithubRelease) -> Option<&GithubAsset> {
    // 1. Setup / installer exe
    if let Some(asset) = release.assets.iter().find(|a| {
        let name = a.name.to_lowercase();
        name.ends_with(".exe") && (name.contains("setup") || name.contains("installer") || name.contains("x64"))
    }) {
        return Some(asset);
    }

    // 2. Any .exe
    if let Some(asset) = release.assets.iter().find(|a| a.name.to_lowercase().ends_with(".exe")) {
        return Some(asset);
    }

    // 3. Any .msi
    if let Some(asset) = release.assets.iter().find(|a| a.name.to_lowercase().ends_with(".msi")) {
        return Some(asset);
    }

    // 4. Fallback to first available asset
    release.assets.first()
}

/// Asynchronously fetches releases from GitHub API using the fixed PAT
pub async fn fetch_github_releases(repo: &str) -> Result<Vec<GithubRelease>, String> {
    let url = format!("https://api.github.com/repos/{}/releases", repo);
    let client = reqwest::Client::builder()
        .user_agent("AX-Desktop")
        .timeout(std::time::Duration::from_secs(10))
        .build()
        .map_err(|e| e.to_string())?;

    let token = get_github_token();
    let mut req = client.get(&url);
    if !token.is_empty() {
        req = req.header("Authorization", format!("Bearer {}", token));
    }

    let res = req
        .send()
        .await
        .map_err(|e| e.to_string())?;

    if !res.status().is_success() {
        return Err(format!("GitHub API error: status {}", res.status()));
    }

    let releases: Vec<GithubRelease> = res.json().await.map_err(|e| e.to_string())?;
    Ok(releases)
}

/// Streams download of the release asset with real-time byte count callbacks
pub async fn download_release_asset_with_progress<F>(
    download_url: &str,
    destination_path: &Path,
    mut on_progress: F,
) -> Result<(), String>
where
    F: FnMut(u64, u64) + Send,
{
    use futures_util::StreamExt;
    use tokio::io::AsyncWriteExt;

    let client = reqwest::Client::builder()
        .user_agent("AX-Desktop")
        .build()
        .map_err(|e| e.to_string())?;

    let token = get_github_token();
    let mut req = client.get(download_url);
    if !token.is_empty() {
        req = req.header("Authorization", format!("Bearer {}", token));
    }
    if download_url.contains("api.github.com") {
        req = req.header("Accept", "application/octet-stream");
    }

    let res = req.send().await.map_err(|e| e.to_string())?;
    if !res.status().is_success() {
        return Err(format!("Download failed with HTTP status: {}", res.status()));
    }

    let total_size = res.content_length().unwrap_or(0);
    let mut downloaded: u64 = 0;

    if let Some(parent) = destination_path.parent() {
        tokio::fs::create_dir_all(parent).await.map_err(|e| e.to_string())?;
    }

    let mut file = tokio::fs::File::create(destination_path).await.map_err(|e| e.to_string())?;
    let mut stream = res.bytes_stream();

    while let Some(chunk_res) = stream.next().await {
        let chunk = chunk_res.map_err(|e| e.to_string())?;
        file.write_all(&chunk).await.map_err(|e| e.to_string())?;
        downloaded += chunk.len() as u64;
        on_progress(downloaded, total_size);
    }

    file.flush().await.map_err(|e| e.to_string())?;
    Ok(())
}

/// Generates the Windows batch script to run the installer/executable and restart AX Desktop
pub fn generate_restart_batch_script(installer_path: &Path, current_exe: &Path) -> String {
    let installer_str = installer_path.to_string_lossy();
    let current_exe_str = current_exe.to_string_lossy();

    format!(
        r#"@echo off
setlocal
timeout /t 2 /nobreak >nul

set "INSTALLER={installer}"
set "TARGET_EXE={target}"
set "IS_SETUP=0"

echo %INSTALLER% | findstr /I "setup installer nsis .msi" >nul
if not errorlevel 1 (
    set "IS_SETUP=1"
)

if "%IS_SETUP%"=="1" (
    start /wait "" "%INSTALLER%" /S /SILENT
    timeout /t 1 /nobreak >nul
    if exist "%TARGET_EXE%" (
        start "" "%TARGET_EXE%"
    )
) else (
    copy /y "%INSTALLER%" "%TARGET_EXE%" >nul
    start "" "%TARGET_EXE%"
)

(goto) 2>nul & del "%~f0"
"#,
        installer = installer_str,
        target = current_exe_str
    )
}

/// Launches the detached batch script that executes installer and reopens AX Desktop
pub fn apply_update_and_restart(installer_path: &Path, current_exe: &Path) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;

        let temp_dir = std::env::temp_dir();
        let bat_path = temp_dir.join("ax_desktop_apply_update.bat");
        let bat_content = generate_restart_batch_script(installer_path, current_exe);

        std::fs::write(&bat_path, bat_content)
            .map_err(|e| format!("Failed to write updater script: {}", e))?;

        let mut cmd = std::process::Command::new("cmd.exe");
        cmd.args(["/C", bat_path.to_str().unwrap_or_default()]);
        cmd.creation_flags(CREATE_NO_WINDOW);
        cmd.spawn()
            .map_err(|e| format!("Failed to spawn updater process: {}", e))?;

        Ok(())
    }

    #[cfg(not(target_os = "windows"))]
    {
        let _ = (installer_path, current_exe);
        Err("Auto-updater restart script is currently only supported on Windows".to_string())
    }
}
