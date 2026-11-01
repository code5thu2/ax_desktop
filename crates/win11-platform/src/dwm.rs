use std::ffi::c_void;
use windows_sys::Win32::Foundation::HWND;
use windows_sys::Win32::Graphics::Dwm::{
    DwmSetWindowAttribute, DWMWA_BORDER_COLOR, DWMWA_CAPTION_COLOR,
    DWMWA_USE_IMMERSIVE_DARK_MODE,
};

/// Applies Windows 11 immersive dark mode and optional custom caption/border colors to a window.
pub fn apply_dark_titlebar(hwnd: isize, is_dark: bool) -> Result<(), String> {
    if hwnd == 0 {
        return Err("Invalid HWND".to_string());
    }

    let hwnd = hwnd as HWND;
    let dark_val: i32 = if is_dark { 1 } else { 0 };

    unsafe {
        let hr = DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE as u32,
            &dark_val as *const i32 as *const c_void,
            std::mem::size_of::<i32>() as u32,
        );

        if hr != 0 {
            return Err(format!("DwmSetWindowAttribute failed with HRESULT 0x{:08X}", hr));
        }

        // Apply dark caption background (0x001E1E1E) and border (0x002D2D2D) if dark mode
        if is_dark {
            // Windows COLORREF is 0x00BBGGRR
            let caption_color: u32 = 0x001E1E1E;
            let _ = DwmSetWindowAttribute(
                hwnd,
                DWMWA_CAPTION_COLOR as u32,
                &caption_color as *const u32 as *const c_void,
                std::mem::size_of::<u32>() as u32,
            );

            let border_color: u32 = 0x002D2D2D;
            let _ = DwmSetWindowAttribute(
                hwnd,
                DWMWA_BORDER_COLOR as u32,
                &border_color as *const u32 as *const c_void,
                std::mem::size_of::<u32>() as u32,
            );
        }

        Ok(())
    }
}
