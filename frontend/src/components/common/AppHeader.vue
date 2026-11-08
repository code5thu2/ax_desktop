<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSettingsStore } from '@/features/settings/stores/settingsStore'
import { usePluginStore } from '@/features/plugins/stores/pluginStore'
import PageMascot from '@/components/common/PageMascot.vue'

const emit = defineEmits<{
  (e: 'openSettings'): void
}>()

const settingsStore = useSettingsStore()
const pluginStore = usePluginStore()

const copiedToast = ref(false)

const gatewayLabel = computed(() => {
  if (!pluginStore.isServerOnline) return 'Offline'
  try {
    const u = new URL(pluginStore.registryServerUrl)
    return `Gateway :${u.port || (u.protocol === 'https:' ? '443' : '80')}`
  } catch {
    return 'Gateway'
  }
})

function copyEndpoint() {
  const url = `${pluginStore.registryServerUrl}/mcp`
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(url)
  }
  copiedToast.value = true
  setTimeout(() => {
    copiedToast.value = false
  }, 2000)
}

function refreshCatalog() {
  pluginStore.fetchCatalogFromServer()
}
</script>

<template>
  <header class="h-13 border-b border-[#e5e5e5] dark:border-[#2e2e2e] bg-white dark:bg-[#1a1a1a] px-4 flex items-center justify-between gap-4 flex-shrink-0 z-20 select-none transition-colors duration-200">
    <!-- LEFT: Branding, Mascot & Server Status Chip -->
    <div class="flex items-center gap-3 shrink-0">
      <div class="flex items-center gap-2">
        <!-- Logo Icon -->
        <div class="w-7 h-7 rounded-lg bg-emerald-500/10 dark:bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 font-bold text-xs shadow-2xs">
          <i class="pi pi-box text-sm"></i>
        </div>

        <span class="font-bold text-sm tracking-tight text-slate-800 dark:text-[#ececec]" data-testid="header-plugin-title">
          MCP PROTOCOL STUDIO
        </span>

        <span class="text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-[#2b2b2b] text-neutral-500 dark:text-neutral-400 font-mono font-medium hidden sm:inline border border-neutral-200 dark:border-[#383838]">
          PRIVATE REGISTRY
        </span>

        <!-- Interactive Koboyo TV Mascot -->
        <PageMascot
          :size="28"
          directions="/mascots/tv-directions.webp"
          reactions="/mascots/tv-reactions.webp"
          class="ml-0.5"
          label="MCP Studio Mascot"
        />
      </div>

      <div class="h-4 w-px bg-neutral-200 dark:bg-[#333333] hidden sm:block"></div>

      <!-- Gateway Server Status Pill with Click-to-Copy -->
      <button
        type="button"
        data-testid="header-gateway-pill"
        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono border transition cursor-pointer active:scale-95"
        :class="pluginStore.isServerOnline 
          ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20' 
          : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30 hover:bg-amber-500/20'"
        :title="copiedToast ? 'Đã sao chép: ' + pluginStore.registryServerUrl + '/mcp' : 'Nhấp để sao chép endpoint: ' + pluginStore.registryServerUrl + '/mcp'"
        @click="copyEndpoint"
      >
        <span class="w-2 h-2 rounded-full" :class="pluginStore.isServerOnline ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'"></span>
        <span>{{ copiedToast ? 'Đã sao chép URL!' : gatewayLabel }}</span>
        <i class="pi pi-copy text-[10px] opacity-70"></i>
      </button>

      <!-- Refresh Catalog Button -->
      <button
        type="button"
        data-testid="btn-refresh-catalog"
        class="w-7 h-7 rounded-lg hover:bg-neutral-100 dark:hover:bg-[#2b2b2b] text-neutral-500 dark:text-neutral-400 flex items-center justify-center cursor-pointer transition border border-transparent hover:border-neutral-200 dark:hover:border-[#383838]"
        title="Làm mới danh mục MCP từ server"
        @click="refreshCatalog"
      >
        <i class="pi pi-sync text-xs" :class="{ 'animate-spin': pluginStore.isLoadingCatalog }"></i>
      </button>
    </div>

    <!-- RIGHT: Primary Actions, Theme Toggle & Settings -->
    <div class="flex items-center gap-2 shrink-0">
      <!-- Action: Import Git Button -->
      <button
        type="button"
        data-testid="btn-main-import-git"
        class="px-3 py-1.5 rounded-lg bg-[#24292F] hover:bg-black text-white flex items-center gap-1.5 font-semibold text-xs cursor-pointer shadow-xs transition active:scale-95"
        title="Nộp link Git / GitHub để tự động import MCP"
        @click="pluginStore.showGitImportModal = true"
      >
        <i class="pi pi-github text-xs"></i>
        <span>Import Git</span>
      </button>

      <!-- Action: Upload Code Button -->
      <button
        type="button"
        data-testid="btn-main-upload-code"
        class="px-3 py-1.5 rounded-lg bg-white dark:bg-[#262626] border border-[#d4d4d4] dark:border-[#3a3a3a] hover:bg-neutral-50 dark:hover:bg-[#2e2e2e] text-slate-800 dark:text-neutral-200 flex items-center gap-1.5 font-semibold text-xs cursor-pointer shadow-xs transition active:scale-95"
        title="Tải lên file code MCP (.py, .zip)"
        @click="pluginStore.showUploadModal = true"
      >
        <i class="pi pi-upload text-xs text-emerald-600 dark:text-emerald-400"></i>
        <span>Upload</span>
      </button>

      <div class="h-4 w-px bg-neutral-200 dark:bg-[#383838] mx-1"></div>

      <!-- Theme Toggle Button -->
      <button
        type="button"
        data-testid="theme-toggle-btn"
        class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-600 dark:text-[#ececec] hover:bg-[#f0f0f0] dark:hover:bg-[#2b2b2b] active:scale-95 transition cursor-pointer"
        :title="settingsStore.darkMode ? 'Chuyển sang Giao diện Sáng' : 'Chuyển sang Giao diện Tối'"
        @click="settingsStore.toggleDarkMode"
      >
        <i
          :class="settingsStore.darkMode ? 'pi pi-sun text-xs text-amber-300' : 'pi pi-moon text-xs text-slate-700'"
        ></i>
      </button>

      <!-- Settings Button -->
      <button
        type="button"
        data-testid="header-settings-btn"
        class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-600 dark:text-[#ececec] hover:bg-[#f0f0f0] dark:hover:bg-[#2b2b2b] active:scale-95 transition cursor-pointer"
        title="Cài đặt hệ thống & Gateway"
        @click="emit('openSettings')"
      >
        <i class="pi pi-cog text-xs"></i>
      </button>
    </div>
  </header>
</template>
