use shared_types::models::{
    AuthTokens, AuthUser, PluginItem, SkillDetail, SkillFileItem, SkillItem, SkillVersionItem,
};
use std::collections::HashMap;
use std::io::Write;
use zip::write::SimpleFileOptions;

pub struct MockEngine {
    skills: Vec<SkillDetail>,
    mcp_servers: Vec<PluginItem>,
}

impl Default for MockEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl MockEngine {
    pub fn new() -> Self {
        let skills = vec![
            SkillDetail {
                id: 101,
                name: "AI Code Assistant".to_string(),
                description: "Tự động phân tích, giải thích mã nguồn và sinh unit tests thông minh cho TypeScript và Rust.".to_string(),
                creator_name: "AIPRO Core Team".to_string(),
                created_at: "2026-10-15T08:00:00Z".to_string(),
                status: "APPROVED".to_string(),
                scope: "PUBLIC".to_string(),
                categories: vec!["Coding".to_string(), "Productivity".to_string()],
                stages: vec!["Development".to_string(), "Testing".to_string()],
                view_count: 1420,
                avg_rating: Some(4.9),
                rating_count: 88,
                subscribed: true,
                installed: false,
                enabled: false,
                install_scope: None,
                installed_projects: vec![],
                project_states: HashMap::new(),
                install_path: None,
                installed_version: None,
                version: 2,
                hashtags: vec!["#rust".to_string(), "#typescript".to_string(), "#ai".to_string()],
                files: vec![
                    SkillFileItem {
                        id: 1,
                        file_name: "SKILL.md".to_string(),
                        file_size: 1450,
                        created_at: "2026-10-15T08:00:00Z".to_string(),
                    },
                    SkillFileItem {
                        id: 2,
                        file_name: "assistant.py".to_string(),
                        file_size: 4200,
                        created_at: "2026-10-15T08:00:00Z".to_string(),
                    },
                ],
                is_creator: false,
                can_edit: false,
                updated_at: "2026-10-28T12:00:00Z".to_string(),
            },
            SkillDetail {
                id: 102,
                name: "Smart Database Query & Introspection".to_string(),
                description: "Truy vấn, phân tích lược đồ dữ liệu PostgreSQL và MySQL với cảnh báo tối ưu hóa chỉ mục SQL.".to_string(),
                creator_name: "GDC Data Lab".to_string(),
                created_at: "2026-09-20T10:30:00Z".to_string(),
                status: "APPROVED".to_string(),
                scope: "PUBLIC".to_string(),
                categories: vec!["Database".to_string()],
                stages: vec!["Production".to_string()],
                view_count: 980,
                avg_rating: Some(4.8),
                rating_count: 52,
                subscribed: false,
                installed: false,
                enabled: false,
                install_scope: None,
                installed_projects: vec![],
                project_states: HashMap::new(),
                install_path: None,
                installed_version: None,
                version: 1,
                hashtags: vec!["#sql".to_string(), "#database".to_string(), "#postgres".to_string()],
                files: vec![
                    SkillFileItem {
                        id: 3,
                        file_name: "SKILL.md".to_string(),
                        file_size: 1200,
                        created_at: "2026-09-20T10:30:00Z".to_string(),
                    },
                ],
                is_creator: false,
                can_edit: false,
                updated_at: "2026-09-20T10:30:00Z".to_string(),
            },
            SkillDetail {
                id: 103,
                name: "Multi-Language Legal Document Analyzer".to_string(),
                description: "Soát xét hợp đồng thương mại, đối chiếu xung đột luật Việt Nam theo thứ bậc văn bản pháp quy.".to_string(),
                creator_name: "LegalTech Vietnam".to_string(),
                created_at: "2026-10-01T09:15:00Z".to_string(),
                status: "APPROVED".to_string(),
                scope: "PUBLIC".to_string(),
                categories: vec!["Legal".to_string(), "Analysis".to_string()],
                stages: vec!["Review".to_string()],
                view_count: 650,
                avg_rating: Some(5.0),
                rating_count: 31,
                subscribed: false,
                installed: false,
                enabled: false,
                install_scope: None,
                installed_projects: vec![],
                project_states: HashMap::new(),
                install_path: None,
                installed_version: None,
                version: 3,
                hashtags: vec!["#law".to_string(), "#vietnam".to_string()],
                files: vec![
                    SkillFileItem {
                        id: 4,
                        file_name: "SKILL.md".to_string(),
                        file_size: 2100,
                        created_at: "2026-10-01T09:15:00Z".to_string(),
                    },
                ],
                is_creator: false,
                can_edit: false,
                updated_at: "2026-10-30T15:20:00Z".to_string(),
            },
        ];

        let mcp_servers = vec![
            PluginItem {
                id: "postgres-mcp".to_string(),
                name: "PostgreSQL MCP Explorer".to_string(),
                item_type: "mcp".to_string(),
                vendor: "Unified Tools Lab".to_string(),
                version: "2.4.1".to_string(),
                icon: "pi pi-database".to_string(),
                rating: 4.9,
                downloads: "48.2k".to_string(),
                summary: "Database introspection & execution tool".to_string(),
                description: "Enables AI models to execute SQL queries directly against PostgreSQL instances.".to_string(),
                features: vec!["Schema Inspection".to_string(), "Query Optimization".to_string()],
                installed: true,
                enabled: true,
                install_path: Some("storage/installed/postgres".to_string()),
                tools: None,
                change_notes: Some("v2.4.1: Partitioned tables support".to_string()),
                category: Some("Database".to_string()),
                runtime: Some("rust".to_string()),
                download_url: None,
                env_requirements: None,
                configured_env: None,
            },
            PluginItem {
                id: "gitlab-mcp".to_string(),
                name: "GitLab Enterprise Gateway".to_string(),
                item_type: "mcp".to_string(),
                vendor: "DevOps Automation".to_string(),
                version: "1.3.0".to_string(),
                icon: "pi pi-code".to_string(),
                rating: 4.7,
                downloads: "23.1k".to_string(),
                summary: "GitLab pipeline and MR manager".to_string(),
                description: "Inspect pipeline statuses, automate merge requests and view CI logs.".to_string(),
                features: vec!["Pipelines".to_string(), "Merge Requests".to_string()],
                installed: false,
                enabled: false,
                install_path: None,
                tools: None,
                change_notes: None,
                category: Some("DevOps".to_string()),
                runtime: Some("rust".to_string()),
                download_url: None,
                env_requirements: None,
                configured_env: None,
            },
        ];

        Self { skills, mcp_servers }
    }

