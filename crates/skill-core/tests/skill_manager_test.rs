use skill_core::skill_manager::SkillManager;
use skill_core::synchronizer::{read_skill_name_from_md, sync_disabled_skills};
use tempfile::tempdir;
use std::fs;

#[test]
fn test_read_skill_name_from_frontmatter() {
    let dir = tempdir().unwrap();
    let skill_dir = dir.path().join("my-skill");
    fs::create_dir_all(&skill_dir).unwrap();

    let skill_md = skill_dir.join("SKILL.md");
    fs::write(&skill_md, "---\nname: \"Super Assistant\"\nversion: 1\n---\nBody").unwrap();

    let name = read_skill_name_from_md(&skill_dir);
    assert_eq!(name, "Super Assistant");
}

#[test]
fn test_sync_disabled_skills() {
    let dir = tempdir().unwrap();
    let config_path = dir.path().join("config.json");

    // Add to disabled
    sync_disabled_skills(&config_path, "Super Assistant", true).expect("Failed sync 1");
    let content = fs::read_to_string(&config_path).unwrap();
    assert!(content.contains("Super Assistant"));

    // Remove from disabled
    sync_disabled_skills(&config_path, "Super Assistant", false).expect("Failed sync 2");
    let content2 = fs::read_to_string(&config_path).unwrap();
    assert!(!content2.contains("Super Assistant"));
}

#[test]
fn test_skill_lifecycle_install_toggle_uninstall() {
    let dir = tempdir().unwrap();
    let global_skills_root = dir.path().join("aipro/skills");
    let config_path = dir.path().join("aipro/config.json");
    let installed_json = dir.path().join("installed.json");

    let manager = SkillManager::new(global_skills_root, installed_json, config_path);

    // 1. Install
    let mock_zip_bytes = {
        let mut buf = Vec::new();
        let mut zip = zip::ZipWriter::new(std::io::Cursor::new(&mut buf));
        zip.start_file("SKILL.md", zip::write::SimpleFileOptions::default()).unwrap();
        std::io::Write::write_all(&mut zip, b"---\nname: test-skill\n---\nHello").unwrap();
        zip.finish().unwrap();
        buf
    };

    let res = manager.install(101, "test-skill", 1, "global", None, &mock_zip_bytes);
    assert!(res.is_ok());

    // Verify installed
    let installed = manager.list_installed();
    assert_eq!(installed.len(), 1);
    assert_eq!(installed[0].name, "test-skill");
    assert!(installed[0].enabled);

    // 2. Toggle disabled
    let toggle_res = manager.toggle(101, false, "global", None);
    assert!(toggle_res.is_ok());
    let installed_after_toggle = manager.list_installed();
    assert!(!installed_after_toggle[0].enabled);

    // 3. Uninstall
    let uninst_res = manager.uninstall(101, "global", None);
    assert!(uninst_res.is_ok());
    let installed_after_uninst = manager.list_installed();
    assert!(installed_after_uninst.is_empty());
}

#[test]
fn test_clone_skill_by_name_and_repair() {
    let dir = tempdir().unwrap();
    let global_skills_root = dir.path().join("aipro/skills");
    let config_path = dir.path().join("aipro/config.json");
    let installed_json = dir.path().join("installed.json");
    let src_proj = dir.path().join("src_project");
    let dst_proj = dir.path().join("dst_project");

    let manager = SkillManager::new(global_skills_root, installed_json, config_path);

    // Create a skill folder with custom name in src_project/.aipro/skills/custom-id-999
    let src_skill_dir = src_proj.join(".aipro/skills/custom-id-999");
    fs::create_dir_all(&src_skill_dir).unwrap();
    fs::write(
        src_skill_dir.join("SKILL.md"),
        "---\nname: Custom Database Tool\nid: 999\n---\n# Doc",
    ).unwrap();

    let clone_res = manager.clone_skill(
        102,
        Some("Custom Database Tool"),
        src_proj.to_str().unwrap(),
        dst_proj.to_str().unwrap(),
    );
    assert!(clone_res.is_ok(), "Clone failed: {:?}", clone_res.err());

    // Verify destination exists and has SKILL.md
    let dst_skill_md = dst_proj.join(".aipro/skills/102/SKILL.md");
    assert!(dst_skill_md.exists());

    // Verify source project was auto-repaired to also have standard folder 102
    let repaired_src_md = src_proj.join(".aipro/skills/102/SKILL.md");
    assert!(repaired_src_md.exists());
}
