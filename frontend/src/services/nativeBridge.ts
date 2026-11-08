/**
 * Unified Native Bridge Adapter for AX Desktop
 * Maps 1:1 with Tauri v2 Native IPC commands per AX Desktop API Reference.
 * Provides fallback mock responses in browser/test mode.
 */

import type { CatalogResponse } from '@/types/generated/CatalogResponse'
import type { PortalStatus } from '@/types/generated/PortalStatus'
import type { SkillItem } from '@/types/generated/SkillItem'
import type { SkillDetail } from '@/types/generated/SkillDetail'
import type { SkillVersionItem } from '@/types/generated/SkillVersionItem'
import type { InstalledPlugin } from '@/types/generated/InstalledPlugin'
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

export async function listenToEvent<T>(
  event: string,
  handler: (payload: T) => void
): Promise<() => void> {
  if (isTauriEnvironment()) {
    try {
      const { listen } = await import('@tauri-apps/api/event')
      const unlisten = await listen<T>(event, (e) => handler(e.payload))
      return unlisten
    } catch (err) {
      console.warn(`[NativeBridge] Failed to listen to '${event}':`, err)
    }
  }
  return () => {}
}

export interface UpdateProgressPayload {
  downloaded: number
  total: number
  percent: number
  status: 'downloading' | 'installing' | 'ready' | 'error'
  error?: string
}

export interface CheckUpdateResponse {
  status: string
  updateAvailable?: boolean
  latestVersion?: string
  currentVersion?: string
  releaseName?: string
  releaseNotes?: string
  assetName?: string
  assetSize?: number
  downloadUrl?: string
  error?: string
}

// In-memory mock storage for dev browser preview
let mockLoggedIn = false
let mockUser: AuthUser = {
  id: BigInt(1) as unknown as bigint,
  name: 'Lê Viết Thắng',
  email: 'thang@aipro.studio',
  avatar: undefined,
}

