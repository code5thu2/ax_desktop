use crate::storage::{extract_zip_safe, normalize_path, read_json_safe, write_json_atomic};
use crate::synchronizer::{read_skill_name_from_md, sync_disabled_skills};
use shared_types::models::InstalledPlugin;
use std::fs;
use std::path::{Path, PathBuf};

pub struct SkillManager {
    pub global_skills_root: PathBuf,
    pub installed_json_path: PathBuf,
    pub global_config_path: PathBuf,
}

impl SkillManager {
    pub fn new(global_skills_root: PathBuf, installed_json_path: PathBuf, global_config_path: PathBuf) -> Self {
        Self {
            global_skills_root,
            installed_json_path,
            global_config_path,
        }
    }

    pub fn list_installed(&self) -> Vec<InstalledPlugin> {
        let raw = read_json_safe::<Vec<InstalledPlugin>>(&self.installed_json_path).unwrap_or_default();
        let mut deduped: Vec<InstalledPlugin> = Vec::new();
        for item in raw {
            if let Some(pos) = deduped.iter().position(|x| {
                (x.id == item.id || x.name == item.name)
                    && x.scope == item.scope
                    && x.project_path == item.project_path
            }) {
                deduped[pos] = item;
            } else {
                deduped.push(item);
            }
        }
        deduped
    }

    fn save_installed(&self, list: &[InstalledPlugin]) -> Result<(), String> {
        write_json_atomic(&self.installed_json_path, &list).map_err(|e| e.to_string())
    }

    pub fn resolve_target_dir(&self, id: u64, scope: &str, project_path: Option<&str>) -> Result<PathBuf, String> {
        if scope == "global" {
            Ok(self.global_skills_root.join(id.to_string()))
        } else if scope == "project" {
            let p_raw = project_path.ok_or_else(|| "project_path is required for project scope".to_string())?;
            let normalized = normalize_path(p_raw);
            Ok(PathBuf::from(normalized).join(".aipro/skills").join(id.to_string()))
        } else {
            Err(format!("Invalid scope: {}", scope))
        }
    }

    pub fn resolve_config_path(&self, scope: &str, project_path: Option<&str>) -> Result<PathBuf, String> {
        if scope == "global" {
            Ok(self.global_config_path.clone())
        } else if scope == "project" {
            let p_raw = project_path.ok_or_else(|| "project_path is required for project scope".to_string())?;
            let normalized = normalize_path(p_raw);
            Ok(PathBuf::from(normalized).join(".aipro/config.json"))
        } else {
            Err(format!("Invalid scope: {}", scope))
        }
    }

    pub fn install(
        &self,
        id: u64,
        name: &str,
        version: u32,
        scope: &str,
        project_path: Option<&str>,
        zip_bytes: &[u8],
    ) -> Result<String, String> {
        let target_dir = self.resolve_target_dir(id, scope, project_path)?;
        let tmp_extract_dir = PathBuf::from(format!("{}.downloading", target_dir.to_string_lossy()));

        if tmp_extract_dir.exists() {
            let _ = fs::remove_dir_all(&tmp_extract_dir);
        }

        extract_zip_safe(zip_bytes, &tmp_extract_dir).map_err(|e| e.to_string())?;

        if target_dir.exists() {
            let _ = fs::remove_dir_all(&target_dir);
        }
        if let Some(parent) = target_dir.parent() {
            let _ = fs::create_dir_all(parent);
        }
        fs::rename(&tmp_extract_dir, &target_dir).map_err(|e| e.to_string())?;

        let mut list = self.list_installed();
        let norm_proj = project_path.map(normalize_path);

        list.retain(|item| {
            !( (item.id == id || item.name == name) && item.scope == scope && item.project_path == norm_proj )
        });

        list.push(InstalledPlugin {
            id,
            name: name.to_string(),
            version,
            enabled: true,
            installed_at: chrono::Utc::now().to_rfc3339(),
            scope: scope.to_string(),
            project_path: norm_proj.clone(),
        });

        self.save_installed(&list)?;

        let config_path = self.resolve_config_path(scope, project_path)?;
        let skill_core_name = read_skill_name_from_md(&target_dir);
        let _ = sync_disabled_skills(&config_path, &skill_core_name, false);

        if !target_dir.join("SKILL.md").exists() {
            Ok("NO_SKILL_MD".to_string())
        } else {
            Ok("SUCCESS".to_string())
        }
    }

