<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useSkillStore } from './stores/skillStore'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { useSettingsStore } from '@/features/settings/stores/settingsStore'
import { useI18n, type LocaleLang } from '@/i18n'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'

import SkillList from './components/SkillList.vue'
import SkillDetailPanel from './components/SkillDetailPanel.vue'
import ProjectListPanel from './components/ProjectListPanel.vue'
import ScopeModal from './components/ScopeModal.vue'
import FolderPickerModal from './components/FolderPickerModal.vue'
import CloneSkillModal from './components/CloneSkillModal.vue'
import UpdateDialog from './components/UpdateDialog.vue'
import SettingsDialog from '@/features/settings/components/SettingsDialog.vue'

// Import existing MCP standalone view for mode switching
import PluginStandaloneView from '@/features/plugins/views/PluginStandaloneView.vue'

const store = useSkillStore()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const { t, locale, setLocale } = useI18n()
const toast = useToast()

const userMenuContainerRef = ref<HTMLElement>()
const isUserMenuOpen = ref(false)
const isLaunchingStudio = ref(false)
const showSettings = ref(false)

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
    <header class="h-14 border-b border-slate-200/90 dark:border-slate-800/80 bg-white/95 dark:bg-slate-900/90 px-5 flex items-center justify-between gap-4 flex-shrink-0 z-20">
      <!-- Left: Logo & Ecosystem Badge -->
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white shadow-sm shadow-emerald-500/25 font-bold">
          <i class="pi pi-bolt text-sm"></i>
        </div>
        <div class="flex items-center gap-2">
          <span class="font-black text-sm tracking-tight text-slate-900 dark:text-white">{{ t('portal.appName') }}</span>
          <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            {{ t('portal.superStudioBadge') }}
          </span>
        </div>
      </div>

      <!-- Center: Mode Switcher (Skill Marketplace <-> MCP Protocol Studio) -->
      <div class="flex items-center bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl border border-slate-200 dark:border-slate-700/80">
        <button
          type="button"
          class="flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="store.currentMode === 'skills' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'"
          @click="store.setMode('skills')"
        >
          <i class="pi pi-box text-xs text-emerald-500"></i>
          <span>{{ t('portal.modeSkills') }}</span>
        </button>

        <button
          type="button"
          class="flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="store.currentMode === 'mcp' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'"
          @click="store.setMode('mcp')"
        >
          <i class="pi pi-share-alt text-xs text-teal-400"></i>
          <span>{{ t('portal.modeMcp') }}</span>
        </button>
      </div>

      <!-- Right: Action Buttons, Theme, Language & User Profile -->
      <div class="flex items-center gap-2.5 flex-shrink-0">
        <!-- Launch AIPRO Studio Button -->
        <button
          type="button"
          :disabled="isLaunchingStudio"
          class="py-1.5 px-3.5 text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white rounded-xl shadow-md shadow-emerald-500/25 transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-60 flex-shrink-0 active:scale-95"
          @click="handleLaunchStudio"
        >
          <i v-if="isLaunchingStudio" class="pi pi-spinner animate-spin text-xs"></i>
          <i v-else class="pi pi-external-link text-xs"></i>
          <span>{{ t('portal.launchStudioBtn') }}</span>
        </button>

        <!-- Multi-language Switcher (VI | EN | KO) -->
        <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl p-1 shadow-xs">
          <button
            type="button"
            class="px-2 py-0.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
            :class="locale === 'vi' ? 'bg-emerald-500 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
            @click="switchLang('vi')"
          >
            VI
          </button>
          <button
            type="button"
            class="px-2 py-0.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
            :class="locale === 'en' ? 'bg-emerald-500 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
            @click="switchLang('en')"
          >
            EN
          </button>
          <button
            type="button"
            class="px-2 py-0.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
            :class="locale === 'ko' ? 'bg-emerald-500 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
            @click="switchLang('ko')"
          >
            KO
          </button>
        </div>

        <!-- Dark/Light Theme Toggle -->
        <button
          type="button"
          class="p-2 rounded-xl text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          :title="settingsStore.darkMode ? t('portal.themeLightTitle') : t('portal.themeDarkTitle')"
          @click="settingsStore.toggleDarkMode"
        >
          <i :class="settingsStore.darkMode ? 'pi pi-sun text-amber-400' : 'pi pi-moon text-slate-600'"></i>
        </button>

        <!-- User Profile Avatar & Solid Dropdown Menu -->
        <div class="relative" ref="userMenuContainerRef">
          <button
            type="button"
            data-testid="header-user-btn"
            class="flex items-center gap-2 p-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
            @click="isUserMenuOpen = !isUserMenuOpen"
          >
            <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-xs shadow-xs">
              {{ (authStore.currentUser?.name || 'AX').substring(0, 2).toUpperCase() }}
            </div>
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-200 hidden sm:inline max-w-[120px] truncate">
              {{ authStore.currentUser?.name || t('portal.guestName') }}
            </span>
            <i class="pi pi-chevron-down text-[10px] text-slate-400 transition-transform duration-200" :class="{ 'rotate-180': isUserMenuOpen }"></i>
          </button>

          <!-- Solid Floating Dropdown Menu (Guaranteed Opaque, Z-9999) -->
          <div
            v-if="isUserMenuOpen"
            data-testid="user-dropdown-menu"
            class="absolute right-0 top-full mt-2 w-72 rounded-2xl border border-slate-700/80 shadow-2xl shadow-black/80 p-1.5 z-[9999] flex flex-col gap-0.5 select-none"
            style="background-color: #0f172a !important;"
          >
            <!-- User Info Header -->
            <div class="px-3.5 py-2.5 border-b border-slate-800 mb-1 flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 flex items-center justify-center text-white font-bold text-xs shadow-md shadow-emerald-500/20 flex-shrink-0">
                {{ (authStore.currentUser?.name || 'AX').substring(0, 2).toUpperCase() }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-xs font-bold text-white truncate flex items-center gap-1.5">
                  <span>{{ authStore.currentUser?.name || t('portal.guestName') }}</span>
                  <span class="text-[9px] font-mono px-1.5 py-0.2 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">PRO</span>
                </div>
                <div class="text-[11px] text-slate-400 font-mono truncate mt-0.5">
                  {{ authStore.currentUser?.email || 'offline@aipro.local' }}
                </div>
              </div>
            </div>

            <button
              type="button"
              class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold text-slate-200 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer text-left"
              @click="showSettings = true; isUserMenuOpen = false"
            >
              <div class="flex items-center gap-2.5">
                <i class="pi pi-cog text-emerald-400 text-xs"></i>
                <span>{{ t('portal.settingsMenu') }}</span>
              </div>
              <kbd class="text-[10px] font-mono text-slate-400 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">Ctrl+,</kbd>
            </button>

            <button
              type="button"
              class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold text-slate-200 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer text-left"
              @click="handleAutostartToggle"
            >
              <div class="flex items-center gap-2.5">
                <i class="pi pi-desktop text-teal-400 text-xs"></i>
                <span>{{ t('portal.autostartMenu') }}</span>
              </div>
              <span class="text-[10px] font-bold px-1.5 py-0.5 rounded" :class="store.autostartEnabled ? 'text-emerald-400 bg-emerald-500/10' : 'text-slate-500 bg-slate-800'">
                {{ store.autostartEnabled ? 'BẬT' : 'TẮT' }}
              </span>
            </button>

            <button
              type="button"
              class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold text-slate-200 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer text-left"
              @click="handleCheckUpdates"
            >
              <div class="flex items-center gap-2.5">
                <i class="pi pi-sync text-cyan-400 text-xs"></i>
                <span>{{ t('portal.checkUpdatesMenu') }}</span>
              </div>
              <span class="text-[10px] font-mono text-slate-400">v{{ store.appVersion }}</span>
            </button>

            <div class="h-px bg-slate-800 my-1"></div>

            <button
              type="button"
              class="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-rose-400 hover:text-rose-300 hover:bg-rose-950/40 transition-colors cursor-pointer text-left"
              @click="authStore.logout(); isUserMenuOpen = false"
            >
              <i class="pi pi-power-off text-rose-400 text-xs"></i>
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
        <PluginStandaloneView :embedded="true" />
      </div>

      <!-- Mode 2: Skill Marketplace Mode -->
      <div v-else class="h-full flex flex-col min-h-0 overflow-hidden">
        <!-- Sub-navigation Tabs (Marketplace, Installed, Projects) -->
        <div class="h-11 border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-900/50 px-6 flex items-center justify-between flex-shrink-0">
          <div class="flex items-center gap-6 h-full">
            <button
              type="button"
              class="h-full flex items-center gap-2 border-b-2 text-xs font-bold transition-all cursor-pointer"
              :class="store.activeTab === 'marketplace' ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
              @click="store.setActiveTab('marketplace')"
            >
              <i class="pi pi-compass text-xs"></i>
              <span>{{ t('portal.tabMarketplace') }}</span>
              <Tag :value="String(store.skills.length)" severity="secondary" class="!text-[10px] !py-0 !px-1.5 !font-mono" />
            </button>

            <button
              type="button"
              class="h-full flex items-center gap-2 border-b-2 text-xs font-bold transition-all cursor-pointer"
              :class="store.activeTab === 'installed' ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
              @click="store.setActiveTab('installed')"
            >
              <i class="pi pi-check-circle text-xs"></i>
              <span>{{ t('portal.tabInstalled') }}</span>
              <Tag :value="String(store.installedSkills.length)" severity="success" class="!text-[10px] !py-0 !px-1.5 !font-mono" />
            </button>

            <button
              type="button"
              class="h-full flex items-center gap-2 border-b-2 text-xs font-bold transition-all cursor-pointer"
              :class="store.activeTab === 'projects' ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
              @click="store.setActiveTab('projects')"
            >
              <i class="pi pi-folder text-xs"></i>
              <span>{{ t('portal.tabProjects') }}</span>
              <Tag :value="String(store.recentProjects.length)" severity="info" class="!text-[10px] !py-0 !px-1.5 !font-mono" />
            </button>
          </div>

          <!-- Current active workspace indicator -->
          <div v-if="store.currentProject" class="hidden md:flex items-center gap-1.5 text-xs text-slate-400">
            <i class="pi pi-folder-open text-xs text-emerald-500"></i>
            <span class="font-mono text-[11px] truncate max-w-xs">{{ store.currentProject }}</span>
          </div>
        </div>

        <!-- Tab Content Layout -->
        <div class="flex-1 flex min-h-0 overflow-hidden">
          <!-- Marketplace & Installed: 2-column layout (List + Detail) -->
          <template v-if="store.activeTab === 'marketplace' || store.activeTab === 'installed'">
            <div class="w-80 md:w-96 lg:w-[420px] flex-shrink-0 h-full overflow-hidden">
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
    </div>

    <!-- Modals -->
    <ScopeModal />
    <FolderPickerModal />
    <CloneSkillModal />
    <UpdateDialog />
    <SettingsDialog v-model:visible="showSettings" />
  </div>
</template>
