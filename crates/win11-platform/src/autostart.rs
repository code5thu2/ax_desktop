use std::ffi::OsStr;
use std::os::windows::ffi::OsStrExt;
use std::ptr;
use windows_sys::Win32::Foundation::ERROR_SUCCESS;
use windows_sys::Win32::System::Registry::{
    RegCloseKey, RegDeleteValueW, RegOpenKeyExW, RegQueryValueExW, RegSetValueExW,
    HKEY_CURRENT_USER, KEY_READ, KEY_WRITE, REG_SZ,
};

const RUN_KEY_PATH: &str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run";

fn to_wide_null(s: &str) -> Vec<u16> {
    OsStr::new(s).encode_wide().chain(Some(0)).collect()
}

pub fn is_run_at_startup_configured(app_name: &str) -> bool {
    let wide_key = to_wide_null(RUN_KEY_PATH);
    let wide_name = to_wide_null(app_name);

    unsafe {
        let mut hkey = ptr::null_mut();
        if RegOpenKeyExW(HKEY_CURRENT_USER, wide_key.as_ptr(), 0, KEY_READ, &mut hkey)
            != ERROR_SUCCESS
        {
            return false;
        }

        let mut val_type = 0u32;
        let mut val_size = 0u32;
        let res = RegQueryValueExW(
            hkey,
            wide_name.as_ptr(),
            ptr::null_mut(),
            &mut val_type,
            ptr::null_mut(),
            &mut val_size,
        );

        RegCloseKey(hkey);
        res == ERROR_SUCCESS && val_size > 0
    }
}

pub fn set_run_at_startup(app_name: &str, enable: bool) -> Result<(), String> {
    let current_exe = if enable {
        Some(std::env::current_exe().map_err(|e| e.to_string())?)
    } else {
        None
    };

    let wide_key = to_wide_null(RUN_KEY_PATH);
    let wide_name = to_wide_null(app_name);

    unsafe {
        let mut hkey = ptr::null_mut();
        if RegOpenKeyExW(HKEY_CURRENT_USER, wide_key.as_ptr(), 0, KEY_WRITE, &mut hkey)
            != ERROR_SUCCESS
        {
            return Err("Failed to open HKCU Run registry key for writing".to_string());
        }

        let result = if let Some(exe) = current_exe {
            let exe_str = format!("\"{}\" --autostart", exe.to_string_lossy());
            let wide_val = to_wide_null(&exe_str);

            let res = RegSetValueExW(
                hkey,
                wide_name.as_ptr(),
                0,
                REG_SZ,
                wide_val.as_ptr() as *const u8,
                (wide_val.len() * 2) as u32,
            );
            if res == ERROR_SUCCESS {
                Ok(())
            } else {
                Err(format!("RegSetValueExW failed with code {}", res))
            }
        } else {
            let res = RegDeleteValueW(hkey, wide_name.as_ptr());
            if res == ERROR_SUCCESS || res == 2 {
                // 2 is ERROR_FILE_NOT_FOUND (already deleted)
                Ok(())
            } else {
                Err(format!("RegDeleteValueW failed with code {}", res))
            }
        };

        RegCloseKey(hkey);
        result
    }
}