    pub fn toggle(&self, id: u64, enabled: bool, scope: &str, project_path: Option<&str>) -> Result<(), String> {
        let norm_proj = project_path.map(normalize_path);
        let mut list = self.list_installed();
        let mut target_dir_opt = None;

        let mut found = false;
        for item in list.iter_mut() {
            if item.id == id && item.scope == scope && item.project_path == norm_proj {
                item.enabled = enabled;
                target_dir_opt = self.resolve_target_dir(id, scope, project_path).ok();
                found = true;
            }
        }

        if !found {
            return Err(format!("Installed skill with id {} not found", id));
        }

        self.save_installed(&list)?;

        if let Some(target_dir) = target_dir_opt {
            let config_path = self.resolve_config_path(scope, project_path)?;
            let skill_core_name = read_skill_name_from_md(&target_dir);
            let _ = sync_disabled_skills(&config_path, &skill_core_name, !enabled);
        }

        Ok(())
    }

    pub fn uninstall(&self, id: u64, scope: &str, project_path: Option<&str>) -> Result<(), String> {
        let norm_proj = project_path.map(normalize_path);
        let mut list = self.list_installed();

        if scope == "all" {
            for item in list.iter().filter(|i| i.id == id) {
                if let Ok(td) = self.resolve_target_dir(item.id, &item.scope, item.project_path.as_deref()) {
                    let core_name = read_skill_name_from_md(&td);
                    let _ = fs::remove_dir_all(&td);
                    if let Ok(cfg) = self.resolve_config_path(&item.scope, item.project_path.as_deref()) {
                        let _ = sync_disabled_skills(&cfg, &core_name, false);
                    }
                }
            }
            list.retain(|item| item.id != id);
        } else {
            let target_item = list.iter().find(|item| {
                item.id == id || (item.scope == scope && item.project_path == norm_proj)
            }).cloned();
            let actual_id = target_item.as_ref().map(|i| i.id).unwrap_or(id);

            if let Ok(td) = self.resolve_target_dir(actual_id, scope, project_path) {
                let core_name = read_skill_name_from_md(&td);
                let _ = fs::remove_dir_all(&td);
                if let Ok(cfg) = self.resolve_config_path(scope, project_path) {
                    let _ = sync_disabled_skills(&cfg, &core_name, false);
                }
            }
            list.retain(|item| {
                !( (item.id == id || item.id == actual_id) && item.scope == scope && item.project_path == norm_proj )
            });
        }

        self.save_installed(&list)
    }

    pub fn clone_skill(&self, id: u64, src_project: &str, dst_project: &str) -> Result<(), String> {
        let src_dir = self.resolve_target_dir(id, "project", Some(src_project))?;
        let dst_dir = self.resolve_target_dir(id, "project", Some(dst_project))?;

        if !src_dir.exists() {
            return Err("Source project skill directory does not exist".to_string());
        }

        if dst_dir.exists() {
            let _ = fs::remove_dir_all(&dst_dir);
        }
        if let Some(parent) = dst_dir.parent() {
            let _ = fs::create_dir_all(parent);
        }

        // Recursive directory copy
        fn copy_dir_all(src: &Path, dst: &Path) -> std::io::Result<()> {
            fs::create_dir_all(dst)?;
            for entry in fs::read_dir(src)? {
                let entry = entry?;
                let file_type = entry.file_type()?;
                if file_type.is_symlink() {
                    continue;
                }
                if file_type.is_dir() {
                    copy_dir_all(&entry.path(), &dst.join(entry.file_name()))?;
                } else {
                    fs::copy(entry.path(), dst.join(entry.file_name()))?;
                }
            }
            Ok(())
        }

        copy_dir_all(&src_dir, &dst_dir).map_err(|e| e.to_string())?;

        let mut list = self.list_installed();
        let norm_dst = normalize_path(dst_project);
        let src_entry = list.iter().find(|i| i.id == id).cloned();

        list.retain(|i| !(i.id == id && i.scope == "project" && i.project_path == Some(norm_dst.clone())));

        let name = src_entry.as_ref().map(|e| e.name.clone()).unwrap_or_else(|| read_skill_name_from_md(&dst_dir));
        let version = src_entry.as_ref().map(|e| e.version).unwrap_or(1);

        list.push(InstalledPlugin {
            id,
            name,
            version,
            enabled: true,
            installed_at: chrono::Utc::now().to_rfc3339(),
            scope: "project".to_string(),
            project_path: Some(norm_dst),
        });

        self.save_installed(&list)
    }
}