let mockSkills: SkillItem[] = [
  {
    id: BigInt(1) as unknown as bigint,
    name: 'vietnam-business-law-skills',
    description: 'Tự động tra cứu và phân tích luật doanh nghiệp, lao động và thuế Việt Nam với độ chính xác cao.',
    creatorName: 'AIPRO Law Lab',
    createdAt: '2026-10-01T08:00:00Z',
    status: 'APPROVED',
    scope: 'PUBLIC',
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
    status: 'APPROVED',
    scope: 'PUBLIC',
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
    status: 'APPROVED',
    scope: 'PUBLIC',
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

let mockInstalled: InstalledPlugin[] = [
  {
    id: BigInt(101) as unknown as bigint,
    name: 'AI Code Assistant',
    version: 1,
    scope: 'global',
    installedAt: '2026-11-02T02:00:00Z',
    enabled: true,
  },
  {
    id: BigInt(101) as unknown as bigint,
    name: 'AI Code Assistant',
    version: 1,
    scope: 'project',
    projectPath: 'D:/baoao',
    installedAt: '2026-11-02T02:00:00Z',
    enabled: true,
  },
  {
    id: BigInt(102) as unknown as bigint,
    name: 'Smart Database Query & Introspection',
    version: 1,
    scope: 'project',
    projectPath: 'D:/baoao',
    installedAt: '2026-11-02T02:00:00Z',
    enabled: true,
  },
  {
    id: BigInt(103) as unknown as bigint,
    name: 'Multi-Language Legal Document Analyzer',
    version: 1,
    scope: 'project',
    projectPath: 'C:/Users/levie/Desktop/ison',
    installedAt: '2026-11-02T02:00:00Z',
    enabled: true,
  },
  {
    id: BigInt(102) as unknown as bigint,
    name: 'Smart Database Query & Introspection',
    version: 1,
    scope: 'project',
    projectPath: 'C:/Users/levie/Desktop/ASAP',
    installedAt: '2026-11-02T02:00:00Z',
    enabled: true,
  },
  {
    id: BigInt(102) as unknown as bigint,
    name: 'Smart Database Query & Introspection',
    version: 1,
    scope: 'global',
    installedAt: '2026-11-02T02:00:00Z',
    enabled: false,
  },
]

let mockRecentProjects: string[] = [
  'D:/AI_Projects/FinanceAssistant',
  'D:/AI_Projects/CodeReviewer',
]

export const nativeBridge = {
  isTauri: isTauriEnvironment,

  // ==========================================
  // A.1 Auth IPC Commands
  // ==========================================
  async login(payload: { email: string; password: string }): Promise<{ ok: boolean; user?: AuthUser; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('login', { payload })
    }
    mockLoggedIn = true
    mockUser.email = payload.email
    return { ok: true, user: mockUser }
  },

  async requestRegisterOtp(email: string): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('request_register_otp', { email })
    }
    return { ok: true }
  },

  async verifyRegisterOtp(email: string, otp: string): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('verify_register_otp', { email, otp })
    }
    if (otp !== '123456') {
      throw new Error('Mã OTP không chính xác. Mã hợp lệ cho môi trường thử nghiệm là 123456')
    }
    return { ok: true }
  },

  async register(payload: { name: string; email: string; password: string; confirmPassword: string }): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('register', { payload })
    }
    mockLoggedIn = true
    mockUser.email = payload.email
    mockUser.name = payload.name
    return { ok: true }
  },

  async requestForgotOtp(email: string): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('request_forgot_otp', { email })
    }
    return { ok: true }
  },

  async verifyForgotOtp(email: string, otp: string): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('verify_forgot_otp', { email, otp })
    }
    return { ok: true }
  },

  async resetPassword(email: string, newPassword: string): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('reset_password', { payload: { email, new_password: newPassword } })
    }
    return { ok: true }
  },

  async logout(): Promise<{ ok: boolean }> {
    if (isTauriEnvironment()) {
      return await invokeNative('logout')
    }
    mockLoggedIn = false
    return { ok: true }
  },

  async showWindow(): Promise<void> {
    if (isTauriEnvironment()) {
      await invokeNative('show_window')
    }
  },

  // ==========================================
  // A.2 Status & Marketplace Commands
  // ==========================================
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
      installed: mockInstalled,
      recentProjects: mockRecentProjects,
      rememberAccount: true,
      rememberedEmail: 'thang@aipro.studio',
    }
  },

  async fetchSkills(params: { page?: number; pageSize?: number; skillName?: string; categoryIds?: string[] } = {}): Promise<{ items: SkillItem[]; totalCount: number }> {
    if (isTauriEnvironment()) {
      return await invokeNative<{ items: SkillItem[]; totalCount: number }>('fetch_skills', {
        query: params.skillName,
        page: params.page,
        pageSize: params.pageSize,
      })
    }
    let list = mockSkills
    if (params.skillName) {
      const q = params.skillName.toLowerCase()
      list = list.filter((s) => s.name.toLowerCase().includes(q) || s.description.toLowerCase().includes(q))
    }
    return { items: list, totalCount: list.length }
  },

  async listMarketplaceSkills(query?: string, _category?: string, _tag?: string): Promise<SkillItem[]> {
    const res = await this.fetchSkills({ skillName: query })
    return res.items
  },

  async getSkillDetail(id: number | bigint): Promise<SkillDetail> {
    const numId = Number(id)
    if (isTauriEnvironment()) {
      return await invokeNative<SkillDetail>('get_skill_detail', { id: numId })
    }
    const matched = mockSkills.find((s) => Number(s.id) === numId) || mockSkills[0]
    return {
      id: matched.id,
      name: matched.name,
      description: matched.description,
      creatorName: matched.creatorName,
      createdAt: matched.createdAt,
      status: matched.status,
      scope: matched.scope,
      categories: matched.categories,
      stages: matched.stages,
      viewCount: matched.viewCount,
      avgRating: matched.avgRating,
      ratingCount: matched.ratingCount,
      subscribed: matched.subscribed,
      installed: matched.installed,
      enabled: matched.enabled,
      installedProjects: matched.installedProjects,
      projectStates: matched.projectStates,
      version: matched.installedVersion || 1,
      hashtags: ['automation', 'aipro'],
      files: [{ id: BigInt(1) as unknown as bigint, fileName: 'SKILL.md', fileSize: BigInt(1024) as unknown as bigint, createdAt: matched.createdAt }],
      isCreator: false,
      canEdit: false,
      updatedAt: matched.createdAt,
    }
  },

  async getSkillVersions(id: number | bigint): Promise<SkillVersionItem[]> {
    const numId = Number(id)
    if (isTauriEnvironment()) {
      return await invokeNative<SkillVersionItem[]>('get_skill_versions', { id: numId })
    }
    return [
      {
        version: 1,
        name: 'skill-initial',
        description: 'Bản phát hành ổn định ban đầu',
        publicScope: 'PUBLIC',
        hashtags: ['v1', 'stable'],
        creatorName: 'AIPRO Studio',
        createdAt: '2026-10-01T08:00:00Z',
        files: [],
      },
    ]
  },

  // ==========================================
  // A.3 Install / Uninstall / Toggle / Clone
  // ==========================================
  async install(payload: { skill_id: number | bigint; name?: string; version?: number; scope?: string; project_path?: string }): Promise<{ ok: boolean; error?: string; warning?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('install', {
        payload: {
          skill_id: Number(payload.skill_id),
          name: payload.name,
          version: payload.version,
          scope: payload.scope,
          project_path: payload.project_path,
        },
      })
    }
    // Mock local install
    const sId = BigInt(payload.skill_id) as unknown as bigint
    const item: InstalledPlugin = {
      id: sId,
      name: payload.name || 'custom-skill',
      version: payload.version || 1,
      scope: payload.scope || 'global',
      installedAt: new Date().toISOString(),
      projectPath: payload.project_path,
      enabled: true,
    }
    mockInstalled.push(item)
    const m = mockSkills.find((s) => s.id === sId)
    if (m) {
      m.installed = true
      m.enabled = true
      m.installScope = payload.scope
      m.installedVersion = payload.version || 1
    }
    return { ok: true }
  },

  async installSkill(name: string, version: number, targetDir: string, scope: string): Promise<InstalledPlugin> {
    const matched = mockSkills.find((s) => s.name === name) || mockInstalled.find((s) => s.name === name)
    const id = matched
      ? matched.id
      : (name === 'AI Code Assistant'
          ? 101
          : name === 'Smart Database Query & Introspection'
          ? 102
          : name === 'Multi-Language Legal Document Analyzer'
          ? 103
          : 1)
    await this.install({
      skill_id: id,
      name,
      version,
      scope,
      project_path: scope === 'project' ? targetDir : undefined,
    })
    return {
      id: BigInt(id) as unknown as bigint,
      name,
      version,
      scope,
      installedAt: new Date().toISOString(),
      projectPath: scope === 'project' ? targetDir : undefined,
      enabled: true,
    }
  },

  async uninstall(payload: { skill_id: number | bigint; scope?: string; project_path?: string }): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('uninstall', {
        payload: {
          skill_id: Number(payload.skill_id),
          scope: payload.scope,
          project_path: payload.project_path,
        },
      })
    }
    const numId = Number(payload.skill_id)
    if (payload.scope === 'project' && payload.project_path) {
      mockInstalled = mockInstalled.filter((i) => !(Number(i.id) === numId && i.scope === 'project' && i.projectPath === payload.project_path))
    } else if (payload.scope === 'global') {
      mockInstalled = mockInstalled.filter((i) => !(Number(i.id) === numId && i.scope === 'global'))
    } else {
      mockInstalled = mockInstalled.filter((i) => Number(i.id) !== numId)
    }
    const hasRemaining = mockInstalled.some((i) => Number(i.id) === numId)
    if (!hasRemaining) {
      const m = mockSkills.find((s) => Number(s.id) === numId)
      if (m) {
        m.installed = false
        m.enabled = false
      }
    }
    return { ok: true }
  },

  async uninstallSkill(name: string, projectPath?: string): Promise<boolean> {
    const matched = mockSkills.find((s) => s.name === name) || mockInstalled.find((s) => s.name === name)
    const id = matched
      ? matched.id
      : (name === 'AI Code Assistant'
          ? 101
          : name === 'Smart Database Query & Introspection'
          ? 102
          : name === 'Multi-Language Legal Document Analyzer'
          ? 103
          : 0)
    const res = await this.uninstall({
      skill_id: id,
      scope: projectPath ? 'project' : 'global',
      project_path: projectPath,
    })
    return res.ok
  },

  async toggle(payload: { skill_id: number | bigint; enabled: boolean; scope?: string; project_path?: string }): Promise<{ ok: boolean }> {
    if (isTauriEnvironment()) {
      return await invokeNative('toggle', {
        payload: {
          skill_id: Number(payload.skill_id),
          enabled: payload.enabled,
          scope: payload.scope,
          project_path: payload.project_path,
        },
      })
    }
    const numId = Number(payload.skill_id)
    const item = mockInstalled.find((i) => Number(i.id) === numId)
    if (item) item.enabled = payload.enabled
    const m = mockSkills.find((s) => Number(s.id) === numId)
    if (m) m.enabled = payload.enabled
    return { ok: true }
  },

  async toggleSkill(name: string, enabled: boolean, projectPath?: string): Promise<boolean> {
    const matched = mockSkills.find((s) => s.name === name) || mockInstalled.find((s) => s.name === name)
    const id = matched
      ? matched.id
      : (name === 'AI Code Assistant'
          ? 101
          : name === 'Smart Database Query & Introspection'
          ? 102
          : name === 'Multi-Language Legal Document Analyzer'
          ? 103
          : 0)
    const res = await this.toggle({
      skill_id: id,
      enabled,
      scope: projectPath ? 'project' : 'global',
      project_path: projectPath,
    })
    return res.ok
  },

  async cloneSkill(sourceProject: string, targetProject: string, skillNames: string[]): Promise<InstalledPlugin[]> {
    if (isTauriEnvironment()) {
      const cloned: InstalledPlugin[] = []
      for (const name of skillNames) {
        const matched = mockSkills.find((s) => s.name === name)
        const skillId = matched ? Number(matched.id) : 1
        await invokeNative('clone_skill', {
          payload: {
            skill_id: skillId,
            source_project_path: sourceProject,
            target_project_path: targetProject,
          },
        })
        cloned.push({
          id: BigInt(skillId) as unknown as bigint,
          name,
          version: 1,
          enabled: true,
          installedAt: new Date().toISOString(),
          scope: 'project',
          projectPath: targetProject,
        })
      }
      return cloned
    }
    return []
  },

  // ==========================================
  // A.4 Settings / Projects / Integration
  // ==========================================
  async setTheme(theme: string | boolean): Promise<void> {
    const themeStr = typeof theme === 'boolean' ? (theme ? 'dark' : 'light') : theme
    if (isTauriEnvironment()) {
      try {
        await invokeNative('set_theme', { theme: themeStr })
        return
      } catch {
        // ignore
      }
    }
  },

  async saveRecentProject(path: string): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('save_recent_project', { path })
    }
    if (!mockRecentProjects.includes(path)) {
      mockRecentProjects.unshift(path)
    }
    return { ok: true }
  },

  async removeRecentProject(path: string): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('remove_recent_project', { path })
    }
    mockRecentProjects = mockRecentProjects.filter((p) => p !== path)
    return { ok: true }
  },

  async selectFolder(): Promise<{ ok: boolean; path?: string; cancelled?: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('select_folder')
    }
    return { ok: true, path: 'D:/AI_Projects/DemoWorkspace' }
  },

  async openStudio(): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('open_studio')
    }
    return { ok: true }
  },

  async openAiproStudio(): Promise<string> {
    const res = await this.openStudio()
    if (res.ok) {
      return 'Đã khởi động AIPRO Studio thành công.'
    }
    throw new Error(res.error || 'Không tìm thấy AIPRO_Studio.exe')
  },

  async checkForUpdate(): Promise<CheckUpdateResponse> {
    if (isTauriEnvironment()) {
      return await invokeNative<CheckUpdateResponse>('check_for_update')
    }
    return { status: 'success', updateAvailable: false, currentVersion: '1.0.0' }
  },

  async downloadAndInstallUpdate(downloadUrl?: string): Promise<{ ok: boolean; error?: string }> {
    if (isTauriEnvironment()) {
      return await invokeNative('download_and_install_update', {
        payload: { download_url: downloadUrl },
      })
    }
    return { ok: true }
  },

  async onUpdateProgress(
    callback: (payload: UpdateProgressPayload) => void
  ): Promise<() => void> {
    return await listenToEvent<UpdateProgressPayload>('update-progress', callback)
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
        // ignore
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
  // MCP Protocol Studio Catalog
  // ==========================================
  async getCatalog(registryUrl: string, query?: string, category?: string): Promise<CatalogResponse> {
    if (isTauriEnvironment()) {
      try {
        return await invokeNative<CatalogResponse>('get_catalog', { query, category })
      } catch (e) {
        console.warn('[NativeBridge] get_catalog failed, falling back:', e)
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
