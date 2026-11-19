<script setup lang="ts">
import { ref } from 'vue'
import Tag from 'primevue/tag'
import { usePluginStore } from '../stores/pluginStore'
import { useI18n } from '@/i18n'
import type { PluginItem } from '../types/plugin'
import { AxButton, AxIcon } from '@/components/ui'
import McpToolTester from './McpToolTester.vue'

const emit = defineEmits<{
  (e: 'install', id: string, name: string): void
  (e: 'uninstall', id: string, name: string): void
  (e: 'open-config', plugin: PluginItem): void
}>()

const pluginStore = usePluginStore()
const { t } = useI18n()

const activeDetailTab = ref<'overview' | 'tools' | 'config' | 'changelog'>('overview')
</script>

<template>
  <div class="flex-1 h-full overflow-hidden p-6 bg-slate-50/50 dark:bg-[#1E1F22] flex flex-col">
    <!-- Empty State when no MCP server is selected -->
    <div v-if="!pluginStore.selectedPlugin" class="flex-1 flex flex-col items-center justify-center text-slate-400 dark:text-[#868A91]">
      <AxIcon name="puzzle" size="lg" class="mb-3 text-slate-300 dark:text-[#393B40] text-4xl" />
      <p class="text-sm">{{ t('mcpStudio.selectServerHint') }}</p>
    </div>

    <div v-else class="h-full flex flex-col space-y-4 overflow-hidden">
      <!-- Detail Header Card -->
      <div class="p-5 rounded-2xl bg-white dark:bg-[#2B2D30] border border-slate-200/90 dark:border-[#393B40] shadow-sm flex items-start justify-between gap-4">
        <div class="flex items-start gap-4 min-w-0">
          <div class="w-12 h-12 rounded-xl bg-[#3574F0]/15 dark:bg-[#3574F0]/25 text-[#3574F0] flex items-center justify-center font-bold text-xl shadow-sm border border-[#3574F0]/30 flex-shrink-0">
            <AxIcon v-if="pluginStore.selectedPlugin.type === 'mcp' || !pluginStore.selectedPlugin.icon" name="puzzle" size="lg" />
            <i v-else :class="pluginStore.selectedPlugin.icon"></i>
          </div>

          <div class="min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h1 class="text-base font-extrabold text-slate-900 dark:text-[#DFE1E5] tracking-tight truncate">
                {{ pluginStore.selectedPlugin.name }}
              </h1>
              <Tag value="APPROVED" severity="success" class="!text-[10px] !py-0.5 !px-2 !font-bold dark:bg-[#5FAD65]/20 dark:text-[#5FAD65]" />
              <Tag :value="pluginStore.selectedPlugin.category || 'MCP PROTOCOL'" class="!text-[10px] !py-0.5 !px-2 !font-bold dark:bg-[#393B40] dark:text-[#DFE1E5]" />
            </div>

            <p class="text-xs text-slate-500 dark:text-[#868A91] mt-1 flex items-center gap-2">
              <span>{{ t('portal.authorLabel') }}: <strong class="text-slate-700 dark:text-[#DFE1E5]">{{ pluginStore.selectedPlugin.vendor }}</strong></span>
              <span>&bull;</span>
              <span>{{ t('portal.versionLabel') }}: <strong class="font-mono text-slate-700 dark:text-[#DFE1E5]">v{{ pluginStore.selectedPlugin.version }}</strong></span>
            </p>

            <div class="flex items-center gap-3 mt-2 text-xs text-slate-500 dark:text-[#868A91]">
              <span class="flex items-center gap-1 text-[#E3A83F] font-bold">
                <AxIcon name="star" size="xs" class="fill-[#E3A83F] text-[#E3A83F]" />
                {{ pluginStore.selectedPlugin.rating }}
              </span>
              <span>&bull;</span>
              <span>{{ pluginStore.selectedPlugin.downloads }}</span>
            </div>
          </div>
        </div>

        <!-- Top-right Action Buttons -->
        <div class="flex items-center gap-2.5 flex-shrink-0">
          <template v-if="!pluginStore.selectedPlugin.installed">
            <AxButton
              variant="primary"
              size="md"
              ijIcon="download"
              data-testid="detail-install-btn"
              @click="emit('install', pluginStore.selectedPlugin.id, pluginStore.selectedPlugin.name)"
            >
              <span>{{ t('mcpStudio.installBtn') }}</span>
            </AxButton>
          </template>
          <template v-else>
            <div class="flex items-center gap-2 bg-slate-100 dark:bg-[#1E1F22] px-3 py-1.5 rounded-lg border border-slate-200 dark:border-[#43454A]">
              <span class="text-xs font-semibold text-slate-600 dark:text-[#DFE1E5]">
                {{ pluginStore.selectedPlugin.enabled ? t('portal.activeStatus') : t('portal.disabledStatus') }}
              </span>
              <button
                type="button"
                role="switch"
                :aria-checked="pluginStore.selectedPlugin.enabled"
                class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
                :class="pluginStore.selectedPlugin.enabled ? 'bg-[#5FAD65]' : 'bg-slate-300 dark:bg-[#43454A]'"
                @click="pluginStore.togglePlugin(pluginStore.selectedPlugin.id)"
              >
                <span
                  class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out"
                  :class="pluginStore.selectedPlugin.enabled ? 'translate-x-4' : 'translate-x-0'"
                />
              </button>
            </div>

            <!-- Configure Button -->
            <AxButton
              v-if="pluginStore.selectedPlugin.envRequirements?.length"
              variant="secondary"
              size="md"
              ijIcon="settings"
              data-testid="detail-config-btn"
              @click="emit('open-config', pluginStore.selectedPlugin)"
            >
              <span>{{ t('mcpStudio.configureBtn') }}</span>
            </AxButton>

            <!-- Uninstall Button -->
            <AxButton
              variant="danger"
              size="md"
              ijIcon="trash"
              data-testid="detail-uninstall-btn"
              @click="emit('uninstall', pluginStore.selectedPlugin.id, pluginStore.selectedPlugin.name)"
            >
              <span>{{ t('mcpStudio.uninstallBtn') }}</span>
            </AxButton>
          </template>
        </div>
      </div>

      <!-- Scope Card (If installed) -->
      <div
        v-if="pluginStore.selectedPlugin.installed"
        class="p-3.5 rounded-xl bg-[#3574F0]/10 dark:bg-[#2E436E]/30 border border-[#3574F0]/25 flex items-center justify-between text-xs"
      >
        <div class="flex items-center gap-2.5">
          <AxIcon name="folder" size="sm" class="text-[#3574F0] dark:text-[#56A8F5]" />
          <div>
            <span class="font-bold text-slate-900 dark:text-[#DFE1E5]">
              {{ t('mcpStudio.sandboxPathLabel') }} <code class="font-mono bg-white dark:bg-[#1E1F22] px-1 py-0.5 rounded border border-slate-200 dark:border-[#393B40]">{{ pluginStore.selectedPlugin.installPath || '~/.aipro/mcp' }}</code>
            </span>
            <span class="block text-[11px] text-slate-500 dark:text-[#868A91] mt-0.5">
              {{ t('mcpStudio.protocolDesc') }}
            </span>
          </div>
        </div>
        <Tag value="MCP SERVER" severity="success" class="!text-[10px] !font-bold dark:bg-[#5FAD65]/20 dark:text-[#5FAD65]" />
      </div>

      <!-- Navigation Tabs inside Detail -->
      <div class="flex items-center gap-2 border-b border-slate-200 dark:border-[#393B40] pb-2">
        <button
          type="button"
          data-testid="subtab-overview"
          class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
          :class="activeDetailTab === 'overview' 
            ? 'bg-white dark:bg-[#2B2D30] text-[#3574F0] dark:text-[#56A8F5] shadow-xs border border-slate-200 dark:border-[#393B40]' 
            : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
          @click="activeDetailTab = 'overview'"
        >
          <AxIcon name="code" size="xs" />
          <span>{{ t('mcpStudio.tabOverview') }}</span>
        </button>

        <button
          type="button"
          data-testid="subtab-tools"
          class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
          :class="activeDetailTab === 'tools' 
            ? 'bg-white dark:bg-[#2B2D30] text-[#3574F0] dark:text-[#56A8F5] shadow-xs border border-slate-200 dark:border-[#393B40]' 
            : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
          @click="activeDetailTab = 'tools'"
        >
          <AxIcon name="terminal" size="xs" />
          <span>{{ t('mcpStudio.tabTools', { count: pluginStore.selectedPlugin.tools?.length || 0 }) }}</span>
        </button>

        <button
          v-if="pluginStore.selectedPlugin.envRequirements?.length"
          type="button"
          data-testid="subtab-config"
          class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
          :class="activeDetailTab === 'config' 
            ? 'bg-white dark:bg-[#2B2D30] text-[#3574F0] dark:text-[#56A8F5] shadow-xs border border-slate-200 dark:border-[#393B40]' 
            : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
          @click="activeDetailTab = 'config'"
        >
          <AxIcon name="settings" size="xs" class="text-[#E3A83F]" />
          <span>{{ t('mcpStudio.tabEnv') }}</span>
        </button>

        <button
          type="button"
          data-testid="subtab-changelog"
          class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
          :class="activeDetailTab === 'changelog' 
            ? 'bg-white dark:bg-[#2B2D30] text-[#3574F0] dark:text-[#56A8F5] shadow-xs border border-slate-200 dark:border-[#393B40]' 
            : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
          @click="activeDetailTab = 'changelog'"
        >
          <AxIcon name="branches" size="xs" />
          <span>{{ t('mcpStudio.tabChangelog') }}</span>
        </button>
      </div>

      <!-- Detail Sub-Tab Content Area -->
      <div class="flex-1 overflow-y-auto bg-white dark:bg-[#2B2D30] rounded-2xl border border-slate-200/90 dark:border-[#393B40] p-5 min-h-0">
        <!-- 1. OVERVIEW TAB -->
        <div v-if="activeDetailTab === 'overview'" class="space-y-4">
          <div class="prose dark:prose-invert max-w-none text-xs text-slate-700 dark:text-[#CED0D6] leading-relaxed">
            <h3 class="text-sm font-bold text-slate-900 dark:text-[#DFE1E5] mb-2">{{ t('mcpStudio.serverDescTitle') }}</h3>
            <p>{{ pluginStore.selectedPlugin.description }}</p>

            <h3 class="text-sm font-bold text-slate-900 dark:text-[#DFE1E5] mt-4 mb-2">{{ t('mcpStudio.keyFeaturesTitle') }}</h3>
            <div class="space-y-1.5">
              <div
                v-for="(feat, idx) in pluginStore.selectedPlugin.features"
                :key="idx"
                class="flex items-start gap-2"
              >
                <AxIcon name="check" size="xs" class="text-[#5FAD65] mt-0.5 shrink-0" />
                <span>{{ feat }}</span>
              </div>
            </div>

            <!-- Specifications Card -->
            <h3 class="text-sm font-bold text-slate-900 dark:text-[#DFE1E5] mt-4 mb-2">{{ t('mcpStudio.specsTitle') }}</h3>
            <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-200/80 dark:border-[#393B40] grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
              <div>
                <span class="text-slate-400 dark:text-[#868A91] block mb-0.5">{{ t('mcpStudio.extensionType') }}</span>
                <span class="font-bold text-slate-800 dark:text-[#DFE1E5]">{{ pluginStore.selectedPlugin.type }} Protocol</span>
              </div>
              <div>
                <span class="text-slate-400 dark:text-[#868A91] block mb-0.5">{{ t('mcpStudio.executionProtocol') }}</span>
                <span class="font-bold text-slate-800 dark:text-[#DFE1E5]">JSON-RPC 2.0 (Stdio / SSE)</span>
              </div>
              <div>
                <span class="text-slate-400 dark:text-[#868A91] block mb-0.5">{{ t('mcpStudio.versionLabel') }}</span>
                <span class="font-mono text-slate-800 dark:text-[#DFE1E5]">v{{ pluginStore.selectedPlugin.version }}</span>
              </div>
              <div>
                <span class="text-slate-400 dark:text-[#868A91] block mb-0.5">{{ t('mcpStudio.statusLabel') }}</span>
                <span class="font-bold text-[#5FAD65]">
                  {{ pluginStore.selectedPlugin.installed ? (pluginStore.selectedPlugin.enabled ? t('portal.activeStatus') : t('portal.disabledStatus')) : t('portal.notInstalled') }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. TOOLS TAB -->
        <McpToolTester v-else-if="activeDetailTab === 'tools'" />

        <!-- 3. CONFIG TAB -->
        <div v-else-if="activeDetailTab === 'config'" class="space-y-4">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-[#393B40]">
            <span class="text-xs text-slate-500 dark:text-[#868A91]">
              {{ t('mcpStudio.envNotice') }}
            </span>
            <AxButton
              variant="outline"
              size="sm"
              ijIcon="settings"
              @click="emit('open-config', pluginStore.selectedPlugin)"
            >
              <span>{{ t('mcpStudio.editEnvBtn') }}</span>
            </AxButton>
          </div>

          <div class="space-y-2">
            <div
              v-for="req in pluginStore.selectedPlugin.envRequirements"
              :key="req.key"
              class="p-3 rounded-lg border border-slate-200 dark:border-[#393B40] bg-slate-50 dark:bg-[#1E1F22] flex items-center justify-between text-xs"
            >
              <div>
                <span class="font-mono font-bold text-slate-800 dark:text-[#DFE1E5]">{{ req.key }}</span>
                <span class="text-[11px] text-slate-400 dark:text-[#868A91] ml-2">({{ req.label || req.key }})</span>
                <Tag v-if="req.required" :value="t('mcpStudio.requiredBadge')" severity="danger" class="!text-[9px] !py-0 !px-1 ml-2 dark:bg-[#FA5252]/20 dark:text-[#FA5252]" />
              </div>
              <div class="font-mono text-slate-500 dark:text-[#868A91]">
                {{ pluginStore.selectedPlugin.configuredEnv?.[req.key] ? '••••••••' : (req.default || t('mcpStudio.notConfigured')) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 4. CHANGELOG TAB -->
        <div v-else-if="activeDetailTab === 'changelog'" class="space-y-3">
          <div class="p-4 rounded-xl border border-slate-200 dark:border-[#393B40] bg-slate-50 dark:bg-[#1E1F22] text-xs">
            <div class="flex items-center justify-between mb-2">
              <span class="font-bold text-slate-800 dark:text-[#DFE1E5]">{{ t('mcpStudio.versionPrefix') }} v{{ pluginStore.selectedPlugin.version }}</span>
              <Tag :value="t('mcpStudio.currentBadge')" severity="success" class="!text-[10px] dark:bg-[#5FAD65]/20 dark:text-[#5FAD65]" />
            </div>
            <p class="text-slate-600 dark:text-[#CED0D6] leading-relaxed">
              {{ pluginStore.selectedPlugin.changeNotes || t('mcpStudio.releaseNotesDefault') }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
