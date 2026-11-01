use shared_types::models::{
    PluginEnvRequirement, PluginItem, PluginTool, CatalogResponse,
    AuthUser, AuthTokens, InstalledPlugin, SkillItem, SkillDetail,
    SkillVersionItem, PortalStatus, Settings, GithubRelease, GithubAsset
};

#[test]
fn test_ax_desktop_models() {
    let user = AuthUser {
        id: 1,
        name: "Test User".to_string(),
        email: "test@example.com".to_string(),
        avatar: None,
    };
    let auth = AuthTokens {
        access_token: "mock-access-token".to_string(),
        refresh_token: "mock-refresh-token".to_string(),
        user: Some(user.clone()),
        updated_at: Some("2026-11-02T00:00:00Z".to_string()),
    };
    let json_auth = serde_json::to_string(&auth).unwrap();
    assert!(json_auth.contains("mock-access-token"));

    let installed = InstalledPlugin {
        id: 42,
        name: "test-skill".to_string(),
        version: 1,
        enabled: true,
        installed_at: "2026-11-02T00:00:00Z".to_string(),
        scope: "global".to_string(),
        project_path: None,
    };
    let json_inst = serde_json::to_string(&installed).unwrap();
    assert!(json_inst.contains("test-skill"));

    let status = PortalStatus {
        logged_in: true,
        user: Some(user),
        theme: "dark".to_string(),
        installed: vec![installed],
        recent_projects: vec!["D:/projects/demo".to_string()],
        remembered_email: Some("test@example.com".to_string()),
        remember_account: true,
    };
    let json_status = serde_json::to_string(&status).unwrap();
    assert!(json_status.contains("test@example.com"));
    assert!(json_status.contains("recentProjects"));

    let gh_asset = GithubAsset {
        name: "AX-Desktop-Setup.exe".to_string(),
        browser_download_url: "https://github.com/code5thu2/ax_desktop/releases/download/v1.0.1/setup.exe".to_string(),
        size: 5200000,
    };
    let release = GithubRelease {
        tag_name: "v1.0.1".to_string(),
        name: Some("AX Desktop 1.0.1".to_string()),
        body: Some("Bug fixes".to_string()),
        prerelease: false,
        published_at: Some("2026-11-02T00:00:00Z".to_string()),
        assets: vec![gh_asset],
    };
    let json_release = serde_json::to_string(&release).unwrap();
    assert!(json_release.contains("v1.0.1"));
}

#[test]
fn test_plugin_item_serialization() {
    let item = PluginItem {
        id: "postgres-mcp".to_string(),
        name: "PostgreSQL Explorer".to_string(),
        item_type: "mcp".to_string(),
        vendor: "Unified Tools Lab".to_string(),
        version: "2.4.1".to_string(),
        icon: "pi pi-database".to_string(),
        rating: 4.9,
        downloads: "48.2k".to_string(),
        summary: "Database introspection".to_string(),
        description: "Enables AI tools to connect to PostgreSQL".to_string(),
        features: vec!["SQL queries".to_string()],
        installed: true,
        enabled: true,
        install_path: Some("storage/installed/postgres".to_string()),
        tools: Some(vec![PluginTool {
            name: "postgres_execute_query".to_string(),
            description: "Executes SQL query".to_string(),
            parameters: None,
        }]),
        change_notes: Some("v2.4.1: Partitioned tables".to_string()),
        category: Some("Database".to_string()),
        runtime: Some("python".to_string()),
        download_url: None,
        env_requirements: Some(vec![PluginEnvRequirement {
            key: "PG_HOST".to_string(),
            label: "Host".to_string(),
            required: Some(true),
            default: Some("127.0.0.1".to_string()),
            field_type: Some("text".to_string()),
        }]),
        configured_env: None,
    };

    let json = serde_json::to_string(&item).expect("Failed to serialize PluginItem");
    assert!(json.contains("postgres-mcp"));
    assert!(json.contains("PostgreSQL Explorer"));

    let deserialized: PluginItem = serde_json::from_str(&json).expect("Failed to deserialize PluginItem");
    assert_eq!(deserialized.id, "postgres-mcp");
    assert_eq!(deserialized.rating, 4.9);
}

#[test]
fn test_catalog_response_serialization() {
    let resp = CatalogResponse {
        total: 1,
        servers: vec![],
    };
    let json = serde_json::to_string(&resp).unwrap();
    assert!(json.contains("\"total\":1"));
}
