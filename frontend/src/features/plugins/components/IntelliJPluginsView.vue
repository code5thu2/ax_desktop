<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { usePluginStore } from '../stores/pluginStore'
import type { PluginItem } from '../types/plugin'

interface Props {
  appendTo?: string | HTMLElement
  showList?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  appendTo: 'body',
  showList: true
})

const pluginStore = usePluginStore()
const activeDetailTab = ref<'overview' | 'tools' | 'config' | 'changelog'>('overview')
const showInstallSuccessToast = ref(false)
const toastMessage = ref('')
const isEditingInstalledConfig = ref(false)


// Git Import Modal State
const gitRepoUrl = ref('')
const gitBranch = ref('main')
const gitToken = ref('')
const gitName = ref('')
const gitDesc = ref('')
const isGitImporting = ref(false)
const gitImportError = ref('')

// User-defined environment variable drafts for Upload and Git Import
interface CustomEnvDraft {
  key: string
  label: string
  default: string
  type: 'text' | 'password'
  required: boolean
}
const gitCustomEnvs = ref<CustomEnvDraft[]>([])
const uploadCustomEnvs = ref<CustomEnvDraft[]>([])

function addGitCustomEnv() {
  gitCustomEnvs.value.push({
    key: '',
    label: '',
    default: '',
    type: 'text',
    required: false
  })
}

function removeGitCustomEnv(index: number) {
  gitCustomEnvs.value.splice(index, 1)
}

function addUploadCustomEnv() {
  uploadCustomEnvs.value.push({
    key: '',
    label: '',
    default: '',
    type: 'text',
    required: false
  })
}

function removeUploadCustomEnv(index: number) {
  uploadCustomEnvs.value.splice(index, 1)
}

// File Upload Modal State
const uploadFile = ref<File | null>(null)
const uploadName = ref('')
const uploadDesc = ref('')
const isUploading = ref(false)
const uploadError = ref('')

// Live Tool Testing State
const testingToolName = ref<string | null>(null)
const toolOutputs = ref<Record<string, any>>({})

// MCP Env Configuration Modal State
const showEnvConfigModal = ref(false)
const pendingMcpPlugin = ref<PluginItem | null>(null)
const envConfigValues = ref<Record<string, string>>({})

onMounted(() => {
  pluginStore.fetchCatalogFromServer()
})



async function handleGitImport() {
  if (!gitRepoUrl.value.trim()) return
  isGitImporting.value = true
  gitImportError.value = ''
  try {
    const customEnvs = gitCustomEnvs.value
      .filter((e) => e.key.trim())
      .map((e) => ({
        key: e.key.trim(),
        label: e.label.trim() || undefined,
        default: e.default.trim() || undefined,
        type: e.type,
        required: e.required
      }))

    const res = await pluginStore.importFromGit(
      gitRepoUrl.value.trim(),
      gitBranch.value.trim() || 'main',
      gitToken.value.trim() || undefined,
      gitName.value.trim() || undefined,
      gitDesc.value.trim() || undefined,
      customEnvs.length > 0 ? customEnvs : undefined
    )
    pluginStore.showGitImportModal = false
    gitRepoUrl.value = ''
    gitToken.value = ''
    gitName.value = ''
    gitDesc.value = ''
    gitCustomEnvs.value = []
    toastMessage.value = `Đã nhập và xuất bản thành công MCP: ${res.name} (${res.tools_count} tools)`
    showInstallSuccessToast.value = true
    setTimeout(() => {
      showInstallSuccessToast.value = false
    }, 3000)
  } catch (err: any) {
    gitImportError.value = err.message || 'Lỗi khi nhập Git'
  } finally {
    isGitImporting.value = false
  }
}

function onUploadFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    uploadFile.value = input.files[0]
  }
}

async function handleUploadSubmit() {
  if (!uploadFile.value) return
  isUploading.value = true
  uploadError.value = ''
  try {
    const customEnvs = uploadCustomEnvs.value
      .filter((e) => e.key.trim())
      .map((e) => ({
        key: e.key.trim(),
        label: e.label.trim() || undefined,
        default: e.default.trim() || undefined,
        type: e.type,
        required: e.required
      }))

    const res = await pluginStore.uploadCustomMCP(
      uploadFile.value,
      uploadName.value.trim() || undefined,
      uploadDesc.value.trim() || undefined,
      customEnvs.length > 0 ? customEnvs : undefined
    )
    pluginStore.showUploadModal = false
    uploadFile.value = null
    uploadName.value = ''
    uploadDesc.value = ''
    uploadCustomEnvs.value = []
    toastMessage.value = `Đã upload và xuất bản thành công: ${res.name} (${res.tools_count} tools)`
    showInstallSuccessToast.value = true
    setTimeout(() => {
      showInstallSuccessToast.value = false
    }, 3000)
  } catch (err: any) {
    uploadError.value = err.message || 'Lỗi upload code'
  } finally {
    isUploading.value = false
  }
}

const toolInputArgs = ref<Record<string, string>>({})
const showToolArgsInput = ref<Record<string, boolean>>({})

function toggleToolArgs(toolName: string) {
  showToolArgsInput.value[toolName] = !showToolArgsInput.value[toolName]
}



async function runToolTest(toolName: string) {
  testingToolName.value = toolName
  try {
    let args: Record<string, any> = {}
    if (toolInputArgs.value[toolName]?.trim()) {
      try {
        args = JSON.parse(toolInputArgs.value[toolName].trim())
      } catch (jsonErr: any) {
        toolOutputs.value[toolName] = { error: `JSON tham số không hợp lệ: ${jsonErr.message}` }
        return
      }
    }
    const res = await pluginStore.executeToolDirectly(toolName, args)
    toolOutputs.value[toolName] = res.result || res
  } catch (err: any) {
    toolOutputs.value[toolName] = { error: err.message || 'Gọi tool thất bại' }
  } finally {
    testingToolName.value = null
  }
}

function handleInstall(id: string, name: string) {
  const plugin = pluginStore.plugins.find((p) => p.id === id)
  if (plugin && plugin.envRequirements && plugin.envRequirements.length > 0 && !plugin.installed) {
    pendingMcpPlugin.value = plugin
    isEditingInstalledConfig.value = false
    envConfigValues.value = {}
    plugin.envRequirements.forEach(req => {
      envConfigValues.value[req.key] = req.default || ''
    })
    showEnvConfigModal.value = true
  } else {
    executeInstall(id, name)
  }
}

function openConfigModal(plugin: PluginItem) {
  pendingMcpPlugin.value = plugin
  isEditingInstalledConfig.value = true
  envConfigValues.value = {}
  plugin.envRequirements?.forEach(req => {
    envConfigValues.value[req.key] = (plugin.configuredEnv && plugin.configuredEnv[req.key] !== undefined)
      ? plugin.configuredEnv[req.key]
      : (req.default || '')
  })
  showEnvConfigModal.value = true
}

