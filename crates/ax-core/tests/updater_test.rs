use ax_core::updater::{check_github_release_available, version_gt};
use shared_types::models::{GithubAsset, GithubRelease};

#[test]
fn test_version_gt_comparison() {
    assert!(version_gt("1.0.1", "1.0.0"));
    assert!(version_gt("1.10.0", "1.2.0"));
    assert!(version_gt("v2.0.0", "v1.9.9"));
    assert!(version_gt("ax-desktop-v1.0.22", "ax-desktop-v1.0.21"));
    assert!(!version_gt("1.0.0", "1.0.0"));
    assert!(!version_gt("1.0.0", "1.0.1"));
}

#[test]
fn test_check_github_release_available() {
    let releases = vec![
        GithubRelease {
            tag_name: "v1.0.1".to_string(),
            name: Some("Release 1.0.1".to_string()),
            body: Some("Notes".to_string()),
            prerelease: false,
            published_at: None,
            assets: vec![GithubAsset {
                name: "setup.exe".to_string(),
                browser_download_url: "https://example.com/setup.exe".to_string(),
                size: 5000,
            }],
        },
        GithubRelease {
            tag_name: "v1.0.0".to_string(),
            name: Some("Release 1.0.0".to_string()),
            body: None,
            prerelease: false,
            published_at: None,
            assets: vec![],
        },
    ];

    let update = check_github_release_available(&releases, "1.0.0");
    assert!(update.is_some());
    let u = update.unwrap();
    assert_eq!(u.tag_name, "v1.0.1");

    let no_update = check_github_release_available(&releases, "1.0.1");
    assert!(no_update.is_none());
}
