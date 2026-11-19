<script setup lang="ts">
import { computed, ref } from 'vue'
import Tag from 'primevue/tag'
import { usePluginStore } from '../stores/pluginStore'
import { useI18n } from '@/i18n'
import { AxButton, AxIcon } from '@/components/ui'

const emit = defineEmits<{
  (e: 'import-git'): void
  (e: 'upload-zip'): void
}>()

const pluginStore = usePluginStore()
const { t } = useI18n()
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
</script>

<template>
  <div class="h-11 border-b border-slate-200/80 dark:border-[#393B40] bg-white/80 dark:bg-[#1E1F22] px-6 flex items-center justify-between flex-shrink-0 select-none">
    <!-- Left Tabs: Marketplace, Installed -->
    <div class="flex items-center gap-6 h-full">
      <button
        type="button"
        data-testid="tab-marketplace"
        class="h-full flex items-center gap-2 border-b-2 text-xs font-bold transition-all cursor-pointer"
        :class="pluginStore.activeTab === 'marketplace' ? 'border-[#3574F0] text-[#3574F0] dark:text-[#56A8F5]' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
        @click="pluginStore.setActiveTab('marketplace')"
      >
        <AxIcon name="search" size="sm" />
        <span>{{ t('mcpStudio.tabMarketplace') }}</span>
        <Tag :value="String(pluginStore.plugins.length)" severity="secondary" class="!text-[10px] !py-0 !px-1.5 !font-mono dark:bg-[#393B40] dark:text-[#DFE1E5]" />
      </button>

      <button
        type="button"
        data-testid="tab-installed"
        class="h-full flex items-center gap-2 border-b-2 text-xs font-bold transition-all cursor-pointer"
        :class="pluginStore.activeTab === 'installed' ? 'border-[#3574F0] text-[#3574F0] dark:text-[#56A8F5]' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
        @click="pluginStore.setActiveTab('installed')"
      >
        <AxIcon name="check" size="sm" />
        <span>{{ t('mcpStudio.tabInstalled') }}</span>
        <Tag :value="String(pluginStore.installedCount)" severity="success" class="!text-[10px] !py-0 !px-1.5 !font-mono dark:bg-[#5FAD65]/20 dark:text-[#5FAD65]" />
      </button>
    </div>

    <!-- Right Controls: Gateway Pill, Refresh, Git Import & Upload -->
    <div class="flex items-center gap-2.5">
      <!-- Gateway Server Status Pill with Click-to-Copy -->
      <button
        type="button"
        data-testid="header-gateway-pill"
        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono border transition cursor-pointer active:scale-95"
        :class="pluginStore.isServerOnline 
          ? 'bg-[#5FAD65]/10 text-[#36A15E] dark:text-[#5FAD65] border-[#5FAD65]/30 hover:bg-[#5FAD65]/20' 
          : 'bg-[#E3A83F]/10 text-[#D48800] dark:text-[#F2C55C] border-[#E3A83F]/30 hover:bg-[#E3A83F]/20'"
        :title="copiedToast ? 'Đã sao chép: ' + pluginStore.registryServerUrl + '/mcp' : 'Nhấp để sao chép endpoint: ' + pluginStore.registryServerUrl + '/mcp'"
        @click="copyEndpoint"
      >
        <span class="w-2 h-2 rounded-full" :class="pluginStore.isServerOnline ? 'bg-[#5FAD65] shadow-[0_0_6px_rgba(95,173,101,0.8)]' : 'bg-[#E3A83F]'"></span>
        <span>{{ copiedToast ? 'Đã sao chép URL!' : gatewayLabel }}</span>
        <AxIcon name="copy" size="xs" class="opacity-70" />
      </button>

      <!-- Refresh Catalog Button -->
      <button
        type="button"
        data-testid="btn-refresh-catalog"
        class="w-7 h-7 rounded-lg hover:bg-slate-100 dark:hover:bg-[#393B40] text-slate-500 dark:text-[#868A91] flex items-center justify-center cursor-pointer transition border border-slate-200 dark:border-[#393B40]"
        title="Làm mới danh mục MCP từ server"
        @click="pluginStore.fetchCatalogFromServer"
      >
        <i class="pi pi-sync text-xs" :class="{ 'animate-spin': pluginStore.isLoadingCatalog }"></i>
      </button>

      <!-- Import Git Button -->
      <AxButton
        variant="secondary"
        size="sm"
        ijIcon="git"
        data-testid="btn-main-import-git"
        @click="emit('import-git')"
      >
        <span>{{ t('mcpStudio.btnImportGit') }}</span>
      </AxButton>

      <!-- Upload Zip Button -->
      <AxButton
        variant="primary"
        size="sm"
        ijIcon="download"
        data-testid="btn-main-upload"
        @click="emit('upload-zip')"
      >
        <span>{{ t('mcpStudio.btnUploadZip') }}</span>
      </AxButton>
    </div>
  </div>
</template>
