use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

pub struct RuntimeInstaller;

impl RuntimeInstaller {
    /// Discovers bundled or system `uv.exe`
    pub fn find_uv_binary() -> Option<PathBuf> {
        // 1. Explicit environment variable override
        if let Ok(custom_path) = std::env::var("UV_BIN") {
            let p = PathBuf::from(custom_path);
            if p.exists() {
                return Some(p);
            }
        }

        // 2. Upward traversal from current executable directory
        if let Ok(exe_path) = std::env::current_exe() {
            let mut curr = exe_path.parent();
            for _ in 0..5 {
                if let Some(dir) = curr {
                    let candidate1 = dir.join("bin").join("uv.exe");
                    if candidate1.exists() {
                        return Some(candidate1);
                    }
                    let candidate2 = dir.join("uv.exe");
                    if candidate2.exists() {
                        return Some(candidate2);
                    }
                    curr = dir.parent();
                } else {
                    break;
                }
            }
        }

        // 3. Upward traversal from current working directory
        if let Ok(cwd) = std::env::current_dir() {
            let mut curr = Some(cwd.as_path());
            for _ in 0..5 {
                if let Some(dir) = curr {
                    let candidate1 = dir.join("bin").join("uv.exe");
                    if candidate1.exists() {
                        return Some(candidate1);
                    }
                    let candidate2 = dir.join("uv.exe");
                    if candidate2.exists() {
                        return Some(candidate2);
                    }
                    curr = dir.parent();
                } else {
                    break;
                }
            }
        }

        // 4. In development / testing: check workspace root relative to CARGO_MANIFEST_DIR
        let manifest_dir = Path::new(env!("CARGO_MANIFEST_DIR"));
        let mut curr = Some(manifest_dir);
        for _ in 0..4 {
            if let Some(dir) = curr {
                let candidate = dir.join("bin").join("uv.exe");
                if candidate.exists() {
                    return Some(candidate);
                }
                curr = dir.parent();
            } else {
                break;
            }
        }

        // 5. Fallback: check directories in system PATH
        if let Ok(path_var) = std::env::var("PATH") {
            for dir in std::env::split_paths(&path_var) {
                let candidate = dir.join("uv.exe");
                if candidate.exists() {
                    return Some(candidate);
                }
            }
        }

        None
    }

    /// Creates an isolated Python virtual environment inside target_dir/.venv
    pub fn create_venv(uv_bin: &Path, target_dir: &Path) -> Result<PathBuf, String> {
        let venv_dir = target_dir.join(".venv");
        let status = Command::new(uv_bin)
            .arg("venv")
            .arg(&venv_dir)
            .current_dir(target_dir)
            .status()
            .map_err(|e| format!("Failed to execute uv venv: {}", e))?;

        if !status.success() {
            return Err("uv.exe venv command exited with error status".to_string());
        }

        let python_exe = venv_dir.join("Scripts").join("python.exe");
        if !python_exe.exists() {
            return Err(format!("Python executable not found at {}", python_exe.display()));
        }

        Ok(python_exe)
    }

    /// Installs wheels offline from wheels_dir using uv pip install --no-index
    pub fn install_wheels_offline(
        uv_bin: &Path,
        target_dir: &Path,
        wheels_dir: &Path,
        req_file: &Path,
    ) -> Result<(), String> {
        if !req_file.exists() {
            return Ok(());
        }

        let python_exe = target_dir.join(".venv").join("Scripts").join("python.exe");

        let mut cmd = Command::new(uv_bin);
        cmd.arg("pip")
            .arg("install")
            .arg("--no-index")
            .arg("--find-links")
            .arg(wheels_dir)
            .arg("-r")
            .arg(req_file);

        if python_exe.exists() {
            cmd.arg("--python").arg(&python_exe);
        }

        let status = cmd
            .current_dir(target_dir)
            .status()
            .map_err(|e| format!("Failed to execute uv pip install offline: {}", e))?;

        if !status.success() {
            return Err("uv.exe pip install offline failed".to_string());
        }

        Ok(())
    }

    /// End-to-end zero-config provisioning for any package (MCP Server or Skill)
    pub fn provision_runtime(
        target_dir: &Path,
        wheels_zip_bytes: Option<&[u8]>,
    ) -> Result<Option<PathBuf>, String> {
        let has_req = target_dir.join("requirements.txt").exists();
        let has_scripts = target_dir.join("scripts").exists();

        // If package does not contain Python code or requirements, skip runtime setup
        if !has_req && !has_scripts {
            return Ok(None);
        }

        let uv_bin = match Self::find_uv_binary() {
            Some(bin) => bin,
            None => {
                return Err("Bundled uv.exe runtime tool not found. Cannot provision isolated Python environment.".to_string());
            }
        };

        // 1. If wheels zip bytes provided, unpack them safely to target_dir/wheels
        if let Some(bytes) = wheels_zip_bytes {
            let wheels_dir = target_dir.join("wheels");
            let _ = fs::create_dir_all(&wheels_dir);
            crate::storage::extract_zip_safe(bytes, &wheels_dir)
                .map_err(|e| format!("Failed to extract dependency wheels: {}", e))?;
        }

        // 2. Initialize isolated .venv
        let python_exe = Self::create_venv(&uv_bin, target_dir)?;

        // 3. Install wheels offline if requirements.txt and wheels/ exist
        let req_file = target_dir.join("requirements.txt");
        let wheels_dir = target_dir.join("wheels");
        if req_file.exists() && wheels_dir.exists() {
            Self::install_wheels_offline(&uv_bin, target_dir, &wheels_dir, &req_file)?;
        }

        Ok(Some(python_exe))
    }
}
