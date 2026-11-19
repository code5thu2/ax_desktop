<script setup lang="ts">
import Tag from 'primevue/tag'
import { useSkillStore } from '../stores/skillStore'
import { useI18n } from '@/i18n'
import type { SkillItem } from '@/types/generated/SkillItem'
import type { InstalledPlugin } from '@/types/generated/InstalledPlugin'
import { AxButton, AxIcon, AxSearchInput } from '@/components/ui'

const store = useSkillStore()
const { t } = useI18n()

const categories = ['All', 'Legal', 'Frontend', 'Backend', 'Automation', 'General']

function handleSelectSkill(skill: SkillItem) {
  store.selectSkill(skill)
}

function handleSelectInstalled(installed: InstalledPlugin) {
  store.selectInstalledSkill(installed)
}

function handleOpenInstall(skill: SkillItem, e: Event) {
  e.stopPropagation()
  store.pendingInstallSkill = skill
  store.showScopeModal = true
}

function getProjectFolder(path?: string | null): string {
  if (!path) return t('portal.project')
  const clean = path.replace(/\\/g, '/').split('/').filter(Boolean)
  return clean[clean.length - 1] || t('portal.project')
}
</script>

<template>
  <div class="h-full flex flex-col p-4 space-y-3.5 overflow-hidden border-r border-slate-200/90 dark:border-[#393B40] bg-white dark:bg-[#2B2D30]">
    <!-- Search Bar -->
    <div class="relative">
      <AxSearchInput
        v-model="store.searchQuery"
        :placeholder="t('portal.searchSkillsPlaceholder')"
        shortcut="⌘K"
      />
    </div>

    <!-- Category Pills (Marketplace tab) -->
    <div v-if="store.activeTab === 'marketplace'" class="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
      <button
        v-for="cat in categories"
        :key="cat"
        type="button"
        class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
        :class="store.selectedCategory === cat 
          ? 'bg-[#3574F0] text-white shadow-xs' 
          : 'bg-slate-100 dark:bg-[#1E1F22] text-slate-600 dark:text-[#868A91] hover:bg-slate-200 dark:hover:bg-[#393B40]'"
        @click="store.selectedCategory = cat"
      >
        {{ cat }}
      </button>
    </div>

    <!-- Installed Sub-filter (Installed tab) -->
    <div v-else-if="store.activeTab === 'installed'" class="flex items-center gap-1.5 pb-1">
      <button
        type="button"
        class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all cursor-pointer"
        :class="store.installedFilter === 'all' 
          ? 'bg-[#3574F0] text-white shadow-xs' 
          : 'bg-slate-100 dark:bg-[#1E1F22] text-slate-600 dark:text-[#868A91] hover:bg-slate-200 dark:hover:bg-[#393B40]'"
        @click="store.setInstalledFilter('all')"
      >
        {{ t('portal.all') }}
      </button>
      <button
        type="button"
        class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all cursor-pointer flex items-center gap-1"
        :class="store.installedFilter === 'global' 
          ? 'bg-[#3574F0] text-white shadow-xs' 
          : 'bg-slate-100 dark:bg-[#1E1F22] text-slate-600 dark:text-[#868A91] hover:bg-slate-200 dark:hover:bg-[#393B40]'"
        @click="store.setInstalledFilter('global')"
      >
        <AxIcon name="branches" size="xs" />
        <span>{{ t('portal.global') }}</span>
      </button>
      <button
        type="button"
        class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all cursor-pointer flex items-center gap-1"
        :class="store.installedFilter === 'project' 
          ? 'bg-[#3574F0] text-white shadow-xs' 
          : 'bg-slate-100 dark:bg-[#1E1F22] text-slate-600 dark:text-[#868A91] hover:bg-slate-200 dark:hover:bg-[#393B40]'"
        @click="store.setInstalledFilter('project')"
      >
        <AxIcon name="folder" size="xs" />
        <span>{{ t('portal.project') }}</span>
      </button>
    </div>

    <!-- Skills Cards List -->
    <div class="flex-1 overflow-y-auto space-y-2 pr-1">
      <!-- Loading Skeleton State -->
      <div v-if="store.isLoading" class="space-y-2.5">
        <div v-for="i in 3" :key="i" class="p-3.5 rounded-xl border border-slate-200/80 dark:border-[#393B40] bg-slate-50/50 dark:bg-[#1E1F22] animate-shimmer">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-9 h-9 rounded-lg bg-slate-200 dark:bg-[#393B40]"></div>
            <div class="flex-1 space-y-1.5">
              <div class="h-3 bg-slate-200 dark:bg-[#393B40] rounded w-2/3"></div>
              <div class="h-2 bg-slate-200 dark:bg-[#393B40] rounded w-1/3"></div>
            </div>
          </div>
          <div class="h-2 bg-slate-200 dark:bg-[#393B40] rounded w-full mb-1"></div>
          <div class="h-2 bg-slate-200 dark:bg-[#393B40] rounded w-4/5"></div>
        </div>
      </div>

      <!-- Marketplace Tab list -->
      <template v-else-if="store.activeTab === 'marketplace'">
        <div
          v-for="skill in store.filteredMarketplaceSkills"
          :key="skill.name"
          class="p-3 rounded-xl border transition-all cursor-pointer flex flex-col gap-2 group"
          :class="store.selectedSkillName === skill.name 
            ? '!border-[#3574F0] bg-[#3574F0]/10 dark:bg-[#2E436E]/40 shadow-xs ring-1 ring-[#3574F0]/30' 
            : 'border-slate-200/80 dark:border-[#393B40] hover:border-slate-300 dark:hover:border-[#43454A] bg-white dark:bg-[#2B2D30]'"
          @click="handleSelectSkill(skill)"
        >
          <!-- Card top -->
          <div class="flex items-start justify-between gap-2.5">
            <div class="flex items-center gap-2.5 min-w-0">
              <div class="w-9 h-9 rounded-lg bg-[#3574F0]/15 dark:bg-[#3574F0]/25 text-[#3574F0] flex items-center justify-center font-bold text-sm shadow-xs flex-shrink-0 border border-[#3574F0]/30">
                <AxIcon name="puzzle" size="sm" />
              </div>
              <div class="min-w-0">
                <h3 class="text-xs font-bold text-slate-900 dark:text-[#DFE1E5] truncate">
                  {{ skill.name }}
                </h3>
                <div class="text-[11px] text-slate-400 dark:text-[#868A91] flex items-center gap-1.5 mt-0.5">
                  <span class="truncate">{{ skill.creatorName }}</span>
                  <span>&bull;</span>
                  <span class="font-mono">v{{ skill.installedVersion || 1 }}.0.0</span>
                </div>
              </div>
            </div>

            <!-- Install quick button or ready check -->
            <div @click.stop>
              <AxButton
                v-if="!skill.installed"
                variant="primary"
                size="sm"
                ijIcon="download"
                @click="handleOpenInstall(skill, $event)"
              >
                <span>{{ t('portal.install') }}</span>
              </AxButton>
              <span v-else class="text-[11px] font-semibold text-[#5FAD65] flex items-center gap-1">
                <AxIcon name="check" size="xs" /> {{ t('portal.readyBadge') }}
              </span>
            </div>
          </div>

          <!-- Description preview -->
          <p class="text-[11px] text-slate-600 dark:text-[#868A91] line-clamp-2 leading-relaxed">
            {{ skill.description }}
          </p>

          <!-- Card footer -->
          <div class="flex items-center justify-between pt-1 text-[11px] text-slate-400 dark:text-[#868A91] border-t border-slate-100 dark:border-[#393B40]">
            <div class="flex items-center gap-2">
              <span class="flex items-center gap-1 text-[#E3A83F] font-bold">
                <AxIcon name="star" size="xs" class="fill-[#E3A83F] text-[#E3A83F]" />
                {{ skill.avgRating || 5.0 }}
              </span>
              <span>&bull;</span>
              <span>{{ skill.viewCount || 0 }} {{ t('portal.views') }}</span>
            </div>

            <div class="flex items-center gap-1.5">
              <Tag
                v-if="skill.categories?.[0]"
                :value="skill.categories[0]"
                class="!text-[10px] !py-0 !px-1.5 dark:bg-[#393B40] dark:text-[#DFE1E5]"
              />
            </div>
          </div>
        </div>
      </template>

      <!-- Installed Tab list -->
      <template v-else-if="store.activeTab === 'installed'">
        <div
          v-for="installed in store.filteredInstalledSkills"
          :key="`${installed.name}-${installed.projectPath || 'global'}`"
          class="p-3 rounded-xl border transition-all cursor-pointer flex flex-col gap-2 group"
          :class="store.selectedInstalledKey === `${installed.name}-${installed.projectPath || 'global'}` 
            ? '!border-[#3574F0] bg-[#3574F0]/10 dark:bg-[#2E436E]/40 shadow-xs ring-1 ring-[#3574F0]/30' 
            : 'border-slate-200/80 dark:border-[#393B40] hover:border-slate-300 dark:hover:border-[#43454A] bg-white dark:bg-[#2B2D30]'"
          @click="handleSelectInstalled(installed)"
        >
          <div class="flex items-start justify-between gap-2.5">
            <div class="flex items-center gap-2.5 min-w-0">
              <div class="w-9 h-9 rounded-lg bg-[#3574F0]/15 dark:bg-[#3574F0]/25 text-[#3574F0] flex items-center justify-center font-bold text-sm shadow-xs flex-shrink-0 border border-[#3574F0]/30">
                <AxIcon name="puzzle" size="sm" />
              </div>
              <div class="min-w-0">
                <h3 class="text-xs font-bold text-slate-900 dark:text-[#DFE1E5] truncate">
                  {{ installed.name }}
                </h3>
                <div class="text-[11px] text-slate-400 dark:text-[#868A91] flex items-center gap-1.5 mt-0.5">
                  <span class="font-mono">v{{ installed.version }}.0.0</span>
                  <span>&bull;</span>
                  <span v-if="installed.scope === 'project'" class="truncate text-[#3574F0] dark:text-[#56A8F5] flex items-center gap-1">
                    <AxIcon name="folder" size="xs" />
                    {{ getProjectFolder(installed.projectPath) }}
                  </span>
                  <span v-else class="text-[#C77DBB] flex items-center gap-1">
                    <AxIcon name="branches" size="xs" />
                    {{ t('portal.global') }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Toggle Switch -->
            <div @click.stop>
              <button
                type="button"
                role="switch"
                :aria-checked="installed.enabled"
                class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
                :class="installed.enabled ? 'bg-[#5FAD65]' : 'bg-slate-300 dark:bg-[#43454A]'"
                @click="store.toggleSkill(installed.name, !installed.enabled, installed.projectPath)"
              >
                <span
                  class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out"
                  :class="installed.enabled ? 'translate-x-4' : 'translate-x-0'"
                />
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
