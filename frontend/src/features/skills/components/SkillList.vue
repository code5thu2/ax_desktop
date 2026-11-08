<script setup lang="ts">
import Tag from 'primevue/tag'
import { useSkillStore } from '../stores/skillStore'
import { useI18n } from '@/i18n'
import type { SkillItem } from '@/types/generated/SkillItem'
import type { InstalledPlugin } from '@/types/generated/InstalledPlugin'

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
  <div class="h-full flex flex-col p-4 space-y-3.5 overflow-hidden border-r border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900/40">
    <!-- Search Bar with Keyboard Hint -->
    <div class="relative">
      <i class="pi pi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs pointer-events-none"></i>
      <input
        v-model="store.searchQuery"
        type="text"
        :placeholder="t('portal.searchSkillsPlaceholder')"
        class="w-full pl-9 pr-14 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700/80 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30 transition-all"
      />
      <div class="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1">
        <button
          v-if="store.searchQuery"
          type="button"
          class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs cursor-pointer p-0.5"
          @click="store.searchQuery = ''"
        >
          <i class="pi pi-times"></i>
        </button>
        <kbd v-else class="text-[9px] font-mono text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700">⌘K</kbd>
      </div>
    </div>

    <!-- Category Pills (Marketplace tab) -->
    <div v-if="store.activeTab === 'marketplace'" class="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
      <button
        v-for="cat in categories"
        :key="cat"
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer whitespace-nowrap"
        :class="store.selectedCategory === cat ? 'bg-emerald-500 text-white shadow-xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
        @click="store.selectedCategory = cat"
      >
        {{ cat }}
      </button>
    </div>

    <!-- Installed Sub-filter (Installed tab) -->
    <div v-else-if="store.activeTab === 'installed'" class="flex items-center gap-1.5 pb-1">
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer"
        :class="store.installedFilter === 'all' ? 'bg-emerald-500 text-white shadow-xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
        @click="store.setInstalledFilter('all')"
      >
        {{ t('portal.all') }}
      </button>
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer flex items-center gap-1"
        :class="store.installedFilter === 'global' ? 'bg-emerald-500 text-white shadow-xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
        @click="store.setInstalledFilter('global')"
      >
        <i class="pi pi-globe text-[10px]"></i>
        <span>{{ t('portal.global') }}</span>
      </button>
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer flex items-center gap-1"
        :class="store.installedFilter === 'project' ? 'bg-emerald-500 text-white shadow-xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
        @click="store.setInstalledFilter('project')"
      >
        <i class="pi pi-folder text-[10px]"></i>
        <span>{{ t('portal.project') }}</span>
      </button>
    </div>

    <!-- Skills Cards List -->
    <div class="flex-1 overflow-y-auto space-y-2 pr-1">
      <!-- Loading Skeleton State -->
      <div v-if="store.isLoading" class="space-y-2.5">
        <div v-for="i in 3" :key="i" class="p-3.5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40 animate-shimmer">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-xl bg-slate-200 dark:bg-slate-800"></div>
            <div class="flex-1 space-y-1.5">
              <div class="h-3 bg-slate-200 dark:bg-slate-800 rounded w-2/3"></div>
              <div class="h-2 bg-slate-200 dark:bg-slate-800 rounded w-1/3"></div>
            </div>
          </div>
          <div class="h-2 bg-slate-200 dark:bg-slate-800 rounded w-full mb-1"></div>
          <div class="h-2 bg-slate-200 dark:bg-slate-800 rounded w-4/5"></div>
        </div>
      </div>

      <!-- Marketplace Tab list -->
      <template v-else-if="store.activeTab === 'marketplace'">
        <div
          v-for="skill in store.filteredMarketplaceSkills"
          :key="skill.name"
          class="p-3.5 rounded-2xl border transition-all cursor-pointer flex flex-col gap-2.5 group"
          :class="store.selectedSkillName === skill.name ? 'border-emerald-500/80 bg-emerald-50/50 dark:bg-emerald-950/25 shadow-xs ring-1 ring-emerald-500/30' : 'border-slate-200/80 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900/60'"
          @click="handleSelectSkill(skill)"
        >
          <!-- Card top -->
          <div class="flex items-start justify-between gap-2.5">
            <div class="flex items-center gap-2.5 min-w-0">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-sm shadow-xs flex-shrink-0 group-hover:scale-105 transition-transform">
                <i class="pi pi-box"></i>
              </div>
              <div class="min-w-0">
                <h3 class="text-xs font-bold text-slate-900 dark:text-white truncate">
                  {{ skill.name }}
                </h3>
                <div class="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                  <span class="truncate">{{ skill.creatorName }}</span>
                  <span>&bull;</span>
                  <span>v{{ skill.installedVersion || 1 }}</span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-1.5 flex-shrink-0">
              <Tag
                v-if="skill.scope === 'PUBLIC'"
                :value="t('portal.publicBadge')"
                severity="info"
                class="!text-[10px] !py-0.5 !px-1.5"
              />
            </div>
          </div>

          <!-- Description preview -->
          <p class="text-[11px] text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed">
            {{ skill.description }}
          </p>

          <!-- Card footer -->
          <div class="flex items-center justify-between pt-1 text-[11px] text-slate-400 border-t border-slate-100 dark:border-slate-800/80">
            <div class="flex items-center gap-2">
              <span class="flex items-center gap-1 text-amber-500 font-bold">
                <i class="pi pi-star-fill text-[10px]"></i>
                {{ skill.avgRating || 5.0 }}
              </span>
              <span>&bull;</span>
              <span>{{ String(skill.viewCount || 0) }} {{ t('portal.views') }}</span>
            </div>

            <div>
              <button
                v-if="!skill.installed"
                type="button"
                class="py-1 px-2.5 text-[11px] font-bold bg-emerald-500 hover:bg-emerald-600 active:bg-emerald-700 text-white rounded-lg shadow-xs cursor-pointer flex items-center gap-1 transition-all active:scale-95"
                @click="handleOpenInstall(skill, $event)"
              >
                <i class="pi pi-download text-[10px]"></i>
                <span>{{ t('portal.installBtn') }}</span>
              </button>
              <span v-else class="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <i class="pi pi-check text-[10px]"></i> {{ t('portal.readyBadge') }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="store.filteredMarketplaceSkills.length === 0" class="text-center py-12 text-xs text-slate-400">
          {{ t('portal.noMarketplaceSkills', { query: store.searchQuery }) }}
        </div>
      </template>

      <!-- Installed Tab list -->
      <template v-else-if="store.activeTab === 'installed'">
        <div
          v-for="installed in store.filteredInstalledSkills"
          :key="`${installed.id}-${installed.name}-${installed.scope}-${installed.projectPath || 'global'}`"
          class="p-3.5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between gap-3 group"
          :class="store.selectedInstalledKey === `${installed.name}-${installed.scope}-${installed.projectPath || 'global'}` ? 'border-emerald-500/80 bg-emerald-50/50 dark:bg-emerald-950/25 shadow-xs ring-1 ring-emerald-500/30' : 'border-slate-200/80 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900/60'"
          @click="handleSelectInstalled(installed)"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-sm shadow-xs flex-shrink-0 relative group-hover:scale-105 transition-transform">
              <i class="pi pi-bolt"></i>
              <!-- Active status pulse indicator -->
              <span
                class="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full border-2 border-white dark:border-slate-900"
                :class="installed.enabled ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'"
              ></span>
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-1.5">
                <h3 class="text-xs font-bold text-slate-900 dark:text-white truncate">
                  {{ installed.name }}
                </h3>
              </div>

              <!-- Scope & Project Badge Line (Crystal-clear distinction) -->
              <div class="flex items-center gap-1.5 mt-1">
                <!-- Global badge -->
                <span
                  v-if="installed.scope === 'global'"
                  class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-500 dark:text-blue-400 border border-blue-500/20"
                >
                  <i class="pi pi-globe text-[9px]"></i>
                  <span>{{ t('portal.global') }}</span>
                </span>

                <!-- Project badge with Folder Name -->
                <span
                  v-else
                  class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 max-w-[150px] truncate"
                  :title="installed.projectPath || t('portal.project')"
                >
                  <i class="pi pi-folder text-[9px] flex-shrink-0"></i>
                  <span class="truncate">{{ getProjectFolder(installed.projectPath) }}</span>
                </span>

                <span class="text-[10px] font-mono text-slate-400">v{{ installed.version }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-1.5 flex-shrink-0 text-slate-300 dark:text-slate-600 group-hover:text-emerald-500 transition-colors">
            <i class="pi pi-chevron-right text-xs"></i>
          </div>
        </div>

        <div v-if="store.filteredInstalledSkills.length === 0" class="text-center py-12 text-xs text-slate-400">
          <i class="pi pi-inbox text-3xl mb-2 text-slate-300 dark:text-slate-700 block"></i>
          <span>{{ t('portal.noInstalledSkills') }}</span>
        </div>
      </template>
    </div>
  </div>
</template>
