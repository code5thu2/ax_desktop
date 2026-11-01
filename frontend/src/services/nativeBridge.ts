/**
 * Unified Native Bridge Adapter for AX Desktop
 * Automatically routes calls to Tauri v2 Native IPC if running in desktop shell,
 * or falls back seamlessly to Mock/HTTP Gateway in web browser mode.
 */

import type { CatalogResponse } from '@/types/generated/CatalogResponse'
import type { PortalStatus } from '@/types/generated/PortalStatus'
import type { Settings } from '@/types/generated/Settings'
import type { SkillItem } from '@/types/generated/SkillItem'
import type { SkillDetail } from '@/types/generated/SkillDetail'
import type { SkillVersionItem } from '@/types/generated/SkillVersionItem'
import type { InstalledPlugin } from '@/types/generated/InstalledPlugin'
import type { GithubRelease } from '@/types/generated/GithubRelease'
import type { AuthUser } from '@/types/generated/AuthUser'

export function isTauriEnvironment(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window
}

export async function invokeNative<T>(cmd: string, args: Record<string, any> = {}): Promise<T> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      return await invoke<T>(cmd, args)
    } catch (err: any) {
      console.warn(`[NativeBridge] Tauri invoke '${cmd}' failed:`, err)
      throw err
    }
  }
  throw new Error(`Command '${cmd}' requires Tauri environment`)
}

// In-memory mock storage for dev browser preview
let mockLoggedIn = false
let mockUser: AuthUser = {
  id: BigInt(1) as unknown as bigint,
  name: 'Lê Viết Thắng',
  email: 'thang@aipro.studio',
  avatar: undefined,
}

