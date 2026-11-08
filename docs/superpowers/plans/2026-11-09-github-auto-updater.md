# GitHub Auto-Updater Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement automated GitHub Releases auto-update for `code5thu2/ax_desktop` using hardcoded Personal Access Token (`[CONFIGURED_PAT]`). When a new release tag is detected, the UI prompts an update popup; clicking "Cập nhật ngay" streams the download with a live progress bar, silently applies the update on Windows, and automatically restarts the application.

**Tech Stack:** Rust (Tauri v2, reqwest, tokio), Vue 3, PrimeVue 4, Tailwind CSS, Windows Batch Scripting.

---

### Task 1: Rust Backend Updater Core (`skill-core`)

**Files:**
- Modify: `crates/skill-core/src/updater.rs`
- Test: `crates/skill-core/tests/updater_test.rs`

- [ ] **Step 1: Write unit tests in `updater_test.rs`** for token header formatting, version comparison, and asset URL resolution.
- [ ] **Step 2: Update `crates/skill-core/src/updater.rs`**:
  - Add `pub fn get_github_token() -> String;`
  - Add `pub const GITHUB_REPO: &str = "code5thu2/ax_desktop";`
  - Update `fetch_github_releases` to attach the Bearer token.
  - Implement `download_release_asset_with_progress` streaming chunks with callback `Fn(u64, u64)`.
  - Implement `apply_update_and_restart(installer_path: &Path, current_exe: &Path) -> Result<(), String>`.
- [ ] **Step 3: Run `cargo test -p skill-core`** and confirm tests pass.

---

### Task 2: Tauri IPC Commands & Event Streaming (`apps/desktop`)

**Files:**
- Modify: `apps/desktop/src/commands.rs`
- Modify: `apps/desktop/src/lib.rs`

- [ ] **Step 1: In `apps/desktop/src/commands.rs`**:
  - Update `check_for_update` to return release details and selected asset info.
  - Implement `#[tauri::command] pub async fn download_and_install_update(app: AppHandle, download_url: String) -> Result<(), String>`:
    - Streams download into `%TEMP%\ax_desktop_update.exe`.
    - Emits Tauri event `update-progress` with `{ "downloaded": u64, "total": u64, "percent": u32 }`.
    - Spawns background Windows batch script that executes installer and restarts `desktop.exe`.
    - Calls `app.exit(0)`.
- [ ] **Step 2: Register `commands::download_and_install_update`** in `apps/desktop/src/lib.rs`.
- [ ] **Step 3: Run `cargo check -p desktop`** to ensure clean compilation.

---

### Task 3: Frontend Bridge, Store & Update Dialog UI

**Files:**
- Modify: `frontend/src/services/nativeBridge.ts`
- Modify: `frontend/src/features/skills/stores/skillStore.ts`
- Modify: `frontend/src/features/skills/components/UpdateDialog.vue`

- [ ] **Step 1: In `nativeBridge.ts`**:
  - Add `downloadAndInstallUpdate(downloadUrl: string): Promise<void>` calling Tauri IPC `download_and_install_update` with mock fallback for web.
- [ ] **Step 2: In `skillStore.ts`**:
  - Add reactive states: `isUpdating`, `updateProgress`, `updateStatusText`, `updateError`.
  - Add `applyUpdate()` action listening to `update-progress` events.
- [ ] **Step 3: In `UpdateDialog.vue`**:
  - Add animated progress bar (0% -> 100%), downloaded MB / total MB indicator.
  - Change button state to "Đang tải bản cập nhật..." with spinner.
  - Update footer actions: disable dismiss while updating, provide retry / error state.
- [ ] **Step 4: Run frontend tests & build**:
  - `npm --prefix frontend run test`
  - `npm --prefix frontend run build`

---

### Task 4: End-to-End Verification

- [ ] **Step 1: Run `cargo build --release -p desktop`** to produce the final release binary.
- [ ] **Step 2: Verify simulated and real GitHub API requests with the hardcoded token**.
