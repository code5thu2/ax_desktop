use shared_types::models::GithubRelease;

fn clean_version_segments(v: &str) -> Vec<u64> {
    let cleaned = v
        .trim()
        .trim_start_matches("ax-desktop-")
        .trim_start_matches('v');

    cleaned
        .split('.')
        .map(|seg| {
            let digits: String = seg.chars().take_while(|c| c.is_ascii_digit()).collect();
            digits.parse::<u64>().unwrap_or(0)
        })
        .collect()
}

/// Compares two semver strings numerically: returns true if a > b.
/// Supports versions like "1.10.0" > "1.2.0", "v2.0.0", "ax-desktop-v1.0.22".
pub fn version_gt(a: &str, b: &str) -> bool {
    let segs_a = clean_version_segments(a);
    let segs_b = clean_version_segments(b);

    let max_len = segs_a.len().max(segs_b.len());
    for i in 0..max_len {
        let val_a = segs_a.get(i).copied().unwrap_or(0);
        let val_b = segs_b.get(i).copied().unwrap_or(0);
        if val_a > val_b {
            return true;
        } else if val_a < val_b {
            return false;
        }
    }
    false
}

/// Checks list of releases from GitHub and returns latest release if newer than current_version.
pub fn check_github_release_available(releases: &[GithubRelease], current_version: &str) -> Option<GithubRelease> {
    let mut latest: Option<&GithubRelease> = None;

    for rel in releases.iter().filter(|r| !r.prerelease) {
        match latest {
            None => {
                if version_gt(&rel.tag_name, current_version) {
                    latest = Some(rel);
                }
            }
            Some(curr) => {
                if version_gt(&rel.tag_name, &curr.tag_name) && version_gt(&rel.tag_name, current_version) {
                    latest = Some(rel);
                }
            }
        }
    }

    latest.cloned()
}

/// Asynchronously fetches releases from GitHub API
pub async fn fetch_github_releases(repo: &str) -> Result<Vec<GithubRelease>, String> {
    let url = format!("https://api.github.com/repos/{}/releases", repo);
    let client = reqwest::Client::builder()
        .user_agent("AX-Desktop")
        .timeout(std::time::Duration::from_secs(10))
        .build()
        .map_err(|e| e.to_string())?;

    let res = client
        .get(&url)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    if !res.status().is_success() {
        return Err(format!("GitHub API error: status {}", res.status()));
    }

    let releases: Vec<GithubRelease> = res.json().await.map_err(|e| e.to_string())?;
    Ok(releases)
}