export const nativeBridge = {
  isTauri: isTauriEnvironment,

  // ==========================================
  // Auth Commands
  // ==========================================
  async login(payload: { email: string; password: string }): Promise<any> {
    if (isTauriEnvironment()) {
      return await invokeNative('login', { payload })
    }
    // Web mock fallback
    mockLoggedIn = true
    mockUser.email = payload.email
    return {
      tokens: { access_token: 'mock_token', token_type: 'Bearer', expires_in: 3600 },
      user: mockUser,
    }
  },

  async requestRegisterOtp(payload: { email: string; username: string; password: string }): Promise<string> {
    if (isTauriEnvironment()) {
      return await invokeNative('request_register_otp', { payload })
    }
    return '123456'
  },

  async verifyRegisterOtp(payload: { email: string; otp: string; username: string; password: string }): Promise<any> {
    if (isTauriEnvironment()) {
      return await invokeNative('verify_register_otp', { payload })
    }
    if (payload.otp !== '123456') {
      throw new Error('Mã OTP không chính xác. Mã hợp lệ cho môi trường thử nghiệm là 123456')
    }
    mockLoggedIn = true
    mockUser.email = payload.email
    mockUser.name = payload.username
    return {
      tokens: { access_token: 'mock_token', token_type: 'Bearer', expires_in: 3600 },
      user: mockUser,
    }
  },

  async logout(): Promise<void> {
    if (isTauriEnvironment()) {
      await invokeNative('logout')
      return
    }
    mockLoggedIn = false
  },

  async getStatus(): Promise<PortalStatus> {
    if (isTauriEnvironment()) {
      try {
        return await invokeNative<PortalStatus>('get_status')
      } catch (e) {
        console.warn('[NativeBridge] get_status failed, using fallback:', e)
      }
    }
    return {
      loggedIn: mockLoggedIn,
      user: mockLoggedIn ? mockUser : undefined,
      theme: 'dark',
      installed: [],
      recentProjects: ['D:/AI_Projects/FinanceAssistant', 'D:/AI_Projects/CodeReviewer'],
      rememberAccount: true,
      rememberedEmail: 'thang@aipro.studio',
    }
  },

  async getSettings(): Promise<Settings> {
    if (isTauriEnvironment()) {
      return await invokeNative<Settings>('get_settings')
    }
    return {
      theme: 'dark',
      recentProjects: ['D:/AI_Projects/FinanceAssistant'],
      rememberedEmail: 'thang@aipro.studio',
      rememberAccount: true,
    }
  },

  async updateSettings(payload: Settings): Promise<void> {
    if (isTauriEnvironment()) {
      await invokeNative('update_settings', { payload })
    }
  },

  // ==========================================
  // Skill Marketplace Commands
  // ==========================================
  async listMarketplaceSkills(query?: string, category?: string, tag?: string): Promise<SkillItem[]> {
    if (isTauriEnvironment()) {
      return await invokeNative<SkillItem[]>('list_marketplace_skills', { query, category, tag })
    }
    return [
      {
        id: BigInt(1) as unknown as bigint,
        name: 'vietnam-business-law-skills',
        description: 'Tự động tra cứu và phân tích luật doanh nghiệp, lao động và thuế Việt Nam với độ chính xác cao.',
        creatorName: 'AIPRO Law Lab',
        createdAt: '2026-10-01T08:00:00Z',
        status: 'published',
        scope: 'public',
        categories: ['Legal', 'Business'],
        stages: ['Production'],
        viewCount: BigInt(1250) as unknown as bigint,
        avgRating: 4.9,
        ratingCount: BigInt(48) as unknown as bigint,
        subscribed: false,
        installed: false,
        enabled: false,
        installedProjects: [],
        projectStates: {},
      },
      {
        id: BigInt(2) as unknown as bigint,
        name: 'frontend-design-master',
        description: 'Thiết kế giao diện PrimeVue & Tailwind chuẩn UX/UI chuyên nghiệp, loại bỏ jank và animation thừa.',
        creatorName: 'AIPRO Studio',
        createdAt: '2026-10-10T08:00:00Z',
        status: 'published',
        scope: 'public',
        categories: ['Frontend', 'UI'],
        stages: ['Production'],
        viewCount: BigInt(3400) as unknown as bigint,
        avgRating: 4.8,
        ratingCount: BigInt(112) as unknown as bigint,
        subscribed: true,
        installed: true,
        enabled: true,
        installScope: 'global',
        installedProjects: [],
        projectStates: {},
        installedVersion: 2,
      },
      {
        id: BigInt(3) as unknown as bigint,
        name: 'spring-boot-suite',
        description: 'Bộ công cụ phân tích Bean, Request Mappings, và chẩn đoán lỗi tự động cho Spring Boot.',
        creatorName: 'DevTools Corp',
        createdAt: '2026-09-15T08:00:00Z',
        status: 'published',
        scope: 'public',
        categories: ['Backend', 'Java'],
        stages: ['Production'],
        viewCount: BigInt(980) as unknown as bigint,
        avgRating: 4.7,
        ratingCount: BigInt(35) as unknown as bigint,
        subscribed: false,
        installed: false,
        enabled: false,
        installedProjects: [],
        projectStates: {},
      },
    ]
  },

  async getSkillDetail(name: string): Promise<SkillDetail> {
    if (isTauriEnvironment()) {
      return await invokeNative<SkillDetail>('get_skill_detail', { name })
    }
    return {
      id: BigInt(1) as unknown as bigint,
      name,
      description: 'Mô tả chi tiết về skill ' + name,
      creatorName: 'AIPRO Studio',
      createdAt: '2026-10-01T08:00:00Z',
      status: 'published',
      scope: 'public',
      categories: ['Productivity'],
      stages: ['Production'],
      viewCount: BigInt(100) as unknown as bigint,
      avgRating: 5.0,
      ratingCount: BigInt(12) as unknown as bigint,
      subscribed: false,
      installed: false,
      enabled: false,
      installedProjects: [],
      projectStates: {},
      version: 1,
      hashtags: ['productivity', 'ai'],
      files: [{ id: BigInt(1) as unknown as bigint, fileName: 'SKILL.md', fileSize: BigInt(1024) as unknown as bigint, createdAt: '2026-10-01T08:00:00Z' }],
      isCreator: false,
      canEdit: false,
      updatedAt: '2026-10-01T08:00:00Z',
    }
  },

  async listSkillVersions(name: string): Promise<SkillVersionItem[]> {
    if (isTauriEnvironment()) {
      return await invokeNative<SkillVersionItem[]>('list_skill_versions', { name })
    }
    return [
      {
        version: 1,
        name,
        description: 'Bản phát hành đầu tiên',
        publicScope: 'public',
        hashtags: ['initial'],
        creatorName: 'AIPRO Studio',
        createdAt: '2026-10-01T08:00:00Z',
        files: [],
      },
    ]
  },

  async listInstalledSkills(projectPath?: string): Promise<InstalledPlugin[]> {
    if (isTauriEnvironment()) {
      return await invokeNative<InstalledPlugin[]>('list_installed_skills', { projectPath })
    }
    return [
      {
        id: BigInt(1) as unknown as bigint,
        name: 'frontend-design-master',
        version: 2,
        scope: 'global',
        installedAt: '2026-10-10T08:00:00Z',
        enabled: true,
      },
    ]
  },

  async installSkill(name: string, version: number, targetDir: string, scope: string): Promise<InstalledPlugin> {
    if (isTauriEnvironment()) {
      return await invokeNative<InstalledPlugin>('install_skill', { name, version, targetDir, scope })
    }
    return {
      id: BigInt(Date.now()) as unknown as bigint,
      name,
      version,
      scope,
      installedAt: new Date().toISOString(),
      projectPath: scope === 'project' ? targetDir : undefined,
      enabled: true,
    }
  },

  async uninstallSkill(name: string, projectPath?: string): Promise<boolean> {
    if (isTauriEnvironment()) {
      return await invokeNative<boolean>('uninstall_skill', { name, projectPath })
    }
    return true
  },

  async toggleSkill(name: string, enabled: boolean, projectPath?: string): Promise<boolean> {
    if (isTauriEnvironment()) {
      return await invokeNative<boolean>('toggle_skill', { name, enabled, projectPath })
    }
    return true
  },

  async cloneSkill(sourceProject: string, targetProject: string, skillNames: string[]): Promise<InstalledPlugin[]> {
    if (isTauriEnvironment()) {
      return await invokeNative<InstalledPlugin[]>('clone_skill', { sourceProject, targetProject, skillNames })
    }
    return []
  },

  // ==========================================
  // System & Platform Commands
  // ==========================================
  async openAiproStudio(): Promise<string> {
    if (isTauriEnvironment()) {
      return await invokeNative<string>('open_aipro_studio')
    }
    return 'Đã kích hoạt khởi động AIPRO Studio trong chế độ thử nghiệm.'
  },

  async checkAppUpdate(currentVersion: string): Promise<GithubRelease | null> {
    if (isTauriEnvironment()) {
      return await invokeNative<GithubRelease | null>('check_app_update', { currentVersion })
    }
    return null
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

  async setTheme(isDark: boolean): Promise<void> {
    if (isTauriEnvironment()) {
      try {
        await invokeNative('set_theme', { isDark })
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
      name: 'AX Desktop',
      version: '1.0.0',
      platform: isTauriEnvironment() ? 'Tauri v2 Native' : 'Web Browser Dev',
    }
  },

  // ==========================================
  // Legacy / MCP Catalog Commands
  // ==========================================
  async getCatalog(registryUrl: string, query?: string, category?: string): Promise<CatalogResponse> {
    if (isTauriEnvironment()) {
      try {
        return await invokeNative<CatalogResponse>('get_catalog', { query, category })
      } catch (e) {
        console.warn('[NativeBridge] get_catalog invoke failed, falling back to fetch:', e)
      }
    }

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
}
