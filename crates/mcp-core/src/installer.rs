use std::collections::HashMap;
use std::path::PathBuf;
use tokio::process::Command;

pub struct ClientInstaller {
    base_install_dir: PathBuf,
    uv_bin_path: PathBuf,
}

impl ClientInstaller {
    pub fn new(base_install_dir: PathBuf, uv_bin_path: PathBuf) -> Self {
        Self {
            base_install_dir,
            uv_bin_path,
        }
    }

    pub fn get_server_dir(&self, server_id: &str) -> PathBuf {
        self.base_install_dir.join(server_id)
    }

    pub fn is_installed(&self, server_id: &str) -> bool {
        let dir = self.get_server_dir(server_id);
        let python_exe = dir.join(".venv").join("Scripts").join("python.exe");
        dir.exists() && python_exe.exists()
    }

    /// Initializes a virtualenv using uv.exe in the server directory
    pub async fn create_venv(&self, server_id: &str) -> Result<PathBuf, String> {
        let server_dir = self.get_server_dir(server_id);
        tokio::fs::create_dir_all(&server_dir)
            .await
            .map_err(|e| e.to_string())?;

        let venv_dir = server_dir.join(".venv");

        let status = Command::new(&self.uv_bin_path)
            .arg("venv")
            .arg(&venv_dir)
            .current_dir(&server_dir)
            .status()
            .await
            .map_err(|e| format!("Failed to execute uv venv: {}", e))?;

        if !status.success() {
            return Err("uv venv execution failed".to_string());
        }

        let python_exe = venv_dir.join("Scripts").join("python.exe");
        Ok(python_exe)
    }

    /// Writes environment variables to .env file in server directory
    pub async fn write_env_file(&self, server_id: &str, env_vars: &HashMap<String, String>) -> Result<(), String> {
        let server_dir = self.get_server_dir(server_id);
        let mut content = String::new();
        for (k, v) in env_vars {
            content.push_str(&format!("{}={}\n", k, v));
        }

        let env_path = server_dir.join(".env");
        tokio::fs::write(&env_path, content)
            .await
            .map_err(|e| format!("Failed to write .env file: {}", e))
    }
}
