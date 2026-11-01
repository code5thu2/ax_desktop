use win11_platform::single_instance::SingleInstanceGuard;
use win11_platform::autostart::is_run_at_startup_configured;

#[test]
fn test_single_instance_mutex() {
    let mutex_name = "MCP_Studio_Test_Mutex_Unique_9988";
    let guard1 = SingleInstanceGuard::acquire(mutex_name);
    assert!(guard1.is_ok(), "First acquisition must succeed");

    let guard2 = SingleInstanceGuard::acquire(mutex_name);
    assert!(guard2.is_err(), "Second acquisition must fail while first is alive");

    drop(guard1);
    let guard3 = SingleInstanceGuard::acquire(mutex_name);
    assert!(guard3.is_ok(), "Third acquisition must succeed after first is dropped");
}

#[test]
fn test_autostart_check_does_not_crash() {
    // Checking whether an app is configured to autostart should return a bool without panicking
    let _ = is_run_at_startup_configured("NonExistentTestAppAIPRO");
}
