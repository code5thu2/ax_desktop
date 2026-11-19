<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { usePluginStore } from '../stores/pluginStore'
import { useI18n } from '@/i18n'
import type { PluginItem } from '../types/plugin'

import McpStudioHeader from './McpStudioHeader.vue'
import McpServerList from './McpServerList.vue'
import McpServerDetail from './McpServerDetail.vue'
import McpGitImportModal from './modals/McpGitImportModal.vue'
import McpUploadModal from './modals/McpUploadModal.vue'
import McpEnvConfigModal from './modals/McpEnvConfigModal.vue'

interface Props {
  appendTo?: string | HTMLElement
  showList?: boolean
  embedded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  appendTo: 'body',
  showList: true,
  embedded: false,
})

const pluginStore = usePluginStore()
const { t } = useI18n()
const toast = useToast()
const confirm = useConfirm()

// MCP Env Configuration Modal State
const showEnvConfigModal = ref(false)
const pendingMcpPlugin = ref<PluginItem | null>(null)
const isEditingInstalledConfig = ref(false)
const envConfigValues = ref<Record<string, string>>({})

onMounted(() => {
  pluginStore.fetchCatalogFromServer()
})

function triggerToast(msg: string) {
  toast.add({
    severity: 'success',
    summary: 'MCP Protocol Studio',
    detail: msg,
    life: 3000,
  })
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
    triggerToast(t('mcpStudio.configUpdatedToast', { name: mcp.name }))
  } else {
    executeInstall(mcp.id, mcp.name)
  }
}

function executeInstall(id: string, name: string) {
  pluginStore.installPlugin(id)
  triggerToast(t('mcpStudio.installSuccessToast', { name }))
}

function handleUninstall(id: string, name: string) {
  confirm.require({
    message: t('mcpStudio.confirmUninstallMsg', { name }),
    header: t('mcpStudio.uninstallBtn'),
    acceptClass: 'p-button-danger',
    acceptLabel: t('mcpStudio.uninstallBtn'),
    rejectLabel: t('common.cancel'),
    accept: () => {
      pluginStore.uninstallPlugin(id)
      triggerToast(t('mcpStudio.toastUninstalled', { name }))
    },
  })
}

function onGitSuccess(name: string, count: number) {
  triggerToast(t('mcpStudio.gitImportSuccessToast', { name, count }))
}

function onUploadSuccess(name: string, count: number) {
  triggerToast(t('mcpStudio.uploadSuccessToast', { name, count }))
}
</script>

<template>
  <div class="h-full w-full flex flex-col min-h-0 bg-white dark:bg-[#1E1F22] text-slate-900 dark:text-[#DFE1E5] select-none font-sans overflow-hidden">
    <!-- Sub-navigation Header with Tabs & Controls -->
    <McpStudioHeader
      @import-git="pluginStore.showGitImportModal = true"
      @upload-zip="pluginStore.showUploadModal = true"
    />

    <!-- Main Content: Split Pane -->
    <div class="flex-1 flex min-h-0 overflow-hidden">
      <!-- LEFT PANE: MCP Servers List -->
      <McpServerList
        :show-list="props.showList"
        @install="handleInstall"
      />

      <!-- RIGHT PANE: MCP Server Detail Panel -->
      <McpServerDetail
        @install="handleInstall"
        @uninstall="handleUninstall"
        @open-config="openConfigModal"
      />
    </div>

    <!-- Modals -->
    <McpGitImportModal @success="onGitSuccess" />
    <McpUploadModal @success="onUploadSuccess" />
    <McpEnvConfigModal
      v-model:visible="showEnvConfigModal"
      :plugin="pendingMcpPlugin"
      :is-editing="isEditingInstalledConfig"
      :env-values="envConfigValues"
      @confirm="confirmEnvConfigInstall"
    />
  </div>
</template>
