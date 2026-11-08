import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { nativeBridge } from '@/services/nativeBridge'
import type { SkillItem } from '@/types/generated/SkillItem'
import type { SkillDetail } from '@/types/generated/SkillDetail'
import type { SkillVersionItem } from '@/types/generated/SkillVersionItem'
import type { InstalledPlugin } from '@/types/generated/InstalledPlugin'

export type StudioMode = 'skills' | 'mcp'
export type SkillTab = 'marketplace' | 'installed' | 'projects'
export type InstalledFilter = 'all' | 'global' | 'project'

export const useSkillStore = defineStore('skills', () => {
  // App Mode (Skill Marketplace vs MCP Protocol Studio)
  const currentMode = ref<StudioMode>('skills')

  // Navigation & Filtering
  const activeTab = ref<SkillTab>('marketplace')
  const installedFilter = ref<InstalledFilter>('all')
  const searchQuery = ref('')
  const selectedCategory = ref<string>('All')

  // Data states
  const skills = ref<SkillItem[]>([])
  const selectedSkillName = ref<string | null>(null)
  const selectedInstalledKey = ref<string | null>(null)
  const skillDetail = ref<SkillDetail | null>(null)
  const skillVersions = ref<SkillVersionItem[]>([])
  const installedSkills = ref<InstalledPlugin[]>([])
  const recentProjects = ref<string[]>([])
  const currentProject = ref<string | null>(null)

  // System states
  const isLoading = ref(false)
  const isCheckingUpdate = ref(false)
  const availableUpdate = ref<any>(null)
  const appVersion = ref('1.0.2')
  const autostartEnabled = ref(false)
  const isUpdating = ref(false)
  const updateProgress = ref(0)
  const updateBytesDownloaded = ref(0)
  const updateBytesTotal = ref(0)
  const updateStatusText = ref('')
  const updateError = ref<string | null>(null)

  // Dialog Visibility
  const showScopeModal = ref(false)
  const pendingInstallSkill = ref<SkillItem | null>(null)
  const showFolderPickerModal = ref(false)
  const showCloneSkillModal = ref(false)
  const showUpdateDialog = ref(false)

  // Computed Properties
  const selectedSkill = computed<SkillItem | null>(() => {
    // If installed tab is active, look in installedSkills first
    if (activeTab.value === 'installed') {
      let inst: InstalledPlugin | undefined
      if (selectedInstalledKey.value) {
        inst = installedSkills.value.find(
          (s) => `${s.name}-${s.scope}-${s.projectPath || 'global'}` === selectedInstalledKey.value
        )
      }
      if (!inst && selectedSkillName.value) {
        inst = installedSkills.value.find((s) => s.name === selectedSkillName.value)
      }
      if (!inst && installedSkills.value.length > 0) {
        inst = installedSkills.value[0]
      }
      if (inst) {
        return {
          id: inst.id,
          name: inst.name,
          description: skillDetail.value?.description || `Skill cài đặt: ${inst.name}`,
          creatorName: 'AIPRO Community',
          createdAt: inst.installedAt,
          status: 'APPROVED',
          scope: inst.scope.toUpperCase(),
          categories: ['General'],
          stages: ['Production'],
          viewCount: BigInt(100) as unknown as bigint,
          avgRating: 5.0,
          ratingCount: BigInt(1) as unknown as bigint,
          subscribed: false,
          installed: true,
          enabled: inst.enabled,
          installScope: inst.scope,
          installedProjects: inst.projectPath ? [inst.projectPath] : [],
          projectStates: {},
          installedVersion: inst.version,
        }
      }
    }

    if (!selectedSkillName.value) {
      if (skills.value.length > 0) return skills.value[0]
      return null
    }

    const found = skills.value.find((s) => s.name === selectedSkillName.value)
    if (found) return found

    // Fallback: look up in installedSkills
    const inst = installedSkills.value.find((s) => s.name === selectedSkillName.value)
    if (inst) {
      return {
        id: inst.id,
        name: inst.name,
        description: skillDetail.value?.description || `Skill cài đặt: ${inst.name}`,
        creatorName: 'AIPRO Community',
        createdAt: inst.installedAt,
        status: 'APPROVED',
        scope: inst.scope.toUpperCase(),
        categories: ['General'],
        stages: ['Production'],
        viewCount: BigInt(100) as unknown as bigint,
        avgRating: 5.0,
        ratingCount: BigInt(1) as unknown as bigint,
        subscribed: false,
        installed: true,
        enabled: inst.enabled,
        installScope: inst.scope,
        installedProjects: inst.projectPath ? [inst.projectPath] : [],
        projectStates: {},
        installedVersion: inst.version,
      }
    }

    return skills.value[0] || null
  })

  const filteredMarketplaceSkills = computed<SkillItem[]>(() => {
    let list = skills.value
    if (selectedCategory.value && selectedCategory.value !== 'All') {
      list = list.filter((s) => s.categories.includes(selectedCategory.value))
    }
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase().trim()
      list = list.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.creatorName.toLowerCase().includes(q)
      )
    }
    return list
  })

  const filteredInstalledSkills = computed<InstalledPlugin[]>(() => {
    let list = installedSkills.value
    if (installedFilter.value === 'global') {
      list = list.filter((s) => s.scope === 'global')
    } else if (installedFilter.value === 'project') {
      list = list.filter((s) => s.scope === 'project')
    }
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase().trim()
      list = list.filter((s) => s.name.toLowerCase().includes(q))
    }
    return list
  })

  // Mode and Tab switchers
  function setMode(mode: StudioMode) {
    currentMode.value = mode
  }

  function setActiveTab(tab: SkillTab) {
    activeTab.value = tab
    if (tab === 'installed' && installedSkills.value.length > 0) {
      selectInstalledSkill(installedSkills.value[0])
    } else if (tab === 'marketplace' && skills.value.length > 0) {
      selectSkill(skills.value[0])
    }
  }

  function setInstalledFilter(filter: InstalledFilter) {
    installedFilter.value = filter
  }

  // Actions
  async function loadAppVersion() {
    try {
      const info = await nativeBridge.getAppInfo()
      if (info?.version) {
        appVersion.value = info.version
      }
    } catch {
      // fallback
    }
  }

  async function loadPortalStatus() {
    try {
      const [status, isAuto] = await Promise.all([
        nativeBridge.getStatus(),
        nativeBridge.isAutostartEnabled().catch(() => false),
        loadAppVersion()
      ])
      const rawInstalled = status.installed || []
      const seen = new Set<string>()
      const deduped: InstalledPlugin[] = []
      for (const item of rawInstalled) {
        const key = `${item.name}-${item.scope}-${item.projectPath || 'global'}`
        if (!seen.has(key)) {
          seen.add(key)
          deduped.push(item)
        }
      }
      installedSkills.value = deduped
      recentProjects.value = status.recentProjects || []
      if (!currentProject.value && recentProjects.value.length > 0) {
        currentProject.value = recentProjects.value[0]
      }
      autostartEnabled.value = isAuto
    } catch (e) {
      console.warn('Failed to load portal status:', e)
    }
  }

  async function fetchMarketplaceSkills(query?: string) {
    isLoading.value = true
    try {
      const res = await nativeBridge.fetchSkills({ skillName: query })
      skills.value = res.items
      if (res.items.length > 0 && !selectedSkillName.value) {
        selectedSkillName.value = res.items[0].name
        await fetchSkillDetail(res.items[0].id)
      }
    } catch (e) {
      console.error('Failed to fetch marketplace skills:', e)
    } finally {
      isLoading.value = false
    }
  }

  let lastRequestedSkillId: number | bigint | null = null

  async function fetchSkillDetail(id: number | bigint) {
    lastRequestedSkillId = id
    try {
      const [detail, versions] = await Promise.all([
        nativeBridge.getSkillDetail(id),
        nativeBridge.getSkillVersions(id),
      ])
      // Discard response if another skill was selected in the meantime
      if (lastRequestedSkillId !== id) return

      skillDetail.value = detail
      skillVersions.value = versions
    } catch (e) {
      if (lastRequestedSkillId === id) {
        console.error(`Failed to fetch skill detail for ${id}:`, e)
      }
    }
  }

  function selectSkill(skill: SkillItem) {
    selectedSkillName.value = skill.name
    fetchSkillDetail(skill.id)
  }

  function selectInstalledSkill(inst: InstalledPlugin) {
    selectedSkillName.value = inst.name
    selectedInstalledKey.value = `${inst.name}-${inst.scope}-${inst.projectPath || 'global'}`
    fetchSkillDetail(inst.id)
  }

  async function installSkill(
    name: string,
    version: number,
    scope: 'global' | 'project',
    targetDir?: string
  ): Promise<InstalledPlugin> {
    isLoading.value = true
    try {
      if (scope === 'project') {
        const finalTarget = (targetDir || currentProject.value || '').trim()
        if (!finalTarget || finalTarget === '.') {
          throw new Error('Vui lòng chọn hoặc nhập đường dẫn dự án đích khi cài đặt theo dự án.')
        }
      }
      const target = scope === 'project' ? (targetDir || currentProject.value || '').trim() : '.'
      const installed = await nativeBridge.installSkill(name, version, target, scope)

      // Update state
      const existingIdx = installedSkills.value.findIndex(
        (s) => s.name === name && s.scope === scope && (s.projectPath || '') === (installed.projectPath || '')
      )
      if (existingIdx >= 0) {
        installedSkills.value[existingIdx] = installed
      } else {
        installedSkills.value.push(installed)
      }

      // Mark in marketplace skills
      const mSkill = skills.value.find((s) => s.name === name)
      if (mSkill) {
        mSkill.installed = true
        mSkill.enabled = true
        mSkill.installScope = scope
        mSkill.installedVersion = version
      }

      if (skillDetail.value && skillDetail.value.name === name) {
        skillDetail.value.installed = true
        skillDetail.value.enabled = true
        skillDetail.value.installScope = scope
        skillDetail.value.installedVersion = version
      }

      return installed
    } finally {
      isLoading.value = false
    }
  }

  async function uninstallSkill(name: string, projectPath?: string): Promise<boolean> {
    isLoading.value = true
    try {
      const ok = await nativeBridge.uninstallSkill(name, projectPath)
      if (ok) {
        const normProj = projectPath ? projectPath.replace(/\\/g, '/').toLowerCase() : null
        installedSkills.value = installedSkills.value.filter((s) => {
          if (s.name !== name) return true
          if (normProj) {
            return !s.projectPath || s.projectPath.replace(/\\/g, '/').toLowerCase() !== normProj
          }
          return s.scope !== 'global' && Boolean(s.projectPath)
        })
        const hasRemaining = installedSkills.value.some((s) => s.name === name)
        if (!hasRemaining) {
          const mSkill = skills.value.find((s) => s.name === name)
          if (mSkill) {
            mSkill.installed = false
            mSkill.enabled = false
            mSkill.installedVersion = undefined
          }
          if (skillDetail.value && skillDetail.value.name === name) {
            skillDetail.value.installed = false
            skillDetail.value.enabled = false
            skillDetail.value.installedVersion = undefined
          }
        }
        await loadPortalStatus()
      }
      return ok
    } finally {
      isLoading.value = false
    }
  }

  async function toggleSkill(name: string, enabled: boolean, projectPath?: string): Promise<boolean> {
    try {
      const ok = await nativeBridge.toggleSkill(name, enabled, projectPath)
      if (ok) {
        const normProj = projectPath ? projectPath.replace(/\\/g, '/').toLowerCase() : null
        const item = installedSkills.value.find((s) => {
          if (s.name !== name) return false
          if (normProj) {
            return s.projectPath && s.projectPath.replace(/\\/g, '/').toLowerCase() === normProj
          }
          return s.scope === 'global' || !s.projectPath
        })
        if (item) {
          item.enabled = enabled
        }
        const mSkill = skills.value.find((s) => s.name === name)
        if (mSkill) {
          mSkill.enabled = enabled
        }
        if (skillDetail.value && skillDetail.value.name === name) {
          skillDetail.value.enabled = enabled
        }
        await loadPortalStatus()
      }
      return ok
    } catch (e) {
      console.error(`Failed to toggle skill ${name}:`, e)
      return false
    }
  }

  async function cloneSkills(
    sourceProject: string,
    targetProject: string,
    skillNames: string[]
  ): Promise<InstalledPlugin[]> {
    isLoading.value = true
    try {
      const cloned = await nativeBridge.cloneSkill(sourceProject, targetProject, skillNames)
      await nativeBridge.saveRecentProject(targetProject)
      if (!recentProjects.value.includes(targetProject)) {
        recentProjects.value.unshift(targetProject)
      }
      await loadPortalStatus()
      return cloned
    } finally {
      isLoading.value = false
    }
  }

  function setCurrentProject(projectPath: string) {
    currentProject.value = projectPath
    if (!recentProjects.value.includes(projectPath)) {
      recentProjects.value.unshift(projectPath)
    }
    nativeBridge.saveRecentProject(projectPath).catch(() => {})
  }

  function addProject(projectPath: string) {
    if (!recentProjects.value.includes(projectPath)) {
      recentProjects.value.unshift(projectPath)
    }
    currentProject.value = projectPath
    nativeBridge.saveRecentProject(projectPath).catch(() => {})
  }

  async function removeProject(projectPath: string) {
    await nativeBridge.removeRecentProject(projectPath)
    recentProjects.value = recentProjects.value.filter((p) => p !== projectPath)
    if (currentProject.value === projectPath) {
      currentProject.value = recentProjects.value[0] || null
    }
  }

  async function pickProjectFolder(): Promise<string | null> {
    const res = await nativeBridge.selectFolder()
    if (res.ok && res.path) {
      await addProject(res.path)
      return res.path
    }
    return null
  }

  async function checkForUpdates() {
    isCheckingUpdate.value = true
    try {
      const rel = await nativeBridge.checkForUpdate()
      if (rel?.currentVersion) {
        appVersion.value = rel.currentVersion
      }
      if (rel.status === 'success' && rel.updateAvailable) {
        availableUpdate.value = rel
        showUpdateDialog.value = true
      } else {
        availableUpdate.value = null
      }
      return rel
    } catch (e) {
      console.warn('Update check failed:', e)
      return null
    } finally {
      isCheckingUpdate.value = false
    }
  }

  async function openAiproStudio(): Promise<string> {
    return await nativeBridge.openAiproStudio()
  }

  async function setAutostart(enable: boolean) {
    await nativeBridge.setAutostart(enable)
    autostartEnabled.value = enable
  }

  async function applyAutoUpdate() {
    if (isUpdating.value) return
    isUpdating.value = true
    updateProgress.value = 0
    updateBytesDownloaded.value = 0
    updateBytesTotal.value = 0
    updateError.value = null
    updateStatusText.value = 'Đang kết nối tới máy chủ cập nhật...'

    let unlisten: (() => void) | null = null
    try {
      unlisten = await nativeBridge.onUpdateProgress((payload) => {
        if (payload.status === 'downloading') {
          updateProgress.value = payload.percent
          updateBytesDownloaded.value = payload.downloaded
          updateBytesTotal.value = payload.total
          updateStatusText.value = `Đang tải xuống (${payload.percent}%)...`
        } else if (payload.status === 'installing') {
          updateProgress.value = 100
          updateStatusText.value = 'Đang tự động áp dụng bản cập nhật và khởi động lại...'
        } else if (payload.status === 'error') {
          updateError.value = payload.error || 'Cập nhật thất bại'
          isUpdating.value = false
        }
      })

      const downloadUrl = availableUpdate.value?.downloadUrl
      const res = await nativeBridge.downloadAndInstallUpdate(downloadUrl)
      if (!res.ok && res.error) {
        updateError.value = res.error
        isUpdating.value = false
      }
    } catch (e: any) {
      updateError.value = e?.message || String(e)
      isUpdating.value = false
    } finally {
      if (updateError.value && unlisten) {
        unlisten()
      }
    }
  }

  return {
    currentMode,
    activeTab,
    installedFilter,
    searchQuery,
    selectedCategory,
    skills,
    selectedSkillName,
    selectedInstalledKey,
    selectedSkill,
    skillDetail,
    skillVersions,
    installedSkills,
    recentProjects,
    currentProject,
    isLoading,
    isCheckingUpdate,
    availableUpdate,
    appVersion,
    loadAppVersion,
    autostartEnabled,
    isUpdating,
    updateProgress,
    updateBytesDownloaded,
    updateBytesTotal,
    updateStatusText,
    updateError,
    showScopeModal,
    pendingInstallSkill,
    showFolderPickerModal,
    showCloneSkillModal,
    showUpdateDialog,
    filteredMarketplaceSkills,
    filteredInstalledSkills,
    setMode,
    setActiveTab,
    setInstalledFilter,
    loadPortalStatus,
    fetchMarketplaceSkills,
    fetchSkillDetail,
    selectSkill,
    selectInstalledSkill,
    installSkill,
    uninstallSkill,
    toggleSkill,
    cloneSkills,
    setCurrentProject,
    addProject,
    removeProject,
    pickProjectFolder,
    checkForUpdates,
    applyAutoUpdate,
    openAiproStudio,
    setAutostart,
  }
})