async function confirmEnvConfigInstall() {
  if (!pendingMcpPlugin.value) return
  const mcp = pendingMcpPlugin.value
  mcp.configuredEnv = { ...envConfigValues.value }
  showEnvConfigModal.value = false

  if (isEditingInstalledConfig.value) {
    await pluginStore.updateMcpConfig(mcp.id, envConfigValues.value)
    isEditingInstalledConfig.value = false
    toastMessage.value = `Đã cập nhật cấu hình cho ${mcp.name}`
    showInstallSuccessToast.value = true
    setTimeout(() => {
      showInstallSuccessToast.value = false
    }, 2500)
  } else {
    executeInstall(mcp.id, mcp.name)
  }
}

function executeInstall(id: string, name: string) {
  pluginStore.installPlugin(id)
  toastMessage.value = `Đã cài đặt thành công MCP Server: ${name}`
  showInstallSuccessToast.value = true
  setTimeout(() => {
    showInstallSuccessToast.value = false
  }, 2500)
}

function handleUninstall(id: string, name: string) {
  pluginStore.uninstallPlugin(id)
  toastMessage.value = `Đã gỡ cài đặt: ${name}`
  showInstallSuccessToast.value = true
  setTimeout(() => {
    showInstallSuccessToast.value = false
  }, 2500)
}
</script>

