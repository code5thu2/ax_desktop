use std::path::PathBuf;

/// Opens the modern Windows 11 Common Item Dialog to pick a folder.
/// Operates 100% in-process via native COM IFileDialog without spawning any console/PowerShell window.
pub fn pick_folder(title: Option<&str>) -> Option<PathBuf> {
    let mut dialog = rfd::FileDialog::new();
    if let Some(t) = title {
        dialog = dialog.set_title(t);
    }
    dialog.pick_folder()
}
