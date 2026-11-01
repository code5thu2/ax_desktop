<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Tag from 'primevue/tag'
import InputSwitch from 'primevue/inputswitch'
import { usePluginStore } from '../stores/pluginStore'
import { useI18n } from '@/i18n'
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
const { t } = useI18n()
const activeDetailTab = ref<'overview' | 'tools' | 'config' | 'changelog'>('overview')
const showInstallSuccessToast = ref(false)
const toastMessage = ref('')
const isEditingInstalledConfig = ref(false)

let toastTimer: ReturnType<typeof setTimeout> | null = null

function triggerToast(msg: string) {
  toastMessage.value = msg
  showInstallSuccessToast.value = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    showInstallSuccessToast.value = false
    toastTimer = null
  }, 2500)
}

onUnmounted(() => {
  if (toastTimer) clearTimeout(toastTimer)
})

// Git Import Modal State
const gitRepoUrl = ref('')
const gitBranch = ref('main')
const gitToken = ref('')
const gitName = ref('')
const gitDesc = ref('')
const isGitImporting = ref(false)
const gitImportError = ref('')

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
    const res = await pluginStore.importFromGit(
      gitRepoUrl.value.trim(),
      gitBranch.value.trim() || 'main',
      gitToken.value.trim() || undefined,
      gitName.value.trim() || undefined,
      gitDesc.value.trim() || undefined
    )
    pluginStore.showGitImportModal = false
    gitRepoUrl.value = ''
    gitToken.value = ''
    gitName.value = ''
    gitDesc.value = ''
    triggerToast(`Đã nhập và xuất bản thành công MCP: ${res.name} (${res.tools_count} tools)`)
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
    const res = await pluginStore.uploadCustomMCP(
      uploadFile.value,
      uploadName.value.trim() || undefined,
      uploadDesc.value.trim() || undefined
    )
    pluginStore.showUploadModal = false
    uploadFile.value = null
    uploadName.value = ''
    uploadDesc.value = ''
    triggerToast(`Đã upload và xuất bản thành công: ${res.name} (${res.tools_count} tools)`)
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
    plugin.envRequirements.forEach((req) => {
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
  plugin.envRequirements?.forEach((req) => {
    envConfigValues.value[req.key] =
      plugin.configuredEnv && plugin.configuredEnv[req.key] !== undefined
        ? plugin.configuredEnv[req.key]
        : req.default || ''
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
    triggerToast(`Đã cập nhật cấu hình cho ${mcp.name}`)
  } else {
    executeInstall(mcp.id, mcp.name)
  }
}

function executeInstall(id: string, name: string) {
  pluginStore.installPlugin(id)
  triggerToast(`Đã cài đặt thành công MCP Server: ${name}`)
}

function handleUninstall(id: string, name: string) {
  pluginStore.uninstallPlugin(id)
  triggerToast(`Đã gỡ cài đặt: ${name}`)
}
</script>

<template>
  <div class="h-full min-h-0 flex bg-white dark:bg-[#121214] text-slate-900 dark:text-[#ececec] select-none font-sans overflow-hidden">
    <!-- Notification Toast Banner -->
    <div
      v-if="showInstallSuccessToast"
      class="fixed top-16 right-6 z-50 px-4 py-2 bg-emerald-500 text-white text-xs rounded-xl shadow-lg flex items-center gap-2 animate-bounce"
    >
      <i class="pi pi-check-circle text-sm"></i>
      <span class="font-bold">{{ toastMessage }}</span>
      <button type="button" class="ml-2 cursor-pointer" @click="showInstallSuccessToast = false">
        <i class="pi pi-times text-xs"></i>
      </button>
    </div>

    <!-- Main Content: Split Pane matching Skill Marketplace exactly -->
    <div class="flex-1 flex min-h-0 overflow-hidden">
      <!-- LEFT PANE: MCP Servers List (w-80 md:w-96 lg:w-[420px]) -->
      <div
        v-show="props.showList"
        data-testid="plugin-list-pane"
        class="w-80 md:w-96 lg:w-[420px] border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/40 flex flex-col p-4 space-y-4 overflow-hidden flex-shrink-0"
      >
        <!-- Search Bar -->
        <div class="relative">
          <i class="pi pi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
          <InputText
            v-model="pluginStore.searchQuery"
            data-testid="plugin-search-input"
            :placeholder="t('mcpStudio.searchPlaceholder')"
            class="w-full !pl-9 !py-2 !text-xs !rounded-xl"
          />
          <button
            v-if="pluginStore.searchQuery"
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs cursor-pointer"
            @click="pluginStore.searchQuery = ''"
          >
            <i class="pi pi-times"></i>
          </button>
        </div>

        <!-- 1. Tabs Segmented Control: Marketplace | Installed -->
        <div class="grid grid-cols-2 p-1 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 gap-1">
          <button
            type="button"
            data-testid="tab-marketplace"
            class="py-1.5 px-3 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
            :class="[
              pluginStore.activeTab === 'marketplace'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs'
                : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
            ]"
            @click="pluginStore.setActiveTab('marketplace')"
          >
            <i class="pi pi-compass text-xs text-emerald-500"></i>
            <span>{{ t('mcpStudio.tabMarketplace') }}</span>
          </button>

          <button
            type="button"
            data-testid="tab-installed"
            class="py-1.5 px-3 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
            :class="[
              pluginStore.activeTab === 'installed'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs'
                : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
            ]"
            @click="pluginStore.setActiveTab('installed')"
          >
            <i class="pi pi-check-circle text-xs text-teal-400"></i>
            <span>{{ t('mcpStudio.tabInstalled') }}</span>
            <Tag :value="String(pluginStore.installedCount)" severity="success" class="!text-[10px] !py-0 !px-1.5 !font-mono" />
          </button>
        </div>

        <!-- 2. Category Filter Pills -->
        <div class="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
          <button
            type="button"
            data-testid="filter-all"
            class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
            :class="pluginStore.filterCategory === 'all' ? 'bg-emerald-500 text-white shadow-xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
            @click="pluginStore.setFilterCategory('all')"
          >
            {{ t('mcpStudio.catAll') }}
          </button>
          <button
            type="button"
            data-testid="filter-inhouse"
            class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
            :class="pluginStore.filterCategory === 'In-House Tools' ? 'bg-emerald-500 text-white shadow-xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
            @click="pluginStore.setFilterCategory('In-House Tools')"
          >
            {{ t('mcpStudio.catInHouse') }}
          </button>
          <button
            type="button"
            data-testid="filter-custom"
            class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
            :class="pluginStore.filterCategory === 'Custom Tools' ? 'bg-emerald-500 text-white shadow-xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
            @click="pluginStore.setFilterCategory('Custom Tools')"
          >
            {{ t('mcpStudio.catCustom') }}
          </button>
          <button
            type="button"
            data-testid="filter-git"
            class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
            :class="pluginStore.filterCategory === 'Git Tools' ? 'bg-emerald-500 text-white shadow-xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
            @click="pluginStore.setFilterCategory('Git Tools')"
          >
            {{ t('mcpStudio.catGit') }}
          </button>
        </div>

        <!-- 3. Add Server Action Toolbar -->
        <div class="flex items-center gap-2">
          <Button
            type="button"
            icon="pi pi-github"
            :label="t('mcpStudio.btnImportGit')"
            variant="outlined"
            class="flex-1 !py-1 !px-2 !text-[11px] !font-bold !rounded-xl cursor-pointer"
            @click="pluginStore.showGitImportModal = true"
          />
          <Button
            type="button"
            icon="pi pi-upload"
            :label="t('mcpStudio.btnUploadZip')"
            variant="outlined"
            class="flex-1 !py-1 !px-2 !text-[11px] !font-bold !rounded-xl cursor-pointer"
            @click="pluginStore.showUploadModal = true"
          />
        </div>

        <!-- 4. MCP Server Cards List -->
        <div class="flex-1 overflow-y-auto space-y-2.5 pr-1">
          <div
            v-if="pluginStore.filteredPlugins.length === 0"
            class="text-center py-12 text-xs text-slate-400"
          >
            <i class="pi pi-inbox text-3xl mb-2 text-slate-300 dark:text-slate-700 block"></i>
            <span>{{ t('mcpStudio.noServersFound') }}</span>
          </div>

          <div
            v-for="plugin in pluginStore.filteredPlugins"
            :key="plugin.id"
            :data-testid="`plugin-item-${plugin.id}`"
            class="p-3.5 rounded-2xl border transition-all cursor-pointer flex flex-col gap-2.5"
            :class="pluginStore.selectedPlugin?.id === plugin.id ? 'border-emerald-500 bg-emerald-50/40 dark:bg-emerald-950/20 shadow-xs' : 'border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900/60'"
            @click="pluginStore.selectPlugin(plugin.id)"
          >
            <!-- Card top -->
            <div class="flex items-start justify-between gap-2.5">
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-sm shadow-xs flex-shrink-0">
                  <i :class="plugin.icon || 'pi pi-share-alt'"></i>
                </div>
                <div class="min-w-0">
                  <h3 class="text-xs font-bold text-slate-900 dark:text-white truncate">
                    {{ plugin.name }}
                  </h3>
                  <div class="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                    <span class="truncate">{{ plugin.vendor || 'AIPRO Community' }}</span>
                    <span>&bull;</span>
                    <span>v{{ plugin.version }}</span>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-1.5">
                <Tag
                  :value="plugin.category || 'MCP'"
                  severity="info"
                  class="!text-[10px] !py-0.5 !px-1.5"
                />
              </div>
            </div>

            <!-- Summary preview -->
            <p class="text-[11px] text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed">
              {{ plugin.summary || plugin.description }}
            </p>

            <!-- Card footer -->
            <div class="flex items-center justify-between pt-1 text-[11px] text-slate-400 border-t border-slate-100 dark:border-slate-800/80">
              <div class="flex items-center gap-2">
                <span class="flex items-center gap-1 text-amber-500 font-bold">
                  <i class="pi pi-star-fill text-[10px]"></i>
                  {{ plugin.rating || 5.0 }}
                </span>
                <span>&bull;</span>
                <span>{{ plugin.downloads || '100+' }}</span>
              </div>

              <div @click.stop>
                <template v-if="pluginStore.activeTab === 'marketplace'">
                  <Button
                    v-if="!plugin.installed"
                    type="button"
                    :data-testid="`install-btn-${plugin.id}`"
                    :label="t('mcpStudio.installBtn')"
                    icon="pi pi-download"
                    class="!py-1 !px-2.5 !text-[11px] !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-xs cursor-pointer !rounded-lg"
                    @click="handleInstall(plugin.id, plugin.name)"
                  />
                  <span v-else class="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                    <i class="pi pi-check text-[10px]"></i> {{ t('portal.readyBadge') }}
                  </span>
                </template>
                <template v-else>
                  <InputSwitch
                    :modelValue="plugin.enabled"
                    @update:modelValue="() => pluginStore.togglePlugin(plugin.id)"
                  />
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT PANE: MCP Server Detail Panel (Matching SkillDetailPanel.vue exactly) -->
      <div v-if="pluginStore.selectedPlugin" class="h-full flex-1 flex flex-col p-6 overflow-hidden bg-slate-50/50 dark:bg-slate-950/40">
        <!-- Detail Header Card -->
        <div class="p-5 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 shadow-sm flex items-start justify-between gap-4">
          <div class="flex items-start gap-4 min-w-0">
            <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-2xl shadow-md shadow-emerald-500/20 flex-shrink-0">
              <i :class="pluginStore.selectedPlugin.icon || 'pi pi-share-alt'"></i>
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h1 class="text-lg font-extrabold text-slate-900 dark:text-white tracking-tight truncate">
                  {{ pluginStore.selectedPlugin.name }}
                </h1>
                <Tag value="APPROVED" severity="success" class="!text-[10px] !py-0.5 !px-2 !font-bold" />
                <Tag :value="pluginStore.selectedPlugin.category || 'MCP PROTOCOL'" severity="info" class="!text-[10px] !py-0.5 !px-2 !font-bold" />
              </div>

              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2">
                <span>{{ t('portal.authorLabel') }}: <strong class="text-slate-700 dark:text-slate-300">{{ pluginStore.selectedPlugin.vendor }}</strong></span>
                <span>&bull;</span>
                <span>{{ t('portal.versionLabel') }}: <strong class="text-slate-700 dark:text-slate-300">v{{ pluginStore.selectedPlugin.version }}</strong></span>
              </p>

              <div class="flex items-center gap-3 mt-2 text-xs text-slate-500">
                <span class="flex items-center gap-1 text-amber-500 font-bold">
                  <i class="pi pi-star-fill text-xs"></i>
                  {{ pluginStore.selectedPlugin.rating }}
                </span>
                <span>&bull;</span>
                <span>{{ pluginStore.selectedPlugin.downloads }}</span>
              </div>
            </div>
          </div>

          <!-- Top-right Action Buttons -->
          <div class="flex items-center gap-3 flex-shrink-0">
            <template v-if="!pluginStore.selectedPlugin.installed">
              <Button
                type="button"
                data-testid="detail-install-btn"
                :label="t('mcpStudio.installBtn')"
                icon="pi pi-download"
                class="!py-2.5 !px-4 !text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/25 cursor-pointer !rounded-xl"
                @click="handleInstall(pluginStore.selectedPlugin.id, pluginStore.selectedPlugin.name)"
              />
            </template>
            <template v-else>
              <div class="flex items-center gap-2.5 bg-slate-100 dark:bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
                <span class="text-xs font-semibold text-slate-600 dark:text-slate-300">
                  {{ pluginStore.selectedPlugin.enabled ? t('portal.activeStatus') : t('portal.disabledStatus') }}
                </span>
                <InputSwitch
                  :modelValue="pluginStore.selectedPlugin.enabled"
                  @update:modelValue="() => pluginStore.selectedPlugin && pluginStore.togglePlugin(pluginStore.selectedPlugin.id)"
                />
              </div>

              <!-- Configure Button -->
              <Button
                v-if="pluginStore.selectedPlugin.envRequirements?.length"
                type="button"
                data-testid="detail-config-btn"
                icon="pi pi-sliders-h"
                :label="t('mcpStudio.configureBtn')"
                variant="outlined"
                class="!py-2.5 !px-3 !text-xs !rounded-xl cursor-pointer"
                @click="openConfigModal(pluginStore.selectedPlugin)"
              />

              <!-- Uninstall Button -->
              <Button
                type="button"
                data-testid="detail-uninstall-btn"
                icon="pi pi-trash"
                :label="t('mcpStudio.uninstallBtn')"
                variant="outlined"
                severity="danger"
                class="!py-2.5 !px-3 !text-xs !rounded-xl cursor-pointer"
                @click="handleUninstall(pluginStore.selectedPlugin.id, pluginStore.selectedPlugin.name)"
              />
            </template>
          </div>
        </div>

        <!-- Scope Card (If installed) -->
        <div
          v-if="pluginStore.selectedPlugin.installed"
          class="p-3.5 rounded-2xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-800/60 flex items-center justify-between text-xs mt-4"
        >
          <div class="flex items-center gap-2.5">
            <i class="pi pi-info-circle text-emerald-600 dark:text-emerald-400 text-sm"></i>
            <div>
              <span class="font-bold text-slate-900 dark:text-white">
                Thư mục Sandbox MCP: <code class="font-mono bg-white dark:bg-slate-900 px-1 py-0.5 rounded border border-slate-200 dark:border-slate-800">{{ pluginStore.selectedPlugin.installPath || '~/.aipro/mcp' }}</code>
              </span>
              <span class="block text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                Giao tiếp qua Model Context Protocol tiêu chuẩn (JSON-RPC 2.0).
              </span>
            </div>
          </div>
          <Tag value="MCP SERVER" severity="success" class="!text-[10px] !font-bold" />
        </div>

        <!-- Navigation Tabs inside Detail -->
        <div class="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2 mt-4">
          <button
            type="button"
            data-testid="subtab-overview"
            class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
            :class="activeDetailTab === 'overview' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
            @click="activeDetailTab = 'overview'"
          >
            <i class="pi pi-file-edit text-xs"></i>
            <span>{{ t('mcpStudio.tabOverview') }}</span>
          </button>

          <button
            type="button"
            data-testid="subtab-tools"
            class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
            :class="activeDetailTab === 'tools' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
            @click="activeDetailTab = 'tools'"
          >
            <i class="pi pi-box text-xs"></i>
            <span>{{ t('mcpStudio.tabTools', { count: pluginStore.selectedPlugin.tools?.length || 0 }) }}</span>
          </button>

          <button
            v-if="pluginStore.selectedPlugin.envRequirements?.length"
            type="button"
            data-testid="subtab-config"
            class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
            :class="activeDetailTab === 'config' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
            @click="activeDetailTab = 'config'"
          >
            <i class="pi pi-sliders-h text-xs text-amber-500"></i>
            <span>{{ t('mcpStudio.tabEnv') }}</span>
          </button>

          <button
            type="button"
            data-testid="subtab-changelog"
            class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
            :class="activeDetailTab === 'changelog' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
            @click="activeDetailTab = 'changelog'"
          >
            <i class="pi pi-history text-xs"></i>
            <span>{{ t('mcpStudio.tabChangelog') }}</span>
          </button>
        </div>

        <!-- Detail Sub-Tab Content Area -->
        <div class="flex-1 overflow-y-auto bg-white dark:bg-slate-900/60 rounded-3xl border border-slate-200/90 dark:border-slate-800 p-6 min-h-0 mt-4">
          <!-- 1. OVERVIEW TAB -->
          <div v-if="activeDetailTab === 'overview'" class="space-y-4">
            <div class="prose dark:prose-invert max-w-none text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
              <h3 class="text-sm font-bold text-slate-900 dark:text-white mb-2">Mô tả MCP Server</h3>
              <p>{{ pluginStore.selectedPlugin.description }}</p>

              <h3 class="text-sm font-bold text-slate-900 dark:text-white mt-4 mb-2">Tính năng nổi bật (Key Features)</h3>
              <div class="space-y-1.5">
                <div
                  v-for="(feat, idx) in pluginStore.selectedPlugin.features"
                  :key="idx"
                  class="flex items-start gap-2"
                >
                  <i class="pi pi-check text-emerald-500 text-xs mt-0.5 shrink-0"></i>
                  <span>{{ feat }}</span>
                </div>
              </div>

              <!-- Specifications Card -->
              <h3 class="text-sm font-bold text-slate-900 dark:text-white mt-4 mb-2">Thông số Kỹ thuật</h3>
              <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
                <div>
                  <span class="text-slate-400 block mb-0.5">Loại Extension</span>
                  <span class="font-bold text-slate-800 dark:text-white">{{ pluginStore.selectedPlugin.type }} Protocol</span>
                </div>
                <div>
                  <span class="text-slate-400 block mb-0.5">Giao thức thực thi</span>
                  <span class="font-bold text-slate-800 dark:text-white">JSON-RPC 2.0 (Stdio / SSE)</span>
                </div>
                <div>
                  <span class="text-slate-400 block mb-0.5">Phiên bản</span>
                  <span class="font-mono text-slate-800 dark:text-white">v{{ pluginStore.selectedPlugin.version }}</span>
                </div>
                <div>
                  <span class="text-slate-400 block mb-0.5">Trạng thái</span>
                  <span class="font-bold text-emerald-600 dark:text-emerald-400">
                    {{ pluginStore.selectedPlugin.installed ? (pluginStore.selectedPlugin.enabled ? 'Đã kích hoạt' : 'Đã vô hiệu hóa') : 'Chưa cài đặt' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 2. TOOLS TAB -->
          <div v-else-if="activeDetailTab === 'tools'" class="space-y-3">
            <div class="text-xs text-slate-500 dark:text-slate-400 mb-2">
              MCP Server này cung cấp <strong>{{ pluginStore.selectedPlugin.tools?.length || 0 }}</strong> công cụ có thể gọi trực tiếp:
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div
                v-for="tool in pluginStore.selectedPlugin.tools"
                :key="tool.name"
                class="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 flex flex-col justify-between"
              >
                <div>
                  <div class="flex items-center justify-between gap-2 mb-1.5">
                    <div class="flex items-center gap-2">
                      <span class="font-mono font-bold text-xs text-emerald-600 dark:text-emerald-400">
                        {{ tool.name }}
                      </span>
                      <span class="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-mono font-bold">
                        tool
                      </span>
                    </div>
                    <div class="flex items-center gap-1.5">
                      <button
                        type="button"
                        class="px-2 py-0.5 rounded-lg text-[10px] font-bold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 cursor-pointer"
                        @click="toggleToolArgs(tool.name)"
                      >
                        <i class="pi pi-code text-[10px]"></i>
                        <span class="ml-1">JSON</span>
                      </button>
                      <button
                        type="button"
                        class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-emerald-500 hover:bg-emerald-600 text-white cursor-pointer flex items-center gap-1"
                        :disabled="testingToolName === tool.name"
                        @click="runToolTest(tool.name)"
                      >
                        <i v-if="testingToolName === tool.name" class="pi pi-spin pi-spinner text-[9px]"></i>
                        <i v-else class="pi pi-play text-[9px]"></i>
                        <span>{{ testingToolName === tool.name ? t('mcpStudio.testRunning') : t('mcpStudio.runTestBtn') }}</span>
                      </button>
                    </div>
                  </div>
                  <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                    {{ tool.description }}
                  </p>

                  <!-- Parameters list badge -->
                  <div
                    v-if="tool.parameters && (Array.isArray(tool.parameters) ? tool.parameters.length : Object.keys(tool.parameters?.properties || {}).length)"
                    class="mt-2 flex flex-wrap items-center gap-1.5"
                  >
                    <span class="text-[10px] text-slate-400">Tham số:</span>
                    <span
                      v-for="p in (Array.isArray(tool.parameters) ? tool.parameters : Object.keys(tool.parameters?.properties || {}))"
                      :key="p"
                      class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300"
                    >
                      {{ p }}
                    </span>
                  </div>

                  <!-- Optional JSON Input for Tool Testing -->
                  <div v-if="showToolArgsInput[tool.name]" class="mt-2.5 space-y-1">
                    <span class="text-[10px] text-slate-400">Tham số JSON:</span>
                    <input
                      v-model="toolInputArgs[tool.name]"
                      type="text"
                      :placeholder="t('mcpStudio.paramsPlaceholder')"
                      class="w-full text-xs font-mono py-1.5 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200"
                      @keydown.enter="runToolTest(tool.name)"
                    />
                  </div>
                </div>

                <!-- Live Test Call Output -->
                <div v-if="toolOutputs[tool.name]" class="mt-3 pt-2 border-t border-slate-200/80 dark:border-slate-800">
                  <div class="text-[10px] font-mono text-slate-400 mb-1 flex items-center justify-between">
                    <span>{{ t('mcpStudio.testResult') }}</span>
                    <button type="button" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer" @click="delete toolOutputs[tool.name]">
                      <i class="pi pi-times text-[10px]"></i>
                    </button>
                  </div>
                  <pre class="p-3 rounded-xl bg-slate-950 text-emerald-400 text-xs font-mono overflow-x-auto max-h-40 border border-slate-800">{{ JSON.stringify(toolOutputs[tool.name], null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. CONFIGURATION (ENV) TAB -->
          <div v-else-if="activeDetailTab === 'config'" class="space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
              <div>
                <h4 class="font-bold text-slate-800 dark:text-slate-100 text-xs flex items-center gap-1.5">
                  <i class="pi pi-sliders-h text-amber-500"></i>
                  <span>{{ t('mcpStudio.tabEnv') }}</span>
                </h4>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  .env Sandbox • {{ pluginStore.selectedPlugin.name }}
                </p>
              </div>
              <Button
                type="button"
                data-testid="btn-open-config-modal"
                icon="pi pi-file-edit"
                :label="t('mcpStudio.configureBtn')"
                class="!py-2 !px-3 !text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-sm cursor-pointer !rounded-xl"
                @click="openConfigModal(pluginStore.selectedPlugin)"
              />
            </div>

            <!-- Current Values Card List -->
            <div class="grid grid-cols-1 gap-2.5">
              <div
                v-for="req in pluginStore.selectedPlugin.envRequirements"
                :key="req.key"
                class="p-3.5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 flex items-center justify-between"
              >
                <div class="space-y-0.5 min-w-0 pr-4">
                  <div class="flex items-center gap-2">
                    <span class="font-mono font-bold text-xs text-emerald-600 dark:text-emerald-400">
                      {{ req.key }}
                    </span>
                    <span v-if="req.required" class="text-[9px] px-1.5 py-0.2 rounded bg-rose-500/10 text-rose-500 font-mono font-bold">
                      required
                    </span>
                  </div>
                  <div class="text-xs text-slate-500 dark:text-slate-400">
                    {{ req.label || req.key }}
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <span class="font-mono text-xs px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200">
                    {{ (pluginStore.selectedPlugin.configuredEnv && pluginStore.selectedPlugin.configuredEnv[req.key] !== undefined)
                        ? (req.key.toLowerCase().includes('pass') || req.key.toLowerCase().includes('token') || req.key.toLowerCase().includes('secret')
                            ? '••••••••'
                            : pluginStore.selectedPlugin.configuredEnv[req.key] || '(chưa đặt)')
                        : (req.default || '(mặc định)') }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 4. CHANGELOG TAB -->
          <div v-else-if="activeDetailTab === 'changelog'" class="space-y-3">
            <div class="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
              <div class="flex items-center justify-between mb-2">
                <span class="font-bold text-slate-800 dark:text-white text-xs">Nhật ký cập nhật</span>
                <span class="font-mono text-slate-400 text-xs">v{{ pluginStore.selectedPlugin.version }}</span>
              </div>
              <p class="text-xs text-slate-600 dark:text-slate-300 font-mono leading-relaxed">
                {{ pluginStore.selectedPlugin.changeNotes || 'Tối ưu hóa hiệu năng và kết nối Stdio JSON-RPC.' }}
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
      :header="t('mcpStudio.gitModalTitle')"
      :style="{ width: '540px' }"
      class="p-dialog-custom"
    >
      <div class="space-y-3.5 text-xs py-2">
        <p class="text-slate-500 dark:text-slate-400 leading-relaxed">
          {{ t('mcpStudio.gitModalTitle') }}
        </p>

        <div v-if="gitImportError" class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-rose-700 dark:text-rose-300">
          <i class="pi pi-exclamation-triangle mr-1"></i>
          <span>{{ gitImportError }}</span>
        </div>

        <div>
          <label class="block font-bold mb-1 text-slate-700 dark:text-slate-300">Git Repository URL <span class="text-rose-500">*</span></label>
          <InputText
            v-model="gitRepoUrl"
            class="w-full !text-xs !py-2.5 !px-3 font-mono !rounded-xl"
            placeholder="https://github.com/my-org/my-mcp.git"
          />
        </div>

        <div class="grid grid-cols-2 gap-2.5">
          <div>
            <label class="block font-bold mb-1 text-slate-700 dark:text-slate-300">Nhánh (Branch) / Tag</label>
            <InputText
              v-model="gitBranch"
              class="w-full !text-xs !py-2.5 !px-3 font-mono !rounded-xl"
              placeholder="main"
            />
          </div>
          <div>
            <label class="block font-bold mb-1 text-slate-700 dark:text-slate-300">Tên Hiển Thị</label>
            <InputText
              v-model="gitName"
              class="w-full !text-xs !py-2.5 !px-3 !rounded-xl"
              placeholder="VD: Database Tools"
            />
          </div>
        </div>

        <div>
          <label class="block font-bold mb-1 text-slate-700 dark:text-slate-300">Token Xác Thực (Private Repo)</label>
          <InputText
            v-model="gitToken"
            type="password"
            class="w-full !text-xs !py-2.5 !px-3 font-mono !rounded-xl"
            placeholder="ghp_xxxx"
          />
        </div>

        <div>
          <label class="block font-bold mb-1 text-slate-700 dark:text-slate-300">Mô Tả Ngắn</label>
          <InputText
            v-model="gitDesc"
            class="w-full !text-xs !py-2.5 !px-3 !rounded-xl"
            placeholder="Mô tả công cụ..."
          />
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2 pt-2">
          <Button
            :label="t('common.cancel')"
            variant="text"
            class="!text-xs !rounded-xl cursor-pointer"
            :disabled="isGitImporting"
            @click="pluginStore.showGitImportModal = false"
          />
          <Button
            :label="isGitImporting ? t('mcpStudio.importing') : t('mcpStudio.submitImportBtn')"
            icon="pi pi-check"
            :loading="isGitImporting"
            class="!text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/20 cursor-pointer !rounded-xl"
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
      :header="t('mcpStudio.uploadModalTitle')"
      :style="{ width: '540px' }"
      class="p-dialog-custom"
    >
      <div class="space-y-3.5 text-xs py-2">
        <p class="text-slate-500 dark:text-slate-400 leading-relaxed">
          {{ t('mcpStudio.uploadModalTitle') }}
        </p>

        <div v-if="uploadError" class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-rose-700 dark:text-rose-300">
          <i class="pi pi-exclamation-triangle mr-1"></i>
          <span>{{ uploadError }}</span>
        </div>

        <div>
          <label class="block font-bold mb-1 text-slate-700 dark:text-slate-300">Chọn Tệp (.py / .zip) <span class="text-rose-500">*</span></label>
          <input
            type="file"
            accept=".py,.zip"
            class="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-500/10 file:text-emerald-600 hover:file:bg-emerald-500/20 cursor-pointer"
            @change="onUploadFileChange"
          />
        </div>

        <div>
          <label class="block font-bold mb-1 text-slate-700 dark:text-slate-300">Tên Hiển Thị</label>
          <InputText
            v-model="uploadName"
            class="w-full !text-xs !py-2.5 !px-3 !rounded-xl"
            placeholder="VD: Custom File Server"
          />
        </div>

        <div>
          <label class="block font-bold mb-1 text-slate-700 dark:text-slate-300">Mô Tả</label>
          <InputText
            v-model="uploadDesc"
            class="w-full !text-xs !py-2.5 !px-3 !rounded-xl"
            placeholder="Mô tả công cụ..."
          />
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2 pt-2">
          <Button
            :label="t('common.cancel')"
            variant="text"
            class="!text-xs !rounded-xl cursor-pointer"
            :disabled="isUploading"
            @click="pluginStore.showUploadModal = false"
          />
          <Button
            :label="isUploading ? t('mcpStudio.uploading') : t('mcpStudio.submitUploadBtn')"
            icon="pi pi-upload"
            :loading="isUploading"
            class="!text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/20 cursor-pointer !rounded-xl"
            :disabled="!uploadFile || isUploading"
            @click="handleUploadSubmit"
          />
        </div>
      </template>
    </Dialog>

    <!-- Environment Variables Config Dialog -->
    <Dialog
      v-model:visible="showEnvConfigModal"
      modal
      :header="t('mcpStudio.envModalTitle') + ': ' + (pendingMcpPlugin?.name || '')"
      :style="{ width: '500px' }"
      class="p-dialog-custom"
    >
      <div v-if="pendingMcpPlugin" class="space-y-3.5 text-xs py-2">
        <p class="text-slate-500 dark:text-slate-400 leading-relaxed">
          {{ isEditingInstalledConfig
              ? 'Cập nhật lại các biến môi trường cho MCP server này (.env):'
              : 'MCP này yêu cầu các biến môi trường để hoạt động. Vui lòng xác nhận:' }}
        </p>

        <div v-for="req in pendingMcpPlugin.envRequirements" :key="req.key">
          <label class="block font-bold mb-1 text-slate-700 dark:text-slate-300">
            {{ req.label || req.key }}
            <span v-if="req.required" class="text-rose-500">*</span>
          </label>
          <InputText
            v-model="envConfigValues[req.key]"
            :type="req.key.toLowerCase().includes('token') || req.key.toLowerCase().includes('key') || req.key.toLowerCase().includes('pass') ? 'password' : 'text'"
            class="w-full !text-xs !py-2.5 !px-3 font-mono !rounded-xl"
            :placeholder="req.default || req.key"
          />
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2 pt-2">
          <Button
            :label="t('common.cancel')"
            variant="text"
            class="!text-xs !rounded-xl cursor-pointer"
            @click="showEnvConfigModal = false"
          />
          <Button
            :label="t('mcpStudio.saveEnvBtn')"
            icon="pi pi-check"
            class="!text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/20 cursor-pointer !rounded-xl"
            @click="confirmEnvConfigInstall"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>
