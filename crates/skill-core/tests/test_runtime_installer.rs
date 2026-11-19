use skill_core::runtime_installer::RuntimeInstaller;

#[test]
fn test_find_uv_binary() {
    let uv_opt = RuntimeInstaller::find_uv_binary();
    assert!(uv_opt.is_some(), "Expected bundled uv.exe to be discovered");
    let path = uv_opt.unwrap();
    assert!(path.exists(), "Discovered uv.exe path must physically exist");
    println!("Discovered uv.exe at: {}", path.display());
}

#[test]
fn test_provision_runtime_empty_skill_skips_python() {
    let temp = tempfile::tempdir().unwrap();
    let res = RuntimeInstaller::provision_runtime(temp.path(), None);
    assert!(res.is_ok());
    assert!(res.unwrap().is_none(), "Skill without scripts or requirements should skip venv");
}

#[test]
fn test_provision_runtime_with_scripts_creates_venv() {
    let temp = tempfile::tempdir().unwrap();
    let scripts_dir = temp.path().join("scripts");
    std::fs::create_dir_all(&scripts_dir).unwrap();
    std::fs::write(scripts_dir.join("main.py"), "print('hello from skill')").unwrap();

    let res = RuntimeInstaller::provision_runtime(temp.path(), None);
    assert!(res.is_ok(), "Provisioning venv must succeed: {:?}", res.err());
    let py_opt = res.unwrap();
    assert!(py_opt.is_some(), "Expected python.exe to be provisioned");
    let py_path = py_opt.unwrap();
    assert!(py_path.exists(), "Virtualenv python.exe must exist: {}", py_path.display());
    println!("Successfully provisioned isolated venv at: {}", py_path.display());
}
