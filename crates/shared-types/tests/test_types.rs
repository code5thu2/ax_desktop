use shared_types::models::{PluginEnvRequirement, PluginItem, PluginTool, CatalogResponse};

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
