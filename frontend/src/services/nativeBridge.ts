/**
 * Unified Native Bridge Adapter
 * Automatically routes calls to Tauri v2 Native IPC if running in desktop shell,
 * or falls back seamlessly to HTTP Gateway (http://127.0.0.1:8000) in web browser mode.
 */

import type { CatalogResponse } from '@/types/generated/CatalogResponse'

export function isTauriEnvironment(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window
}

export async function invokeNative<T>(cmd: string, args: Record<string, any> = {}): Promise<T> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      return await invoke<T>(cmd, args)
    } catch (err) {
      console.warn(`[NativeBridge] Tauri invoke '${cmd}' failed, falling back to HTTP:`, err)
    }
  }
  throw new Error(`Command '${cmd}' requires Tauri environment or fallback`)
}

export const nativeBridge = {
  isTauri: isTauriEnvironment,

  async getCatalog(registryUrl: string, query?: string, category?: string): Promise<CatalogResponse> {
    if (isTauriEnvironment()) {
      try {
        return await invokeNative<CatalogResponse>('get_catalog', { query, category })
      } catch (e) {
        console.warn('[NativeBridge] get_catalog invoke failed, falling back to fetch:', e)
      }
    }

    // Fallback to HTTP Gateway API
    const params = new URLSearchParams()
    if (query) params.append('q', query)
    if (category) params.append('category', category)
    const qs = params.toString() ? `?${params.toString()}` : ''

    const res = await fetch(`${registryUrl}/api/v1/catalog${qs}`)
    if (!res.ok) {
      throw new Error(`Failed to fetch catalog: HTTP ${res.status}`)
    }
    return await res.json()
  },

  async setTheme(isDark: boolean): Promise<void> {
    if (isTauriEnvironment()) {
      try {
        await invokeNative('set_theme', { isDark })
        return
      } catch {
        // Fallback or ignore
      }
    }

    // Fallback to legacy pywebview if present
    if (typeof window !== 'undefined') {
      const api = (window as any).pywebview?.api
      if (api && typeof api.set_theme === 'function') {
        api.set_theme(isDark)
      }
    }
  },

  async isAutostartEnabled(): Promise<boolean> {
    if (isTauriEnvironment()) {
      try {
        return await invokeNative<boolean>('is_autostart_enabled')
      } catch {
        return false
      }
    }
    return false
  },

  async setAutostart(enable: boolean): Promise<void> {
    if (isTauriEnvironment()) {
      try {
        await invokeNative('set_autostart', { enable })
      } catch {
        // Ignore
      }
    }
  },

  async getAppInfo(): Promise<any> {
    if (isTauriEnvironment()) {
      try {
        return await invokeNative('get_app_info')
      } catch {
        // Fallback
      }
    }
    return {
      name: 'MCP Protocol Studio',
      version: '1.0.0',
      platform: isTauriEnvironment() ? 'Tauri v2 Native' : 'Web/PyWebView',
    }
  }
}