<template>
  <div class="h-full min-h-0 flex flex-col bg-white dark:bg-[#171717] text-slate-900 dark:text-[#ececec] select-none font-sans">
    <!-- Notification Toast Banner -->
    <div
      v-if="showInstallSuccessToast"
      class="px-4 py-1.5 bg-[#10A37F]/10 border-b border-[#10A37F]/20 text-[#10A37F] text-xs flex items-center justify-between transition-all"
    >
      <div class="flex items-center gap-2">
        <i class="pi pi-check-circle text-xs"></i>
        <span>{{ toastMessage }}</span>
      </div>
      <button type="button" @click="showInstallSuccessToast = false">
        <i class="pi pi-times text-[10px]"></i>
      </button>
    </div>

    <!-- Main Content: IntelliJ Master-Detail Split Pane -->
    <div class="flex-1 flex min-h-0 overflow-hidden">
      <!-- LEFT PANE: Plugins List (~360px - 384px) -->
      <div
        v-show="props.showList"
        data-testid="plugin-list-pane"
        class="w-84 sm:w-96 border-r border-[#e5e5e5] dark:border-[#2e2e2e] bg-[#fbfbfb] dark:bg-[#181818] flex flex-col flex-shrink-0 transition-all duration-200"
      >
        <!-- PANE CONTROL HEADER: Tabs + Search + Category Filter Pills -->
        <div class="p-3 border-b border-[#e5e5e5] dark:border-[#2a2a2a] bg-white dark:bg-[#1e1e1e] space-y-2.5 flex-shrink-0 shadow-2xs">
          <!-- 1. Tabs Segmented Control: Marketplace | Installed -->
          <div class="grid grid-cols-2 p-1 rounded-xl bg-neutral-100 dark:bg-[#141414] border border-neutral-200/80 dark:border-[#2c2c2c] gap-1">
            <button
              type="button"
              data-testid="tab-marketplace"
              class="py-1.5 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center justify-center gap-1.5"
              :class="[
                pluginStore.activeTab === 'marketplace'
                  ? 'bg-white dark:bg-[#2b2b2b] text-slate-900 dark:text-white shadow-xs font-bold'
                  : 'text-neutral-500 dark:text-neutral-400 hover:text-slate-900 dark:hover:text-white'
              ]"
              @click="pluginStore.setActiveTab('marketplace')"
            >
              <i class="pi pi-shopping-bag text-xs"></i>
              <span>Marketplace</span>
            </button>

            <button
              type="button"
              data-testid="tab-installed"
              class="py-1.5 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center justify-center gap-1.5"
              :class="[
                pluginStore.activeTab === 'installed'
                  ? 'bg-white dark:bg-[#2b2b2b] text-slate-900 dark:text-white shadow-xs font-bold'
                  : 'text-neutral-500 dark:text-neutral-400 hover:text-slate-900 dark:hover:text-white'
              ]"
              @click="pluginStore.setActiveTab('installed')"
            >
              <i class="pi pi-check-circle text-xs"></i>
              <span>Installed</span>
              <span
                data-testid="installed-badge-count"
                class="ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold"
                :class="[
                  pluginStore.activeTab === 'installed'
                    ? 'bg-[#10A37F] text-white'
                    : 'bg-neutral-200 dark:bg-[#333333] text-neutral-600 dark:text-neutral-300'
                ]"
              >
                {{ pluginStore.installedCount }}
              </span>
            </button>
          </div>

          <!-- 2. Search Input (Full width of list pane) -->
          <div class="relative w-full">
            <i class="pi pi-search absolute left-2.5 top-1/2 -translate-y-1/2 text-neutral-400 text-xs"></i>
            <input
              v-model="pluginStore.searchQuery"
              data-testid="plugin-search-input"
              type="text"
              placeholder="Tìm kiếm MCP Servers & Tools..."
              class="w-full pl-8 pr-7 py-1.5 text-xs rounded-lg bg-neutral-50 dark:bg-[#141414] border border-[#e5e5e5] dark:border-[#2e2e2e] focus:border-[#10A37F] dark:focus:border-[#10A37F] text-slate-900 dark:text-[#ececec] placeholder:text-neutral-400 focus:outline-none transition shadow-2xs"
            />
            <button
              v-if="pluginStore.searchQuery"
              type="button"
              class="absolute right-2 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 cursor-pointer"
              title="Xóa tìm kiếm"
              @click="pluginStore.searchQuery = ''"
            >
              <i class="pi pi-times text-[10px]"></i>
            </button>
          </div>

          <!-- 3. Category Filter Pills (Exact matching user screenshot) -->
          <div class="grid grid-cols-4 p-0.5 rounded-lg bg-neutral-100 dark:bg-[#141414] border border-neutral-200/80 dark:border-[#2c2c2c] gap-0.5">
            <button
              type="button"
              data-testid="filter-all"
              class="py-1 px-1 rounded-md text-[11px] font-medium transition cursor-pointer text-center"
              :class="pluginStore.filterCategory === 'all'
                ? 'bg-[#10A37F] text-white font-semibold shadow-xs'
                : 'text-neutral-500 dark:text-neutral-400 hover:text-slate-900 dark:hover:text-white'"
              @click="pluginStore.setFilterCategory('all')"
            >
              Tất cả
            </button>
            <button
              type="button"
              data-testid="filter-inhouse"
              class="py-1 px-1 rounded-md text-[11px] font-medium transition cursor-pointer flex items-center justify-center gap-1"
              :class="pluginStore.filterCategory === 'In-House Tools'
                ? 'bg-[#10A37F] text-white font-semibold shadow-xs'
                : 'text-neutral-500 dark:text-neutral-400 hover:text-slate-900 dark:hover:text-white'"
              @click="pluginStore.setFilterCategory('In-House Tools')"
            >
              <i class="pi pi-verified text-[10px]"></i>
              <span>In-House</span>
            </button>
            <button
              type="button"
              data-testid="filter-custom"
              class="py-1 px-1 rounded-md text-[11px] font-medium transition cursor-pointer flex items-center justify-center gap-1"
              :class="pluginStore.filterCategory === 'Custom Tools'
                ? 'bg-[#10A37F] text-white font-semibold shadow-xs'
                : 'text-neutral-500 dark:text-neutral-400 hover:text-slate-900 dark:hover:text-white'"
              @click="pluginStore.setFilterCategory('Custom Tools')"
            >
              <i class="pi pi-code text-[10px]"></i>
              <span>Custom</span>
            </button>
            <button
              type="button"
              data-testid="filter-git"
              class="py-1 px-1 rounded-md text-[11px] font-medium transition cursor-pointer flex items-center justify-center gap-1"
              :class="pluginStore.filterCategory === 'Git Tools'
                ? 'bg-[#10A37F] text-white font-semibold shadow-xs'
                : 'text-neutral-500 dark:text-neutral-400 hover:text-slate-900 dark:hover:text-white'"
              @click="pluginStore.setFilterCategory('Git Tools')"
            >
              <i class="pi pi-github text-[10px]"></i>
              <span>Git</span>
            </button>
          </div>
        </div>

        <!-- Sub-header counter -->
        <div class="px-3.5 py-2 border-b border-[#e5e5e5] dark:border-[#2e2e2e] flex items-center justify-between text-[11px] text-neutral-500 dark:text-neutral-400 font-medium">
          <span>{{ pluginStore.activeTab === 'marketplace' ? 'Available in Store' : 'Installed on Machine' }}</span>
          <span class="font-mono text-xs">{{ pluginStore.filteredPlugins.length }} items</span>
        </div>

        <!-- List items -->
        <div class="flex-1 overflow-y-auto divide-y divide-[#e5e5e5] dark:divide-[#262626]">
          <div
            v-if="pluginStore.filteredPlugins.length === 0"
            class="p-8 text-center text-xs text-neutral-400 dark:text-neutral-500"
          >
            <i class="pi pi-inbox text-2xl mb-2 block"></i>
            <span>No plugins found matching criteria</span>
          </div>

          <div
            v-for="plugin in pluginStore.filteredPlugins"
            :key="plugin.id"
            :data-testid="`plugin-item-${plugin.id}`"
            class="p-3 transition-colors cursor-pointer flex items-start gap-3 relative"
            :class="[
              pluginStore.selectedPlugin?.id === plugin.id
                ? 'bg-white dark:bg-[#262626] border-l-2 border-[#10A37F]'
                : 'hover:bg-neutral-100 dark:hover:bg-[#202020]'
            ]"
            @click="pluginStore.selectPlugin(plugin.id)"
          >
            <!-- Plugin Icon -->
            <div
              class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-2xs mt-0.5"
              :class="[
                plugin.type === 'mcp'
                  ? 'bg-blue-500/10 text-blue-500 dark:text-blue-400 border border-blue-500/20'
                  : 'bg-emerald-500/10 text-[#10A37F] border border-emerald-500/20'
              ]"
            >
              <i :class="[plugin.icon, 'text-sm']"></i>
            </div>

            <!-- Plugin Info -->
            <div class="flex-1 min-w-0 pr-1">
              <div class="flex items-center justify-between gap-1">
                <span class="text-xs font-bold truncate text-slate-900 dark:text-white" :title="plugin.name">
                  {{ plugin.name }}
                </span>
              </div>

              <!-- Badges & Stats row -->
              <div class="flex items-center gap-1.5 mt-1 text-[10px]">
                <!-- Category Badge -->
                <span
                  class="px-1.5 py-0.2 rounded font-mono text-[9px] font-semibold tracking-wider bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20"
                >
                  {{ plugin.category || 'MCP' }}
                </span>
                <span class="text-neutral-400 font-mono">{{ plugin.downloads }}</span>
                <span class="text-amber-500 font-mono">★ {{ plugin.rating }}</span>
              </div>

              <!-- Summary snippet -->
              <p class="text-[11px] text-neutral-500 dark:text-neutral-400 mt-1 line-clamp-1 leading-normal font-normal">
                {{ plugin.summary }}
              </p>
            </div>

            <!-- Action Button / Toggle on Right -->
            <div class="shrink-0 flex items-center self-center" @click.stop>
              <!-- In Marketplace: Install or Installed status -->
              <template v-if="pluginStore.activeTab === 'marketplace'">
                <button
                  v-if="!plugin.installed"
                  type="button"
                  :data-testid="`install-btn-${plugin.id}`"
                  class="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-[#10A37F] hover:bg-[#0e8e6e] active:scale-95 text-white transition cursor-pointer shadow-2xs"
                  @click="handleInstall(plugin.id, plugin.name)"
                >
                  Install
                </button>
                <span
                  v-else
                  class="text-[11px] font-medium text-neutral-400 dark:text-neutral-500 flex items-center gap-1"
                >
                  <i class="pi pi-check text-[10px] text-[#10A37F]"></i>
                  <span>Installed</span>
                </span>
              </template>

              <!-- In Installed tab: Toggle Switch (Enabled/Disabled) -->
              <template v-else>
                <button
                  type="button"
                  :data-testid="`toggle-btn-${plugin.id}`"
                  class="w-8 h-4.5 rounded-full transition-colors relative cursor-pointer flex items-center px-0.5"
                  :class="plugin.enabled ? 'bg-[#10A37F]' : 'bg-neutral-300 dark:bg-[#404040]'"
                  :title="plugin.enabled ? 'Click to disable' : 'Click to enable'"
                  @click="pluginStore.togglePlugin(plugin.id)"
                >
                  <span
                    class="w-3.5 h-3.5 rounded-full bg-white transition-transform shadow-xs"
                    :class="plugin.enabled ? 'translate-x-3.5' : 'translate-x-0'"
                  ></span>
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT PANE: Plugin Detail Preview (IntelliJ Style) -->
      <div v-if="pluginStore.selectedPlugin" class="flex-1 flex flex-col min-w-0 bg-white dark:bg-[#171717] overflow-y-auto">
        <!-- Detail Header -->
        <div class="p-5 border-b border-[#e5e5e5] dark:border-[#2e2e2e] flex items-start justify-between gap-4 flex-shrink-0">
          <div class="flex items-start gap-4 min-w-0">
            <!-- Large Icon -->
            <div
              class="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-xs"
              :class="[
                pluginStore.selectedPlugin.type === 'mcp'
                  ? 'bg-blue-500/10 text-blue-500 dark:text-blue-400 border border-blue-500/20'
                  : 'bg-emerald-500/10 text-[#10A37F] border border-emerald-500/20'
              ]"
            >
              <i :class="[pluginStore.selectedPlugin.icon, 'text-xl']"></i>
            </div>

            <!-- Title & Metadata -->
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-base font-bold text-slate-900 dark:text-white truncate">
                  {{ pluginStore.selectedPlugin.name }}
                </h3>
                <!-- Type Pill -->
                <span
                  class="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase tracking-wider"
                  :class="[
                    pluginStore.selectedPlugin.type === 'mcp'
                      ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20'
                      : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                  ]"
                >
                  {{ pluginStore.selectedPlugin.type }}
                </span>
                <span class="text-[11px] font-mono text-neutral-400">
                  {{ pluginStore.selectedPlugin.version }}
                </span>
              </div>

              <!-- Vendor & Stats -->
              <div class="flex items-center gap-3 mt-1 text-xs text-neutral-500 dark:text-neutral-400">
                <span>By <strong class="text-slate-800 dark:text-slate-200">{{ pluginStore.selectedPlugin.vendor }}</strong></span>
                <span>•</span>
                <span class="text-amber-500 font-mono">★ {{ pluginStore.selectedPlugin.rating }}</span>
                <span>•</span>
                <span class="font-mono">{{ pluginStore.selectedPlugin.downloads }} downloads</span>
              </div>
            </div>
          </div>

          <!-- Top-right Action Buttons -->
          <div class="flex items-center gap-2 shrink-0">
            <template v-if="!pluginStore.selectedPlugin.installed">
              <button
                type="button"
                data-testid="detail-install-btn"
                class="px-4 py-1.5 rounded-lg text-xs font-semibold bg-[#10A37F] hover:bg-[#0e8e6e] text-white transition cursor-pointer flex items-center gap-1.5 shadow-xs active:scale-95"
                @click="handleInstall(pluginStore.selectedPlugin.id, pluginStore.selectedPlugin.name)"
              >
                <i class="pi pi-download text-xs"></i>
                <span>Install</span>
              </button>
            </template>
            <template v-else>
              <!-- Enable / Disable Button -->
              <button
                type="button"
                data-testid="detail-toggle-btn"
                class="px-3 py-1.5 rounded-lg text-xs font-medium border border-[#e5e5e5] dark:border-[#383838] transition cursor-pointer"
                :class="[
                  pluginStore.selectedPlugin.enabled
                    ? 'bg-neutral-100 dark:bg-[#282828] text-slate-800 dark:text-neutral-200 hover:bg-neutral-200 dark:hover:bg-[#333333]'
                    : 'bg-[#10A37F]/10 border-[#10A37F]/30 text-[#10A37F] font-semibold'
                ]"
                @click="pluginStore.togglePlugin(pluginStore.selectedPlugin.id)"
              >
                {{ pluginStore.selectedPlugin.enabled ? 'Disable' : 'Enable' }}
              </button>

              <!-- Configure Button for Installed MCP with env requirements -->
              <button
                v-if="pluginStore.selectedPlugin.installed && pluginStore.selectedPlugin.envRequirements?.length"
                type="button"
                data-testid="detail-config-btn"
                class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-neutral-100 hover:bg-neutral-200 dark:bg-[#2b2b2b] dark:hover:bg-[#383838] text-slate-800 dark:text-neutral-200 transition cursor-pointer flex items-center gap-1.5 border border-[#e5e5e5] dark:border-[#383838] active:scale-95 shadow-2xs"
                title="Xem và chỉnh sửa cấu hình biến môi trường"
                @click="openConfigModal(pluginStore.selectedPlugin)"
              >
                <i class="pi pi-sliders-h text-xs text-amber-500"></i>
                <span>Cấu hình</span>
              </button>

              <!-- Uninstall Button -->
              <button
                type="button"
                data-testid="detail-uninstall-btn"
                class="px-3 py-1.5 rounded-lg text-xs font-medium text-rose-600 dark:text-rose-400 hover:bg-rose-500/10 border border-rose-500/20 transition cursor-pointer"
                @click="handleUninstall(pluginStore.selectedPlugin.id, pluginStore.selectedPlugin.name)"
              >
                Uninstall
              </button>
            </template>
          </div>
        </div>

        <!-- Detail Sub-Navigation (IntelliJ Tabs: Overview, Tools / Triggers, Config, Change Notes) -->
        <div class="px-5 border-b border-[#e5e5e5] dark:border-[#2e2e2e] flex items-center gap-4 flex-shrink-0 bg-[#f9f9f9] dark:bg-[#1f1f1f]">
          <button
            type="button"
            data-testid="subtab-overview"
            class="py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer"
            :class="[
              activeDetailTab === 'overview'
                ? 'border-[#10A37F] text-[#10A37F]'
                : 'border-transparent text-neutral-500 hover:text-slate-900 dark:hover:text-white'
            ]"
            @click="activeDetailTab = 'overview'"
          >
            Overview
          </button>

          <button
            type="button"
            data-testid="subtab-tools"
            class="py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer flex items-center gap-1.5"
            :class="[
              activeDetailTab === 'tools'
                ? 'border-[#10A37F] text-[#10A37F]'
                : 'border-transparent text-neutral-500 hover:text-slate-900 dark:hover:text-white'
            ]"
            @click="activeDetailTab = 'tools'"
          >
            <span>Exposed Tools</span>
            <span class="px-1.5 py-0.2 rounded-full bg-neutral-200 dark:bg-[#2e2e2e] text-[10px] font-mono">
              {{ pluginStore.selectedPlugin.tools?.length || 0 }}
            </span>
          </button>

          <!-- Configuration Tab (For MCPs with Env Requirements) -->
          <button
            v-if="pluginStore.selectedPlugin.envRequirements?.length"
            type="button"
            data-testid="subtab-config"
            class="py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer flex items-center gap-1.5"
            :class="[
              activeDetailTab === 'config'
                ? 'border-[#10A37F] text-[#10A37F]'
                : 'border-transparent text-neutral-500 hover:text-slate-900 dark:hover:text-white'
            ]"
            @click="activeDetailTab = 'config'"
          >
            <i class="pi pi-sliders-h text-xs" :class="activeDetailTab === 'config' ? 'text-[#10A37F]' : 'text-amber-500'"></i>
            <span>Cấu Hình</span>
          </button>

          <button
            type="button"
            data-testid="subtab-changelog"
            class="py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer"
            :class="[
              activeDetailTab === 'changelog'
                ? 'border-[#10A37F] text-[#10A37F]'
                : 'border-transparent text-neutral-500 hover:text-slate-900 dark:hover:text-white'
            ]"
            @click="activeDetailTab = 'changelog'"
          >
            What's New
          </button>
        </div>

        <!-- Detail Sub-Tab Content -->
        <div class="p-5 flex-1 overflow-y-auto text-xs space-y-4">
          <!-- 1. OVERVIEW TAB -->
          <div v-if="activeDetailTab === 'overview'" class="space-y-4">
            <div>
              <h4 class="font-bold text-slate-800 dark:text-slate-100 mb-1.5 text-xs">
                Description
              </h4>
              <p class="text-neutral-600 dark:text-neutral-300 leading-relaxed font-normal">
                {{ pluginStore.selectedPlugin.description }}
              </p>
            </div>

            <!-- Key Features -->
            <div>
              <h4 class="font-bold text-slate-800 dark:text-slate-100 mb-2 text-xs">
                Key Features
              </h4>
              <div class="space-y-1.5">
                <div
                  v-for="(feat, idx) in pluginStore.selectedPlugin.features"
                  :key="idx"
                  class="flex items-start gap-2 text-neutral-600 dark:text-neutral-300"
                >
                  <i class="pi pi-check text-[#10A37F] text-xs mt-0.5 shrink-0"></i>
                  <span>{{ feat }}</span>
                </div>
              </div>
            </div>

            <!-- Plugin Specifications Card -->
            <div class="p-3.5 rounded-xl border border-[#e5e5e5] dark:border-[#2e2e2e] bg-[#f9f9f9] dark:bg-[#212121] grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
              <div>
                <span class="text-neutral-400 block mb-0.5">Plugin Type</span>
                <span class="font-semibold capitalize text-slate-800 dark:text-white">{{ pluginStore.selectedPlugin.type }} Extension</span>
              </div>
              <div>
                <span class="text-neutral-400 block mb-0.5">Execution Environment</span>
                <span class="font-semibold text-slate-800 dark:text-white">{{ pluginStore.selectedPlugin.type === 'mcp' ? 'Model Context Protocol (JSON-RPC)' : 'Prompt-driven Agentic Sub-routine' }}</span>
              </div>
              <div>
                <span class="text-neutral-400 block mb-0.5">Version & Build</span>
                <span class="font-mono text-slate-800 dark:text-white">{{ pluginStore.selectedPlugin.version }}</span>
              </div>
              <div>
                <span class="text-neutral-400 block mb-0.5">Status</span>
                <span
                  class="font-semibold"
                  :class="pluginStore.selectedPlugin.installed ? (pluginStore.selectedPlugin.enabled ? 'text-[#10A37F]' : 'text-neutral-400') : 'text-neutral-500'"
                >
                  {{ pluginStore.selectedPlugin.installed ? (pluginStore.selectedPlugin.enabled ? 'Installed (Active)' : 'Installed (Disabled)') : 'Not Installed' }}
                </span>
              </div>
              <div v-if="pluginStore.selectedPlugin.installed && pluginStore.selectedPlugin.installPath" class="sm:col-span-4 pt-2.5 border-t border-[#e5e5e5] dark:border-[#2e2e2e]">
                <div class="text-neutral-500 dark:text-neutral-400 font-mono text-[11px] flex items-center gap-1.5">
                  <i class="pi pi-folder-open text-xs text-[#10A37F]"></i>
                  <span>{{ pluginStore.selectedPlugin.installPath }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 2. TOOLS TAB -->
          <div v-else-if="activeDetailTab === 'tools'" class="space-y-3">
            <!-- MCP Tools List -->
            <div class="text-[11px] text-neutral-500 dark:text-neutral-400 mb-2">
              MCP Server này cung cấp {{ pluginStore.selectedPlugin.tools?.length || 0 }} công cụ (callable tools) kết nối qua JSON-RPC:
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
              <div
                v-for="tool in pluginStore.selectedPlugin.tools"
                :key="tool.name"
                class="p-3 rounded-xl border border-[#e5e5e5] dark:border-[#2e2e2e] bg-[#f9f9f9] dark:bg-[#212121] flex flex-col justify-between"
              >
                <div>
                  <div class="flex items-center justify-between gap-2 mb-1">
                    <div class="flex items-center gap-2">
                      <span class="font-mono font-bold text-xs text-blue-600 dark:text-blue-400">
                        {{ tool.name }}
                      </span>
                      <span class="text-[10px] px-1.5 py-0.2 rounded bg-neutral-200 dark:bg-[#333333] font-mono text-neutral-500">
                        tool
                      </span>
                    </div>
                    <div class="flex items-center gap-1">
                      <button
                        type="button"
                        class="px-1.5 py-0.5 rounded text-[10px] text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200 hover:bg-neutral-200 dark:hover:bg-[#2e2e2e] transition cursor-pointer"
                        :class="showToolArgsInput[tool.name] ? 'bg-neutral-200 dark:bg-[#2e2e2e] text-blue-500' : ''"
                        :title="showToolArgsInput[tool.name] ? 'Ẩn ô nhập tham số' : 'Nhập tham số JSON'"
                        @click="toggleToolArgs(tool.name)"
                      >
                        <i class="pi pi-code text-[10px]"></i>
                        <span class="ml-0.5 text-[9px] font-mono">JSON</span>
                      </button>
                      <button
                        type="button"
                        class="px-2 py-0.5 rounded text-[10px] font-medium bg-blue-500/10 hover:bg-blue-500/20 text-blue-600 dark:text-blue-400 transition cursor-pointer flex items-center gap-1"
                        :disabled="testingToolName === tool.name"
                        title="Gọi thử nghiệm tool qua HTTP Gateway"
                        @click="runToolTest(tool.name)"
                      >
                        <i v-if="testingToolName === tool.name" class="pi pi-spin pi-spinner text-[9px]"></i>
                        <i v-else class="pi pi-play text-[9px]"></i>
                        <span>Chạy Thử</span>
                      </button>
                    </div>
                  </div>
                  <p class="text-[11px] text-neutral-600 dark:text-neutral-300">
                    {{ tool.description }}
                  </p>

                  <!-- Parameters list badge -->
                  <div
                    v-if="tool.parameters && (Array.isArray(tool.parameters) ? tool.parameters.length : Object.keys(tool.parameters?.properties || {}).length)"
                    class="mt-1.5 flex flex-wrap items-center gap-1"
                  >
                    <span class="text-[10px] text-neutral-400">Tham số:</span>
                    <span
                      v-for="p in (Array.isArray(tool.parameters) ? tool.parameters : Object.keys(tool.parameters?.properties || {}))"
                      :key="p"
                      class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-neutral-200/80 dark:bg-[#2b2b2b] text-neutral-600 dark:text-neutral-400"
                    >
                      {{ p }}
                    </span>
                  </div>

                  <!-- Optional JSON Input for Tool Testing -->
                  <div v-if="showToolArgsInput[tool.name]" class="mt-2 space-y-1">
                    <div class="text-[10px] text-neutral-400 flex items-center justify-between">
                      <span>Nhập tham số gọi tool (JSON format):</span>
                    </div>
                    <input
                      v-model="toolInputArgs[tool.name]"
                      type="text"
                      placeholder='{"param": "value"}'
                      class="w-full text-[10px] font-mono py-1 px-2 rounded border border-[#e5e5e5] dark:border-[#383838] bg-white dark:bg-[#1a1a1a] text-slate-800 dark:text-slate-200"
                      @keydown.enter="runToolTest(tool.name)"
                    />
                  </div>
                </div>

                <!-- Live Test Call Output -->
                <div v-if="toolOutputs[tool.name]" class="mt-2.5 pt-2 border-t border-[#e5e5e5] dark:border-[#2e2e2e]">
                  <div class="text-[10px] font-mono text-neutral-400 mb-1 flex items-center justify-between">
                    <span>Phản hồi Gateway:</span>
                    <button type="button" class="text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200" @click="delete toolOutputs[tool.name]">
                      <i class="pi pi-times text-[9px]"></i>
                    </button>
                  </div>
                  <pre class="p-2 rounded bg-neutral-900 text-emerald-400 text-[10px] font-mono overflow-x-auto max-h-32">{{ JSON.stringify(toolOutputs[tool.name], null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. CONFIGURATION (ENV) TAB -->
          <div v-else-if="activeDetailTab === 'config'" class="space-y-4">
            <div class="flex items-center justify-between pb-2 border-b border-[#e5e5e5] dark:border-[#2e2e2e]">
              <div>
                <h4 class="font-bold text-slate-800 dark:text-slate-100 text-xs flex items-center gap-1.5">
                  <i class="pi pi-sliders-h text-amber-500"></i>
                  <span>Cấu Hình Biến Môi Trường (Environment Variables)</span>
                </h4>
                <p class="text-[11px] text-neutral-500 dark:text-neutral-400 mt-0.5">
                  Cấu hình các tham số kết nối, tài khoản, API keys cho MCP {{ pluginStore.selectedPlugin.name }}.
                </p>
              </div>
              <button
                type="button"
                data-testid="btn-open-config-modal"
                class="px-3 py-1.5 rounded-lg bg-[#10A37F] hover:bg-[#0e8e6e] text-white font-semibold text-xs transition cursor-pointer flex items-center gap-1.5 shadow-2xs active:scale-95"
                @click="openConfigModal(pluginStore.selectedPlugin)"
              >
                <i class="pi pi-file-edit text-xs"></i>
                <span>Chỉnh Sửa Cấu Hình</span>
              </button>
            </div>

            <!-- Current Values Card List -->
            <div class="grid grid-cols-1 gap-2.5">
              <div
                v-for="req in pluginStore.selectedPlugin.envRequirements"
                :key="req.key"
                class="p-3.5 rounded-xl border border-[#e5e5e5] dark:border-[#2e2e2e] bg-[#f9f9f9] dark:bg-[#212121] flex items-center justify-between"
              >
                <div class="space-y-0.5 min-w-0 pr-4">
                  <div class="flex items-center gap-2">
                    <span class="font-mono font-bold text-xs text-blue-600 dark:text-blue-400">
                      {{ req.key }}
                    </span>
                    <span v-if="req.required" class="text-[9px] px-1.5 py-0.2 rounded bg-rose-500/10 text-rose-500 font-mono">
                      required
                    </span>
                  </div>
                  <div class="text-[11px] text-neutral-500 dark:text-neutral-400">
                    {{ req.label || req.key }}
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <span class="font-mono text-xs px-2.5 py-1 rounded bg-white dark:bg-[#171717] border border-[#e5e5e5] dark:border-[#333333] text-slate-800 dark:text-slate-200">
                    {{ (pluginStore.selectedPlugin.configuredEnv && pluginStore.selectedPlugin.configuredEnv[req.key] !== undefined)
                        ? (req.key.toLowerCase().includes('pass') || req.key.toLowerCase().includes('token') || req.key.toLowerCase().includes('secret')
                            ? '••••••••'
                            : pluginStore.selectedPlugin.configuredEnv[req.key] || '(chưa đặt)')
                        : (req.default || '(mặc định)') }}
                  </span>
                </div>
              </div>
            </div>

            <div class="text-[11px] text-neutral-400 flex items-center gap-1.5 pt-1">
              <i class="pi pi-info-circle text-xs text-neutral-400"></i>
              <span>Cấu hình được lưu trực tiếp vào file <code>.env</code> bên trong thư mục sandbox của MCP và áp dụng tức thì.</span>
            </div>
          </div>

          <!-- 4. CHANGELOG TAB -->
          <div v-else-if="activeDetailTab === 'changelog'" class="space-y-3">
            <div class="p-4 rounded-xl border border-[#e5e5e5] dark:border-[#2e2e2e] bg-[#f9f9f9] dark:bg-[#212121]">
              <div class="flex items-center justify-between mb-2">
                <span class="font-bold text-slate-800 dark:text-white text-xs">Release Notes</span>
                <span class="font-mono text-neutral-400 text-[11px]">{{ pluginStore.selectedPlugin.version }}</span>
              </div>
              <p class="text-[11px] text-neutral-600 dark:text-neutral-300 font-mono leading-relaxed">
                {{ pluginStore.selectedPlugin.changeNotes || 'Regular maintenance and performance optimizations.' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Git Repository Import Dialog -->
    <Dialog
      v-model:visible="pluginStore.showGitImportModal"
      modal
      header="Import MCP Server từ Git / GitHub"
      :style="{ width: '560px', maxWidth: '95vw' }"
      class="!rounded-2xl overflow-hidden shadow-2xl !bg-white dark:!bg-[#1e1e1e] !text-slate-800 dark:!text-[#ececec]"
    >
      <div class="space-y-3.5 text-xs">
        <p class="text-neutral-500 dark:text-neutral-400">
          Dán link repository (GitHub hoặc GitLab). Server sẽ tự động clone, phân tích AST và xuất bản MCP lên Marketplace.
        </p>

        <div v-if="gitImportError" class="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400">
          <i class="pi pi-exclamation-triangle mr-1"></i>
          <span>{{ gitImportError }}</span>
        </div>

        <div>
          <label class="block font-semibold mb-1">Git Repository URL <span class="text-rose-500">*</span></label>
          <InputText
            v-model="gitRepoUrl"
            class="w-full !text-xs !py-2 !px-3 font-mono !rounded-lg"
            placeholder="https://github.com/my-org/my-mcp.git"
          />
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block font-semibold mb-1">Branch / Tag</label>
            <InputText
              v-model="gitBranch"
              class="w-full !text-xs !py-2 !px-3 font-mono !rounded-lg"
              placeholder="main"
            />
          </div>
          <div>
            <label class="block font-semibold mb-1">Tên Hiển Thị (Tùy chọn)</label>
            <InputText
              v-model="gitName"
              class="w-full !text-xs !py-2 !px-3 !rounded-lg"
              placeholder="VD: My Tool"
            />
          </div>
        </div>

        <div>
          <label class="block font-semibold mb-1">Token Xác Thực (Cho Private Repo)</label>
          <InputText
            v-model="gitToken"
            type="password"
            class="w-full !text-xs !py-2 !px-3 font-mono !rounded-lg"
            placeholder="ghp_xxxxxxxxxxxx (để trống nếu public)"
          />
        </div>

        <div>
          <label class="block font-semibold mb-1">Mô Tả Ngắn (Tùy chọn)</label>
          <InputText
            v-model="gitDesc"
            class="w-full !text-xs !py-2 !px-3 !rounded-lg"
            placeholder="VD: Công cụ quản lý đơn hàng nội bộ"
          />
        </div>

        <!-- Khai báo / Bổ sung Biến Môi Trường -->
        <div class="border-t border-[#e5e5e5] dark:border-[#2e2e2e] pt-3">
          <div class="flex items-center justify-between mb-2">
            <div>
              <span class="font-semibold text-xs text-slate-800 dark:text-neutral-200">Khai báo Biến Môi Trường (Tùy chọn)</span>
              <span class="text-[11px] text-neutral-400 block">Thêm hoặc ghi đè nhãn/loại biến (API Key, URL, Secret...)</span>
            </div>
            <button
              type="button"
              class="text-[11px] px-2.5 py-1 rounded-md bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-medium transition cursor-pointer flex items-center gap-1 shrink-0"
              @click="addGitCustomEnv"
            >
              <i class="pi pi-plus text-[10px]"></i>
              <span>Thêm biến</span>
            </button>
          </div>

          <div v-if="gitCustomEnvs.length === 0" class="p-2.5 rounded-lg border border-dashed border-neutral-200 dark:border-[#333] text-center text-[11px] text-neutral-400">
            Hệ thống sẽ tự động quét biến qua AST. Bấm <b>"+ Thêm biến"</b> nếu muốn bổ sung hoặc chỉ định nhãn/mật khẩu riêng.
          </div>

          <div v-else class="space-y-2 max-h-48 overflow-y-auto pr-1">
            <div
              v-for="(item, idx) in gitCustomEnvs"
              :key="idx"
              class="p-2 rounded-lg bg-neutral-50 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] space-y-1.5"
            >
              <div class="flex items-center gap-2">
                <InputText
                  v-model="item.key"
                  placeholder="Tên biến (VD: GITLAB_TOKEN)"
                  class="flex-1 !text-xs !py-1.5 !px-2 font-mono !rounded"
                />
                <InputText
                  v-model="item.label"
                  placeholder="Nhãn (VD: GitLab Access Token)"
                  class="flex-1 !text-xs !py-1.5 !px-2 !rounded"
                />
                <button
                  type="button"
                  class="w-6 h-6 rounded flex items-center justify-center text-rose-500 hover:bg-rose-500/10 cursor-pointer"
                  title="Xóa biến này"
                  @click="removeGitCustomEnv(idx)"
                >
                  <i class="pi pi-trash text-xs"></i>
                </button>
              </div>
              <div class="flex items-center gap-2">
                <InputText
                  v-model="item.default"
                  placeholder="Giá trị mặc định"
                  class="flex-1 !text-xs !py-1.5 !px-2 !rounded"
                />
                <select
                  v-model="item.type"
                  class="text-xs py-1 px-2 rounded border border-neutral-300 dark:border-[#383838] bg-white dark:bg-[#1e1e1e] text-slate-700 dark:text-neutral-200"
                >
                  <option value="text">Văn bản</option>
                  <option value="password">Mật khẩu</option>
                </select>
                <label class="flex items-center gap-1 text-[11px] cursor-pointer shrink-0">
                  <input type="checkbox" v-model="item.required" class="rounded accent-emerald-500" />
                  <span>Bắt buộc</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2 w-full pt-2">
          <Button
            label="Hủy"
            text
            size="small"
            class="!text-xs"
            :disabled="isGitImporting"
            @click="pluginStore.showGitImportModal = false"
          />
          <Button
            :label="isGitImporting ? 'Đang Import...' : 'Import & Xuất Bản'"
            :icon="isGitImporting ? 'pi pi-spin pi-spinner' : 'pi pi-check'"
            size="small"
            class="!text-xs !bg-[#24292F] hover:!bg-[#1b1f23] !text-white !font-semibold !rounded-lg !py-1.5 !px-4"
            :disabled="!gitRepoUrl.trim() || isGitImporting"
            @click="handleGitImport"
          />
        </div>
      </template>
    </Dialog>

    <!-- Upload MCP Code Dialog -->
    <Dialog
      v-model:visible="pluginStore.showUploadModal"
      modal
      header="Upload MCP Script hoặc Package ZIP"
      :style="{ width: '560px', maxWidth: '95vw' }"
      class="!rounded-2xl overflow-hidden shadow-2xl !bg-white dark:!bg-[#1e1e1e] !text-slate-800 dark:!text-[#ececec]"
    >
      <div class="space-y-3.5 text-xs">
        <p class="text-neutral-500 dark:text-neutral-400">
          Kéo thả hoặc chọn file script (.py) đơn lẻ hoặc file nén (.zip). Hệ thống sẽ tự động quét hàm và xuất bản.
        </p>

        <div v-if="uploadError" class="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400">
          <i class="pi pi-exclamation-triangle mr-1"></i>
          <span>{{ uploadError }}</span>
        </div>

        <div>
          <label class="block font-semibold mb-1">Chọn Tệp (.py / .zip) <span class="text-rose-500">*</span></label>
          <input
            type="file"
            accept=".py,.zip"
            class="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-500/10 file:text-emerald-600 hover:file:bg-emerald-500/20 cursor-pointer"
            @change="onUploadFileChange"
          />
        </div>

        <div>
          <label class="block font-semibold mb-1">Tên Hiển Thị (Tùy chọn)</label>
          <InputText
            v-model="uploadName"
            class="w-full !text-xs !py-2 !px-3 !rounded-lg"
            placeholder="VD: Custom Script Tool"
          />
        </div>

        <div>
          <label class="block font-semibold mb-1">Mô Tả (Tùy chọn)</label>
          <InputText
            v-model="uploadDesc"
            class="w-full !text-xs !py-2 !px-3 !rounded-lg"
            placeholder="Mô tả công cụ..."
          />
        </div>

        <!-- Khai báo / Bổ sung Biến Môi Trường -->
        <div class="border-t border-[#e5e5e5] dark:border-[#2e2e2e] pt-3">
          <div class="flex items-center justify-between mb-2">
            <div>
              <span class="font-semibold text-xs text-slate-800 dark:text-neutral-200">Khai báo Biến Môi Trường (Tùy chọn)</span>
              <span class="text-[11px] text-neutral-400 block">Thêm hoặc ghi đè nhãn/loại biến (API Key, URL, Secret...)</span>
            </div>
            <button
              type="button"
              class="text-[11px] px-2.5 py-1 rounded-md bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-medium transition cursor-pointer flex items-center gap-1 shrink-0"
              @click="addUploadCustomEnv"
            >
              <i class="pi pi-plus text-[10px]"></i>
              <span>Thêm biến</span>
            </button>
          </div>

          <div v-if="uploadCustomEnvs.length === 0" class="p-2.5 rounded-lg border border-dashed border-neutral-200 dark:border-[#333] text-center text-[11px] text-neutral-400">
            Hệ thống sẽ tự động quét biến qua AST. Bấm <b>"+ Thêm biến"</b> nếu muốn bổ sung hoặc chỉ định nhãn/mật khẩu riêng.
          </div>

          <div v-else class="space-y-2 max-h-48 overflow-y-auto pr-1">
            <div
              v-for="(item, idx) in uploadCustomEnvs"
              :key="idx"
              class="p-2 rounded-lg bg-neutral-50 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] space-y-1.5"
            >
              <div class="flex items-center gap-2">
                <InputText
                  v-model="item.key"
                  placeholder="Tên biến (VD: DATABASE_URL)"
                  class="flex-1 !text-xs !py-1.5 !px-2 font-mono !rounded"
                />
                <InputText
                  v-model="item.label"
                  placeholder="Nhãn (VD: Kết Nối Cơ Sở Dữ Liệu)"
                  class="flex-1 !text-xs !py-1.5 !px-2 !rounded"
                />
                <button
                  type="button"
                  class="w-6 h-6 rounded flex items-center justify-center text-rose-500 hover:bg-rose-500/10 cursor-pointer"
                  title="Xóa biến này"
                  @click="removeUploadCustomEnv(idx)"
                >
                  <i class="pi pi-trash text-xs"></i>
                </button>
              </div>
              <div class="flex items-center gap-2">
                <InputText
                  v-model="item.default"
                  placeholder="Giá trị mặc định"
                  class="flex-1 !text-xs !py-1.5 !px-2 !rounded"
                />
                <select
                  v-model="item.type"
                  class="text-xs py-1 px-2 rounded border border-neutral-300 dark:border-[#383838] bg-white dark:bg-[#1e1e1e] text-slate-700 dark:text-neutral-200"
                >
                  <option value="text">Văn bản</option>
                  <option value="password">Mật khẩu</option>
                </select>
                <label class="flex items-center gap-1 text-[11px] cursor-pointer shrink-0">
                  <input type="checkbox" v-model="item.required" class="rounded accent-emerald-500" />
                  <span>Bắt buộc</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2 w-full pt-2">
          <Button
            label="Hủy"
            text
            size="small"
            class="!text-xs"
            :disabled="isUploading"
            @click="pluginStore.showUploadModal = false"
          />
          <Button
            :label="isUploading ? 'Đang Xử Lý...' : 'Upload & Xuất Bản'"
            :icon="isUploading ? 'pi pi-spin pi-spinner' : 'pi pi-upload'"
            size="small"
            class="!text-xs !bg-[#10A37F] hover:!bg-[#0e8f6f] !text-white !font-semibold !rounded-lg !py-1.5 !px-4"
            :disabled="!uploadFile || isUploading"
            @click="handleUploadSubmit"
          />
        </div>
      </template>
    </Dialog>

    <!-- Environment Variables Config Dialog (Install & Edit) -->
    <Dialog
      v-model:visible="showEnvConfigModal"
      modal
      :header="(isEditingInstalledConfig ? 'Chỉnh sửa cấu hình MCP: ' : 'Cấu hình môi trường: ') + (pendingMcpPlugin?.name || '')"
      :style="{ width: '500px' }"
      class="!rounded-2xl overflow-hidden shadow-2xl !bg-white dark:!bg-[#1e1e1e] !text-slate-800 dark:!text-[#ececec]"
    >
      <div v-if="pendingMcpPlugin" class="space-y-3.5 text-xs">
        <p class="text-neutral-500 dark:text-neutral-400">
          {{ isEditingInstalledConfig
              ? 'Cập nhật lại các biến môi trường cho MCP server này. Sau khi lưu, thông tin sẽ được cập nhật trực tiếp vào file .env và áp dụng tức thì:'
              : 'MCP này yêu cầu các biến môi trường để hoạt động. Vui lòng xác nhận thông tin bên dưới:' }}
        </p>

        <div v-for="req in pendingMcpPlugin.envRequirements" :key="req.key">
          <label class="block font-semibold mb-1">
            {{ req.label || req.key }}
            <span v-if="req.required" class="text-rose-500">*</span>
          </label>
          <InputText
            v-model="envConfigValues[req.key]"
            :type="req.key.toLowerCase().includes('token') || req.key.toLowerCase().includes('key') || req.key.toLowerCase().includes('pass') ? 'password' : 'text'"
            class="w-full !text-xs !py-2 !px-3 font-mono !rounded-lg"
            :placeholder="req.default || req.key"
          />
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2 w-full pt-2">
          <Button
            label="Hủy"
            text
            size="small"
            class="!text-xs"
            @click="showEnvConfigModal = false"
          />
          <Button
            :label="isEditingInstalledConfig ? 'Lưu Thay Đổi' : 'Lưu & Kích Hoạt MCP'"
            icon="pi pi-check"
            size="small"
            class="!text-xs !bg-[#10A37F] hover:!bg-[#0e8f6f] !text-white !font-semibold !rounded-lg !py-1.5 !px-4"
            @click="confirmEnvConfigInstall"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>
