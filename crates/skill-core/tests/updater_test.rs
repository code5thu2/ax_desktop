use skill_core::updater::{
    check_github_release_available, find_best_windows_asset, generate_restart_batch_script,
    get_github_token, version_gt, GITHUB_REPO,
};
use shared_types::models::{GithubAsset, GithubRelease};
use std::path::Path;

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

#[test]
fn test_find_best_windows_asset() {
    let rel = GithubRelease {
        tag_name: "v1.2.0".to_string(),
        name: Some("Release 1.2.0".to_string()),
        body: None,
        prerelease: false,
        published_at: None,
        assets: vec![
            GithubAsset {
                name: "source-code.zip".to_string(),
                browser_download_url: "https://example.com/source.zip".to_string(),
                size: 100,
            },
            GithubAsset {
                name: "AX_Desktop_1.2.0_x64-setup.exe".to_string(),
                browser_download_url: "https://example.com/setup.exe".to_string(),
                size: 25000000,
            },
            GithubAsset {
                name: "desktop.exe".to_string(),
                browser_download_url: "https://example.com/desktop.exe".to_string(),
                size: 15000000,
            },
        ],
    };

    let best = find_best_windows_asset(&rel);
    assert!(best.is_some());
    assert_eq!(best.unwrap().name, "AX_Desktop_1.2.0_x64-setup.exe");
}

#[test]
fn test_updater_constants_and_script() {
    assert_eq!(GITHUB_REPO, "code5thu2/ax_desktop");
    assert!(get_github_token().starts_with("github_pat_"));

    let script = generate_restart_batch_script(
        Path::new("C:\\temp\\update-setup.exe"),
        Path::new("C:\\apps\\desktop.exe"),
    );
    assert!(script.contains("C:\\temp\\update-setup.exe"));
    assert!(script.contains("C:\\apps\\desktop.exe"));
    assert!(script.contains("/S /UPDATE /R"));
}

#[test]
fn test_github_api_json_deserialization() {
    let raw_json = r#"[
        {
            "tag_name": "v1.0.1",
            "name": "AX Desktop v1.0.1",
            "body": "Test release notes",
            "draft": false,
            "prerelease": false,
            "published_at": "2026-11-08T18:19:04Z",
            "assets": [
                {
                    "name": "AX_Desktop_1.0.1_x64-setup.exe",
                    "size": 6247561,
                    "browser_download_url": "https://github.com/code5thu2/ax_desktop/releases/download/v1.0.1/AX_Desktop_1.0.1_x64-setup.exe"
                }
            ]
        }
    ]"#;

    let releases: Vec<GithubRelease> = serde_json::from_str(raw_json).expect("Failed to deserialize GitHub releases");
    assert_eq!(releases.len(), 1);
    assert_eq!(releases[0].tag_name, "v1.0.1");
    assert_eq!(releases[0].assets.len(), 1);
    assert_eq!(releases[0].assets[0].name, "AX_Desktop_1.0.1_x64-setup.exe");
    assert_eq!(releases[0].assets[0].browser_download_url, "https://github.com/code5thu2/ax_desktop/releases/download/v1.0.1/AX_Desktop_1.0.1_x64-setup.exe");
    assert_eq!(releases[0].assets[0].size, 6247561);

    let update = check_github_release_available(&releases, "1.0.0");
    assert!(update.is_some());
    assert_eq!(update.unwrap().tag_name, "v1.0.1");
}
