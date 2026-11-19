<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useSkillStore } from './stores/skillStore'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { useSettingsStore } from '@/features/settings/stores/settingsStore'
import { useI18n, type LocaleLang } from '@/i18n'
import { useToast } from 'primevue/usetoast'
import AxIcon from '@/components/ui/AxIcon.vue'

import SkillList from './components/SkillList.vue'
import SkillDetailPanel from './components/SkillDetailPanel.vue'
import ProjectListPanel from './components/ProjectListPanel.vue'
import ScopeModal from './components/ScopeModal.vue'
import FolderPickerModal from './components/FolderPickerModal.vue'
import CloneSkillModal from './components/CloneSkillModal.vue'
import UpdateDialog from './components/UpdateDialog.vue'
import SettingsDialog from '@/features/settings/components/SettingsDialog.vue'

// Import modular MCP studio view for mode switching
import McpStudioView from '@/features/plugins/components/McpStudioView.vue'

const store = useSkillStore()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const { t, locale, setLocale } = useI18n()
const toast = useToast()

const userMenuContainerRef = ref<HTMLElement>()
const isUserMenuOpen = ref(false)
const isLaunchingStudio = ref(false)
const showSettings = ref(false)

const skillLocationInfo = computed(() => {
  // If in projects tab, show active current project workspace
  if (store.activeTab === 'projects') {
    if (!store.currentProject) return null
    return {
      isGlobal: false,
      iconName: 'folder-open',
      iconColor: 'text-emerald-500',
      label: store.currentProject,
      title: store.currentProject,
    }
  }

  // If in marketplace or installed tab, check selectedSkill
  const skill = store.selectedSkill
  if (!skill) return null

  if (!skill.installed) {
    return {
      isGlobal: false,
      iconName: 'cloud',
      iconColor: 'text-slate-400',
      label: t('portal.notInstalled'),
      title: t('portal.notInstalled'),
    }
  }

  const isGlobal = skill.installScope === 'global' || skill.scope === 'GLOBAL'
  if (isGlobal) {
    return {
      isGlobal: true,
      iconName: 'globe',
      iconColor: 'text-blue-500 dark:text-blue-400',
      label: '~/.aipro/skills (Global)',
      title: 'Toàn cục: ~/.aipro/skills',
    }
  }

  // Project scope
  const projPath = skill.installedProjects?.[0] || store.currentProject || ''
  if (!projPath) {
    return {
      isGlobal: false,
      iconName: 'folder-open',
      iconColor: 'text-emerald-500',
      label: t('portal.project'),
      title: t('portal.project'),
    }
  }

  return {
    isGlobal: false,
    iconName: 'folder-open',
    iconColor: 'text-emerald-500',
    label: projPath,
    title: projPath,
  }
})

onClickOutside(userMenuContainerRef, () => {
  isUserMenuOpen.value = false
})

async function handleAutostartToggle() {
  isUserMenuOpen.value = false
  await store.setAutostart(!store.autostartEnabled)
  toast.add({
    severity: 'info',
    summary: t('portal.appName'),
    detail: store.autostartEnabled ? t('portal.autostartEnabledMsg') : t('portal.autostartDisabledMsg'),
    life: 2500,
  })
}

async function handleCheckUpdates() {
  isUserMenuOpen.value = false
  const rel = await store.checkForUpdates()
  if (!rel || !rel.updateAvailable) {
    toast.add({
      severity: 'info',
      summary: t('portal.checkUpdatesMenu'),
      detail: t('portal.latestVersionMsg', { version: rel?.currentVersion ? `v${rel.currentVersion}` : `v${store.appVersion}` }),
      life: 2500,
    })
  }
}

function switchLang(lang: LocaleLang) {
  setLocale(lang)
}

async function handleLaunchStudio() {
  isLaunchingStudio.value = true
  try {
    const msg = await store.openAiproStudio()
    toast.add({
      severity: 'success',
      summary: 'AIPRO Studio',
      detail: msg,
      life: 3000,
    })
  } catch (err: any) {
    toast.add({
      severity: 'warn',
      summary: 'Khởi chạy AIPRO Studio',
      detail: err?.message || String(err),
      life: 4000,
    })
  } finally {
    isLaunchingStudio.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    store.loadPortalStatus(),
    store.fetchMarketplaceSkills(),
  ])
  // Non-blocking update check on launch
  store.checkForUpdates().catch(() => {})

  if (typeof window !== 'undefined') {
    const params = new URLSearchParams(window.location.search)
    if (params.get('tab') === 'installed') {
      store.setActiveTab('installed')
    }
    if (params.get('mode') === 'mcp') {
      store.setMode('mcp')
    }
    if (params.get('settings') === '1') {
      showSettings.value = true
    }
    if (params.get('scope') === '1') {
      store.pendingInstallSkill = store.skills[0] || null
      store.showScopeModal = true
    }
    if (params.get('dropdown') === '1') {
      isUserMenuOpen.value = true
    }
  }
})
</script>

