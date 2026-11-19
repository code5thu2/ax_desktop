use skill_core::runtime_installer::RuntimeInstaller;
use std::fs;
use std::process::Command;

#[test]
fn test_real_end_to_end_skill_provision_and_execution() {
    let temp = tempfile::tempdir().unwrap();
    let skill_dir = temp.path().join("demo-skill");
    let scripts_dir = skill_dir.join("scripts");
    fs::create_dir_all(&scripts_dir).unwrap();

    // 1. Create requirements.txt and Python script that imports pydantic_core
    fs::write(skill_dir.join("requirements.txt"), "pydantic-core\n").unwrap();
    fs::write(
        scripts_dir.join("test_import.py"),
        "import pydantic_core\nprint(f'PROD_VERIFIED: pydantic_core {pydantic_core.__version__}')\n",
    )
    .unwrap();

    // 2. Read the real wheels zip generated from Central Server & Nexus
    let wheels_zip_path = std::env::temp_dir().join("demo-ai-math-wheels.zip");
    if !wheels_zip_path.exists() {
        eprintln!(
            "Skipping test_real_end_to_end_skill_provision_and_execution: fixture {} not found. This test runs when offline nexus wheels are available.",
            wheels_zip_path.display()
        );
        return;
    }
    let wheels_bytes = fs::read(&wheels_zip_path).unwrap();

    // 3. Provision runtime using RuntimeInstaller (Zero-Config, offline pip install from wheels)
    let py_res = RuntimeInstaller::provision_runtime(&skill_dir, Some(&wheels_bytes));
    assert!(py_res.is_ok(), "Provisioning must succeed: {:?}", py_res.err());

    let py_opt = py_res.unwrap();
    assert!(py_opt.is_some(), "Expected python.exe in isolated venv");
    let python_exe = py_opt.unwrap();
    assert!(python_exe.exists(), "Virtualenv python.exe must exist");

    // 4. Execute the script inside the isolated runtime!
    let output = Command::new(&python_exe)
        .arg(scripts_dir.join("test_import.py"))
        .output()
        .expect("Failed to execute python script in isolated venv");

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    println!("--- SCRIPT EXECUTION STDOUT ---\n{}", stdout);
    if !stderr.is_empty() {
        println!("--- SCRIPT EXECUTION STDERR ---\n{}", stderr);
    }

    assert!(output.status.success(), "Script execution must succeed");
    assert!(
        stdout.contains("PROD_VERIFIED: pydantic_core 2.50.4"),
        "Script stdout must confirm successful import of pydantic_core"
    );
    println!(">>> FULL END-TO-END VERIFICATION SUCCEEDED! <<<");
}
