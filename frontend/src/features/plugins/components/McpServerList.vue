<script setup lang="ts">
import Tag from 'primevue/tag'
import { usePluginStore } from '../stores/pluginStore'
import { useI18n } from '@/i18n'
import { AxButton, AxIcon, AxSearchInput } from '@/components/ui'

withDefaults(defineProps<{ showList?: boolean }>(), {
  showList: true,
})

const emit = defineEmits<{
  (e: 'install', id: string, name: string): void
}>()

const pluginStore = usePluginStore()
const { t } = useI18n()
</script>

<template>
  <div
    v-show="showList"
    data-testid="plugin-list-pane"
    class="w-80 md:w-96 lg:w-[400px] border-r border-slate-200 dark:border-[#393B40] bg-white dark:bg-[#2B2D30] flex flex-col p-4 space-y-3.5 overflow-hidden flex-shrink-0"
  >
    <!-- Search Bar -->
    <div class="relative">
      <AxSearchInput
        v-model="pluginStore.searchQuery"
        data-testid="plugin-search-input"
        :placeholder="t('mcpStudio.searchPlaceholder')"
      />
    </div>

    <!-- Category Filter Pills -->
    <div class="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
      <button
        type="button"
        data-testid="filter-all"
        class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
        :class="pluginStore.filterCategory === 'all' 
          ? 'bg-[#3574F0] text-white shadow-xs' 
          : 'bg-slate-100 dark:bg-[#1E1F22] text-slate-600 dark:text-[#868A91] hover:bg-slate-200 dark:hover:bg-[#393B40]'"
        @click="pluginStore.setFilterCategory('all')"
      >
        {{ t('mcpStudio.catAll') }}
      </button>
      <button
        type="button"
        data-testid="filter-inhouse"
        class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
        :class="pluginStore.filterCategory === 'In-House Tools' 
          ? 'bg-[#3574F0] text-white shadow-xs' 
          : 'bg-slate-100 dark:bg-[#1E1F22] text-slate-600 dark:text-[#868A91] hover:bg-slate-200 dark:hover:bg-[#393B40]'"
        @click="pluginStore.setFilterCategory('In-House Tools')"
      >
        {{ t('mcpStudio.catInHouse') }}
      </button>
      <button
        type="button"
        data-testid="filter-custom"
        class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
        :class="pluginStore.filterCategory === 'Custom Tools' 
          ? 'bg-[#3574F0] text-white shadow-xs' 
          : 'bg-slate-100 dark:bg-[#1E1F22] text-slate-600 dark:text-[#868A91] hover:bg-slate-200 dark:hover:bg-[#393B40]'"
        @click="pluginStore.setFilterCategory('Custom Tools')"
      >
        {{ t('mcpStudio.catCustom') }}
      </button>
      <button
        type="button"
        data-testid="filter-git"
        class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
        :class="pluginStore.filterCategory === 'Git Tools' 
          ? 'bg-[#3574F0] text-white shadow-xs' 
          : 'bg-slate-100 dark:bg-[#1E1F22] text-slate-600 dark:text-[#868A91] hover:bg-slate-200 dark:hover:bg-[#393B40]'"
        @click="pluginStore.setFilterCategory('Git Tools')"
      >
        {{ t('mcpStudio.catGit') }}
      </button>
    </div>

    <!-- MCP Server Cards List -->
    <div class="flex-1 overflow-y-auto space-y-2 pr-1">
      <div
        v-if="pluginStore.filteredPlugins.length === 0"
        class="text-center py-12 text-xs text-slate-400"
      >
        <AxIcon name="puzzle" size="lg" class="mb-2 text-slate-300 dark:text-[#43454A] mx-auto block" />
        <span>{{ t('mcpStudio.noServersFound') }}</span>
      </div>

      <div
        v-for="plugin in pluginStore.filteredPlugins"
        :key="plugin.id"
        :data-testid="`plugin-item-${plugin.id}`"
        class="p-3 rounded-xl border transition-all cursor-pointer flex flex-col gap-2"
        :class="pluginStore.selectedPlugin?.id === plugin.id 
          ? '!border-[#3574F0] bg-[#3574F0]/10 dark:bg-[#2E436E]/40 shadow-xs' 
          : 'border-slate-200/80 dark:border-[#393B40] hover:border-slate-300 dark:hover:border-[#43454A] bg-white dark:bg-[#2B2D30]'"
        @click="pluginStore.selectPlugin(plugin.id)"
      >
        <!-- Card top -->
        <div class="flex items-start justify-between gap-2.5">
          <div class="flex items-center gap-2.5 min-w-0">
            <div class="w-9 h-9 rounded-lg bg-[#3574F0]/15 dark:bg-[#3574F0]/25 text-[#3574F0] flex items-center justify-center font-bold text-sm shadow-xs flex-shrink-0 border border-[#3574F0]/30">
              <AxIcon v-if="plugin.type === 'mcp' || !plugin.icon" name="puzzle" size="sm" />
              <i v-else :class="plugin.icon" class="text-xs"></i>
            </div>
            <div class="min-w-0">
              <h3 class="text-xs font-bold text-slate-900 dark:text-[#DFE1E5] truncate">
                {{ plugin.name }}
              </h3>
              <div class="text-[11px] text-slate-400 dark:text-[#868A91] flex items-center gap-1.5 mt-0.5">
                <span class="truncate">{{ plugin.vendor || 'AIPRO Community' }}</span>
                <span>&bull;</span>
                <span class="font-mono">v{{ plugin.version }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-1.5 flex-shrink-0">
            <Tag
              :value="plugin.category || 'MCP'"
              class="!text-[10px] !py-0.5 !px-1.5 dark:bg-[#393B40] dark:text-[#DFE1E5]"
            />
          </div>
        </div>

        <!-- Summary preview -->
        <p class="text-[11px] text-slate-600 dark:text-[#868A91] line-clamp-2 leading-relaxed">
          {{ plugin.summary || plugin.description }}
        </p>

        <!-- Card footer -->
        <div class="flex items-center justify-between pt-1 text-[11px] text-slate-400 dark:text-[#868A91] border-t border-slate-100 dark:border-[#393B40]">
          <div class="flex items-center gap-2">
            <span class="flex items-center gap-1 text-[#E3A83F] font-bold">
              <AxIcon name="star" size="xs" class="fill-[#E3A83F] text-[#E3A83F]" />
              {{ plugin.rating || 5.0 }}
            </span>
            <span>&bull;</span>
            <span>{{ plugin.downloads || '100+' }}</span>
          </div>

          <div @click.stop>
            <template v-if="pluginStore.activeTab === 'marketplace'">
              <AxButton
                v-if="!plugin.installed"
                variant="primary"
                size="sm"
                ijIcon="download"
                :data-testid="`install-btn-${plugin.id}`"
                @click="emit('install', plugin.id, plugin.name)"
              >
                <span>{{ t('mcpStudio.installBtn') }}</span>
              </AxButton>
              <span v-else class="text-[11px] font-semibold text-[#5FAD65] flex items-center gap-1">
                <AxIcon name="check" size="xs" /> {{ t('portal.readyBadge') }}
              </span>
            </template>
            <template v-else>
              <button
                type="button"
                role="switch"
                :aria-checked="plugin.enabled"
                class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
                :class="plugin.enabled ? 'bg-[#5FAD65]' : 'bg-slate-300 dark:bg-[#43454A]'"
                @click="pluginStore.togglePlugin(plugin.id)"
              >
                <span
                  class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out"
                  :class="plugin.enabled ? 'translate-x-4' : 'translate-x-0'"
                />
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