<template>
  <div class="h-screen w-screen flex flex-col bg-white dark:bg-[#121214] text-slate-900 dark:text-[#ececec] overflow-hidden select-none font-sans">
    <!-- Master Header -->
    <header class="h-13 border-b border-slate-200/90 dark:border-[#393B40] bg-white/95 dark:bg-[#1E1F22]/95 backdrop-blur-md px-4 flex items-center justify-between gap-3 flex-shrink-0 z-20">
      <!-- Left: Navigation Tabs (Replaces redundant logo/title directly per user request) -->
      <div v-if="store.currentMode === 'skills'" class="flex items-center gap-1 sm:gap-1.5">
        <button
          type="button"
          data-testid="tab-marketplace"
          class="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer"
          :class="store.activeTab === 'marketplace'
            ? 'bg-[#3574F0]/10 text-[#3574F0] dark:text-[#56A8F5] border border-[#3574F0]/30 shadow-xs'
            : 'text-slate-600 dark:text-[#868A91] hover:text-slate-900 dark:hover:text-[#DFE1E5] hover:bg-slate-100 dark:hover:bg-[#2B2D30] border border-transparent'"
          @click="store.setActiveTab('marketplace')"
        >
          <AxIcon name="compass" size="sm" />
          <span>{{ t('portal.tabMarketplace') }}</span>
          <span
            class="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded-full"
            :class="store.activeTab === 'marketplace' ? 'bg-[#3574F0] text-white' : 'bg-slate-200 dark:bg-[#393B40] text-slate-700 dark:text-[#CED0D6]'"
          >
            {{ store.skills.length }}
          </span>
        </button>

        <button
          type="button"
          data-testid="tab-installed"
          class="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer"
          :class="store.activeTab === 'installed'
            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 shadow-xs'
            : 'text-slate-600 dark:text-[#868A91] hover:text-slate-900 dark:hover:text-[#DFE1E5] hover:bg-slate-100 dark:hover:bg-[#2B2D30] border border-transparent'"
          @click="store.setActiveTab('installed')"
        >
          <AxIcon name="check-circle" size="sm" />
          <span>{{ t('portal.tabInstalled') }}</span>
          <span
            class="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded-full"
            :class="store.activeTab === 'installed' ? 'bg-emerald-500 text-white' : 'bg-slate-200 dark:bg-[#393B40] text-slate-700 dark:text-[#CED0D6]'"
          >
            {{ store.installedSkills.length }}
          </span>
        </button>

        <button
          type="button"
          data-testid="tab-projects"
          class="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer"
          :class="store.activeTab === 'projects'
            ? 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/30 shadow-xs'
            : 'text-slate-600 dark:text-[#868A91] hover:text-slate-900 dark:hover:text-[#DFE1E5] hover:bg-slate-100 dark:hover:bg-[#2B2D30] border border-transparent'"
          @click="store.setActiveTab('projects')"
        >
          <AxIcon name="folder" size="sm" />
          <span>{{ t('portal.tabProjects') }}</span>
          <span
            class="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded-full"
            :class="store.activeTab === 'projects' ? 'bg-sky-500 text-white' : 'bg-slate-200 dark:bg-[#393B40] text-slate-700 dark:text-[#CED0D6]'"
          >
            {{ store.recentProjects.length }}
          </span>
        </button>
      </div>

      <!-- Left when in MCP mode -->
      <div v-else class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-500 flex items-center justify-center text-white shadow-sm shadow-teal-500/25">
          <AxIcon name="cpu" size="sm" />
        </div>
        <span class="font-bold text-xs text-slate-900 dark:text-[#DFE1E5] tracking-tight">MCP Protocol Studio</span>
      </div>

      <!-- Center: Mode Switcher (Skill Marketplace <-> MCP Protocol Studio) -->
      <div class="flex items-center bg-slate-100 dark:bg-[#2B2D30] p-1 rounded-xl border border-slate-200 dark:border-[#393B40]">
        <button
          type="button"
          class="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="store.currentMode === 'skills' ? 'bg-white dark:bg-[#35373B] text-slate-900 dark:text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 dark:hover:text-[#DFE1E5]'"
          @click="store.setMode('skills')"
        >
          <AxIcon name="puzzle" size="xs" class="text-emerald-500" />
          <span>{{ t('portal.modeSkills') }}</span>
        </button>

        <button
          type="button"
          class="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="store.currentMode === 'mcp' ? 'bg-white dark:bg-[#35373B] text-slate-900 dark:text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 dark:hover:text-[#DFE1E5]'"
          @click="store.setMode('mcp')"
        >
          <AxIcon name="cpu" size="xs" class="text-teal-400" />
          <span>{{ t('portal.modeMcp') }}</span>
        </button>
      </div>

      <!-- Right: Location info, Launch Studio, Language, Theme & User Profile -->
      <div class="flex items-center gap-2 flex-shrink-0">
        <!-- Active Workspace / Scope path pill -->
        <div
          v-if="skillLocationInfo"
          class="hidden lg:flex items-center gap-1.5 py-1 px-2.5 rounded-lg bg-slate-100 dark:bg-[#2B2D30] border border-slate-200 dark:border-[#393B40] text-[11px] text-slate-600 dark:text-[#CED0D6]"
          :title="skillLocationInfo.title"
        >
          <AxIcon :name="skillLocationInfo.iconName" size="xs" :class="skillLocationInfo.iconColor" />
          <span class="font-mono truncate max-w-[160px]">{{ skillLocationInfo.label }}</span>
        </div>

        <!-- Launch AIPRO Studio Button -->
        <button
          type="button"
          :disabled="isLaunchingStudio"
          class="py-1.5 px-3 text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white rounded-xl shadow-xs shadow-emerald-500/25 transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-60 flex-shrink-0 active:scale-95"
          @click="handleLaunchStudio"
        >
          <AxIcon v-if="isLaunchingStudio" name="spinner" size="xs" class="animate-spin" />
          <AxIcon v-else name="external-link" size="xs" />
          <span>{{ t('portal.launchStudioBtn') }}</span>
        </button>

        <!-- Multi-language Switcher (VI | EN | KO) -->
        <div class="flex items-center gap-0.5 bg-slate-100 dark:bg-[#2B2D30] border border-slate-200 dark:border-[#393B40] rounded-xl p-0.5 shadow-xs">
          <button
            type="button"
            class="px-2 py-0.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
            :class="locale === 'vi' ? 'bg-emerald-500 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
            @click="switchLang('vi')"
          >
            VI
          </button>
          <button
            type="button"
            class="px-2 py-0.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
            :class="locale === 'en' ? 'bg-emerald-500 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
            @click="switchLang('en')"
          >
            EN
          </button>
          <button
            type="button"
            class="px-2 py-0.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
            :class="locale === 'ko' ? 'bg-emerald-500 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
            @click="switchLang('ko')"
          >
            KO
          </button>
        </div>

        <!-- Dark/Light Theme Toggle -->
        <button
          type="button"
          class="p-1.5 rounded-xl text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-[#2B2D30] transition-colors cursor-pointer"
          :title="settingsStore.darkMode ? t('portal.themeLightTitle') : t('portal.themeDarkTitle')"
          @click="settingsStore.toggleDarkMode"
        >
          <AxIcon :name="settingsStore.darkMode ? 'sun' : 'moon'" size="sm" :class="settingsStore.darkMode ? 'text-amber-400' : 'text-slate-600'" />
        </button>

        <!-- User Profile Avatar & Solid Dropdown Menu -->
        <div class="relative" ref="userMenuContainerRef">
          <button
            type="button"
            data-testid="header-user-btn"
            class="flex items-center gap-1.5 p-1 rounded-xl hover:bg-slate-100 dark:hover:bg-[#2B2D30] transition-colors cursor-pointer"
            @click="isUserMenuOpen = !isUserMenuOpen"
          >
            <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-xs shadow-xs">
              {{ (authStore.currentUser?.name || 'AX').substring(0, 2).toUpperCase() }}
            </div>
            <span class="text-xs font-semibold text-slate-700 dark:text-[#CED0D6] hidden md:inline max-w-[110px] truncate">
              {{ authStore.currentUser?.name || t('portal.guestName') }}
            </span>
            <AxIcon name="chevron-down" size="xs" class="text-slate-400 transition-transform duration-200" :class="{ 'rotate-180': isUserMenuOpen }" />
          </button>

          <!-- Sleek Floating Dropdown Menu -->
          <div
            v-if="isUserMenuOpen"
            data-testid="user-dropdown-menu"
            class="absolute right-0 top-full mt-1.5 w-64 rounded-2xl border border-slate-200/90 dark:border-[#393B40] bg-white dark:bg-[#2B2D30] shadow-xl shadow-slate-900/10 dark:shadow-black/60 p-1.5 z-[9999] flex flex-col gap-0.5 select-none"
          >
            <!-- User Info Header -->
            <div class="px-3 py-2 border-b border-slate-100 dark:border-[#393B40] mb-1 flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-xs shadow-xs flex-shrink-0">
                {{ (authStore.currentUser?.name || 'AX').substring(0, 2).toUpperCase() }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-xs font-bold text-slate-900 dark:text-[#DFE1E5] truncate flex items-center gap-1.5">
                  <span>{{ authStore.currentUser?.name || t('portal.guestName') }}</span>
                  <span class="text-[9px] font-mono px-1.5 py-0.2 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-bold">PRO</span>
                </div>
                <div class="text-[11px] text-slate-500 dark:text-[#868A91] font-mono truncate">
                  {{ authStore.currentUser?.email || 'offline@aipro.local' }}
                </div>
              </div>
            </div>

            <button
              type="button"
              class="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-xs font-medium text-slate-700 dark:text-[#CED0D6] hover:bg-slate-100 dark:hover:bg-[#35373B] hover:text-slate-900 dark:hover:text-[#DFE1E5] transition-colors cursor-pointer text-left"
              @click="showSettings = true; isUserMenuOpen = false"
            >
              <div class="flex items-center gap-2">
                <AxIcon name="settings" size="xs" class="text-emerald-500" />
                <span>{{ t('portal.settingsMenu') }}</span>
              </div>
              <kbd class="text-[10px] font-mono text-slate-400 bg-slate-100 dark:bg-[#1E1F22] px-1.5 py-0.5 rounded border border-slate-200 dark:border-[#393B40]">Ctrl+,</kbd>
            </button>

            <button
              type="button"
              class="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-xs font-medium text-slate-700 dark:text-[#CED0D6] hover:bg-slate-100 dark:hover:bg-[#35373B] hover:text-slate-900 dark:hover:text-[#DFE1E5] transition-colors cursor-pointer text-left"
              @click="handleAutostartToggle"
            >
              <div class="flex items-center gap-2">
                <AxIcon name="monitor" size="xs" class="text-teal-500" />
                <span>{{ t('portal.autostartMenu') }}</span>
              </div>
              <span class="text-[10px] font-bold px-1.5 py-0.5 rounded" :class="store.autostartEnabled ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/10' : 'text-slate-500 bg-slate-100 dark:bg-[#1E1F22]'">
                {{ store.autostartEnabled ? t('common.on') : t('common.off') }}
              </span>
            </button>

            <button
              type="button"
              class="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-xs font-medium text-slate-700 dark:text-[#CED0D6] hover:bg-slate-100 dark:hover:bg-[#35373B] hover:text-slate-900 dark:hover:text-[#DFE1E5] transition-colors cursor-pointer text-left"
              @click="handleCheckUpdates"
            >
              <div class="flex items-center gap-2">
                <AxIcon name="sync" size="xs" class="text-cyan-500" />
                <span>{{ t('portal.checkUpdatesMenu') }}</span>
              </div>
              <span class="text-[10px] font-mono text-slate-400">v{{ store.appVersion }}</span>
            </button>

            <div class="h-px bg-slate-100 dark:bg-[#393B40] my-1"></div>

            <button
              type="button"
              class="w-full flex items-center gap-2 px-2.5 py-2 rounded-xl text-xs font-semibold text-rose-500 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 hover:text-rose-600 dark:hover:text-rose-300 transition-colors cursor-pointer text-left"
              @click="authStore.logout(); isUserMenuOpen = false"
            >
              <AxIcon name="logout" size="xs" class="text-rose-500 dark:text-rose-400" />
              <span>{{ t('portal.logoutMenu') }}</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Workspace View -->
    <div class="flex-1 flex flex-col min-h-0 overflow-hidden relative">
      <!-- Mode 1: MCP Protocol Studio Mode -->
      <div v-if="store.currentMode === 'mcp'" class="h-full w-full flex flex-col min-h-0 overflow-hidden">
        <McpStudioView :embedded="true" />
      </div>

      <!-- Mode 2: Skill Marketplace Mode -->
      <div v-else class="h-full flex min-h-0 overflow-hidden">
        <!-- Marketplace & Installed: 2-column layout (List + Detail) -->
        <template v-if="store.activeTab === 'marketplace' || store.activeTab === 'installed'">
          <div class="w-80 md:w-96 lg:w-[420px] flex-shrink-0 h-full overflow-hidden border-r border-slate-200/80 dark:border-[#393B40]">
            <SkillList />
          </div>
          <div class="flex-1 h-full overflow-hidden">
            <SkillDetailPanel />
          </div>
        </template>

        <!-- Projects: Full width Workspace Management -->
        <template v-else-if="store.activeTab === 'projects'">
          <div class="flex-1 h-full overflow-hidden">
            <ProjectListPanel />
          </div>
        </template>
      </div>
    </div>

    <!-- Modals -->
    <ScopeModal />
    <FolderPickerModal />
    <CloneSkillModal />
    <UpdateDialog />
    <SettingsDialog v-model:visible="showSettings" />
  </div>
</template>
