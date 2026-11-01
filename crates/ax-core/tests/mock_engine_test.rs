use ax_core::mock_engine::MockEngine;

#[test]
fn test_mock_auth_flow() {
    let engine = MockEngine::new();

    // Request OTP
    let otp_resp = engine.request_otp("test@aipro.vn");
    assert!(otp_resp.is_ok());

    // Verify OTP
    let verify_resp = engine.verify_otp("test@aipro.vn", "123456");
    assert!(verify_resp.is_ok());

    // Invalid OTP fails
    let verify_bad = engine.verify_otp("test@aipro.vn", "000000");
    assert!(verify_bad.is_err());

    // Login
    let login_resp = engine.login("test@aipro.vn", "secret123");
    assert!(login_resp.is_ok());
    let tokens = login_resp.unwrap();
    assert!(!tokens.access_token.is_empty());
    assert_eq!(tokens.user.unwrap().email, "test@aipro.vn");
}

#[test]
fn test_mock_marketplace_flow() {
    let engine = MockEngine::new();

    let list = engine.fetch_skills(None, 1, 20);
    assert!(!list.is_empty());
    assert!(list.iter().any(|s| s.name.contains("AI") || s.name.contains("Assistant")));

    let detail = engine.get_skill_detail(list[0].id);
    assert!(detail.is_ok());
    let detail_val = detail.unwrap();
    assert_eq!(detail_val.id, list[0].id);

    let versions = engine.get_skill_versions(list[0].id);
    assert!(!versions.is_empty());

    // Download mock ZIP contains valid SKILL.md
    let zip_bytes = engine.generate_skill_zip(list[0].id, "my-skill");
    assert!(zip_bytes.is_ok());
    let bytes = zip_bytes.unwrap();
    assert!(!bytes.is_empty());
}

#[test]
fn test_mock_mcp_catalog_flow() {
    let engine = MockEngine::new();
    let mcp_servers = engine.fetch_mcp_catalog();
    assert!(!mcp_servers.is_empty());
    assert!(mcp_servers.iter().any(|s| s.id.contains("mcp") || s.vendor.contains("Lab")));
}
