<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSkillStore } from './stores/skillStore'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { useSettingsStore } from '@/features/settings/stores/settingsStore'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Menu from 'primevue/menu'
import { useToast } from 'primevue/usetoast'

import SkillList from './components/SkillList.vue'
import SkillDetailPanel from './components/SkillDetailPanel.vue'
import ProjectListPanel from './components/ProjectListPanel.vue'
import ScopeModal from './components/ScopeModal.vue'
import FolderPickerModal from './components/FolderPickerModal.vue'
import CloneSkillModal from './components/CloneSkillModal.vue'
import UpdateDialog from './components/UpdateDialog.vue'

// Import existing MCP standalone view for mode switching
import PluginStandaloneView from '@/features/plugins/views/PluginStandaloneView.vue'

const store = useSkillStore()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const toast = useToast()

const userMenu = ref()
const isLaunchingStudio = ref(false)

const userMenuItems = ref([
  {
    label: 'Khởi động cùng Windows',
    icon: 'pi pi-desktop',
    command: async () => {
      await store.setAutostart(!store.autostartEnabled)
      toast.add({
        severity: 'info',
        summary: 'Cài đặt hệ thống',
        detail: store.autostartEnabled ? 'Đã bật khởi động cùng Windows' : 'Đã tắt khởi động cùng Windows',
        life: 2500,
      })
    },
  },
  {
    label: 'Kiểm tra cập nhật',
    icon: 'pi pi-sync',
    command: async () => {
      await store.checkForUpdates()
      if (!store.availableUpdate) {
        toast.add({
          severity: 'success',
          summary: 'Cập nhật',
          detail: 'Bạn đang sử dụng phiên bản mới nhất (v1.0.0)',
          life: 2500,
        })
      }
    },
  },
  { separator: true },
  {
    label: 'Đăng xuất tài khoản',
    icon: 'pi pi-power-off',
    class: 'text-rose-500 font-bold',
    command: () => {
      authStore.logout()
    },
  },
])

function toggleUserMenu(event: Event) {
  userMenu.value.toggle(event)
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
          <span class="font-black text-sm tracking-tight text-slate-900 dark:text-white">AX Desktop</span>
          <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            AIPRO Super Studio
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
          <span>Skill Marketplace</span>
        </button>

        <button
          type="button"
          class="flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="store.currentMode === 'mcp' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'"
          @click="store.setMode('mcp')"
        >
          <i class="pi pi-share-alt text-xs text-teal-400"></i>
          <span>MCP Protocol Studio</span>
        </button>
      </div>

      <!-- Right: Action Buttons, Theme, Language & User Profile -->
      <div class="flex items-center gap-2.5">
        <!-- Launch AIPRO Studio Button -->
        <Button
          type="button"
          label="Mở AIPRO Studio"
          icon="pi pi-external-link"
          :loading="isLaunchingStudio"
          class="!py-1.5 !px-3 !text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-xs cursor-pointer !rounded-xl"
          @click="handleLaunchStudio"
        />

        <!-- Dark/Light Theme Toggle -->
        <button
          type="button"
          class="p-2 rounded-xl text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          :title="settingsStore.darkMode ? 'Chuyển sang Giao diện Sáng' : 'Chuyển sang Giao diện Tối'"
          @click="settingsStore.toggleDarkMode"
        >
          <i :class="settingsStore.darkMode ? 'pi pi-sun text-amber-400' : 'pi pi-moon text-slate-600'"></i>
        </button>

        <!-- User Profile Avatar & Menu -->
        <div class="relative">
          <button
            type="button"
            class="flex items-center gap-2 p-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
            @click="toggleUserMenu"
          >
            <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-xs shadow-xs">
              {{ (authStore.currentUser?.name || 'AX').substring(0, 2).toUpperCase() }}
            </div>
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-200 hidden sm:inline max-w-[100px] truncate">
              {{ authStore.currentUser?.name || 'Khách' }}
            </span>
            <i class="pi pi-chevron-down text-[10px] text-slate-400"></i>
          </button>
          <Menu ref="userMenu" :model="userMenuItems" :popup="true" class="!rounded-2xl !text-xs" />
        </div>
      </div>
    </header>

    <!-- Main Workspace View -->
    <div class="flex-1 flex flex-col min-h-0 overflow-hidden relative">
      <!-- Mode 1: MCP Protocol Studio Mode -->
      <div v-if="store.currentMode === 'mcp'" class="h-full w-full overflow-hidden">
        <PluginStandaloneView />
      </div>

      <!-- Mode 2: Skill Marketplace Mode -->
      <div v-else class="h-full flex flex-col overflow-hidden">
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
              <span>Marketplace</span>
              <Tag :value="String(store.skills.length)" severity="secondary" class="!text-[10px] !py-0 !px-1.5 !font-mono" />
            </button>

            <button
              type="button"
              class="h-full flex items-center gap-2 border-b-2 text-xs font-bold transition-all cursor-pointer"
              :class="store.activeTab === 'installed' ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
              @click="store.setActiveTab('installed')"
            >
              <i class="pi pi-check-circle text-xs"></i>
              <span>Đã cài đặt</span>
              <Tag :value="String(store.installedSkills.length)" severity="success" class="!text-[10px] !py-0 !px-1.5 !font-mono" />
            </button>

            <button
              type="button"
              class="h-full flex items-center gap-2 border-b-2 text-xs font-bold transition-all cursor-pointer"
              :class="store.activeTab === 'projects' ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
              @click="store.setActiveTab('projects')"
            >
              <i class="pi pi-folder text-xs"></i>
              <span>Quản lý Dự án</span>
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
  </div>
</template>
