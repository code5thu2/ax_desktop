use mcp_core::catalog::CatalogManager;
use mcp_core::mock_runner::MockServerScanner;
use std::fs;

#[test]
fn test_catalog_search_and_filter() {
    let sample_json = r#"{
        "version": "1.0.0",
        "servers": [
            {
                "id": "excel-mcp",
                "name": "Excel MCP Spreadsheet Processor",
                "type": "mcp",
                "vendor": "Office Labs",
                "version": "1.0.0",
                "icon": "pi pi-file-excel",
                "rating": 4.8,
                "downloads": "12.3k",
                "summary": "Process excel sheets",
                "description": "Read and write xlsx files",
                "features": ["formulas"],
                "installed": true,
                "enabled": true,
                "category": "In-House Tools"
            },
            {
                "id": "postgres-mcp",
                "name": "PostgreSQL Database Explorer",
                "type": "mcp",
                "vendor": "DB Tools",
                "version": "2.0.0",
                "icon": "pi pi-database",
                "rating": 4.9,
                "downloads": "50.1k",
                "summary": "Query postgres database",
                "description": "Introspect tables and schemas",
                "features": ["query plan"],
                "installed": false,
                "enabled": false,
                "category": "Database"
            }
        ]
    }"#;

    let cm = CatalogManager::from_json_str(sample_json).expect("Failed to parse catalog JSON");
    
    // Search by name keyword
    let res = cm.search("excel", None);
    assert_eq!(res.len(), 1);
    assert_eq!(res[0].id, "excel-mcp");

    // Filter by category
    let res_cat = cm.search("", Some("database"));
    assert_eq!(res_cat.len(), 1);
    assert_eq!(res_cat[0].id, "postgres-mcp");
}

#[test]
fn test_mock_server_scanner_external_dir() {
    // Create temporary external directory with a mock server
    let temp_dir = std::env::temp_dir().join("aipro_mock_mcp_test");
    let server_dir = temp_dir.join("mock_excel");
    fs::create_dir_all(&server_dir).unwrap();
    
    let manifest_path = server_dir.join("manifest.json");
    fs::write(&manifest_path, r#"{
        "id": "mock_excel",
        "name": "Mock Excel Server",
        "version": "1.0.0",
        "summary": "External mock for testing",
        "tools": [{"name": "mock_tool", "description": "test"}]
    }"#).unwrap();

    let discovered = MockServerScanner::scan_external_dir(&temp_dir);
    assert!(!discovered.is_empty(), "Should discover mock server in external directory");
    let found = discovered.iter().find(|s| s.id == "mock_excel");
    assert!(found.is_some());
    assert_eq!(found.unwrap().name, "Mock Excel Server");

    // Cleanup
    let _ = fs::remove_dir_all(&temp_dir);
}