    pub fn request_otp(&self, _email: &str) -> Result<(), String> {
        Ok(())
    }

    pub fn verify_otp(&self, _email: &str, otp: &str) -> Result<(), String> {
        if otp == "123456" || otp == "729415" || otp == "888999" {
            Ok(())
        } else {
            Err("Mã OTP không hợp lệ (mã mock đúng là 123456 hoặc 729415)".to_string())
        }
    }

    pub fn login(&self, email: &str, _password: &str) -> Result<AuthTokens, String> {
        Ok(AuthTokens {
            access_token: "mock-jwt-access-token-xyz789".to_string(),
            refresh_token: "mock-jwt-refresh-token-abc123".to_string(),
            user: Some(AuthUser {
                id: 1001,
                name: "AIPRO Developer".to_string(),
                email: email.to_string(),
                avatar: None,
            }),
            updated_at: Some("2026-11-02T02:00:00Z".to_string()),
        })
    }

    pub fn fetch_skills(&self, query: Option<&str>, _page: usize, _page_size: usize) -> Vec<SkillItem> {
        self.skills
            .iter()
            .filter(|s| {
                if let Some(q) = query {
                    let q_lower = q.to_lowercase();
                    s.name.to_lowercase().contains(&q_lower)
                        || s.description.to_lowercase().contains(&q_lower)
                } else {
                    true
                }
            })
            .map(|d| SkillItem {
                id: d.id,
                name: d.name.clone(),
                description: d.description.clone(),
                creator_name: d.creator_name.clone(),
                created_at: d.created_at.clone(),
                status: d.status.clone(),
                scope: d.scope.clone(),
                categories: d.categories.clone(),
                stages: d.stages.clone(),
                view_count: d.view_count,
                avg_rating: d.avg_rating,
                rating_count: d.rating_count,
                subscribed: d.subscribed,
                installed: d.installed,
                enabled: d.enabled,
                install_scope: d.install_scope.clone(),
                installed_projects: d.installed_projects.clone(),
                project_states: d.project_states.clone(),
                install_path: d.install_path.clone(),
                installed_version: d.installed_version,
            })
            .collect()
    }

    pub fn get_skill_detail(&self, id: u64) -> Result<SkillDetail, String> {
        self.skills
            .iter()
            .find(|s| s.id == id)
            .cloned()
            .ok_or_else(|| format!("Skill with ID {} not found", id))
    }

    pub fn get_skill_versions(&self, id: u64) -> Vec<SkillVersionItem> {
        if let Ok(detail) = self.get_skill_detail(id) {
            vec![
                SkillVersionItem {
                    version: detail.version,
                    name: detail.name.clone(),
                    description: format!("Phiên bản mới nhất {}", detail.version),
                    public_scope: detail.scope.clone(),
                    hashtags: detail.hashtags.clone(),
                    creator_name: detail.creator_name.clone(),
                    created_at: detail.created_at.clone(),
                    files: detail.files.clone(),
                },
                SkillVersionItem {
                    version: 1,
                    name: detail.name.clone(),
                    description: "Bản phát hành đầu tiên".to_string(),
                    public_scope: detail.scope.clone(),
                    hashtags: detail.hashtags.clone(),
                    creator_name: detail.creator_name.clone(),
                    created_at: "2026-09-01T00:00:00Z".to_string(),
                    files: detail.files.clone(),
                },
            ]
        } else {
            vec![]
        }
    }

    pub fn generate_skill_zip(&self, id: u64, skill_name: &str) -> Result<Vec<u8>, String> {
        let mut buf = Vec::new();
        let cursor = std::io::Cursor::new(&mut buf);
        let mut zip = zip::ZipWriter::new(cursor);

        let skill_md_content = format!(
            "---\nname: {}\nid: {}\ndescription: {}\n---\n\n# {}\n\nSkill được tạo tự động bởi AX Desktop Mock Engine.",
            skill_name, id, skill_name, skill_name
        );

        zip.start_file("SKILL.md", SimpleFileOptions::default())
            .map_err(|e| e.to_string())?;
        zip.write_all(skill_md_content.as_bytes())
            .map_err(|e| e.to_string())?;

        zip.finish().map_err(|e| e.to_string())?;
        Ok(buf)
    }

    pub fn fetch_mcp_catalog(&self) -> Vec<PluginItem> {
        self.mcp_servers.clone()
    }
}
