<script setup lang="ts">
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import InputSwitch from 'primevue/inputswitch'
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

function handleToggleInstalled(skillName: string, enabled: boolean) {
  store.toggleSkill(skillName, enabled)
}
</script>

<template>
  <div class="h-full flex flex-col p-4 space-y-4 overflow-hidden border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/40">
    <!-- Search Bar -->
    <div class="relative">
      <i class="pi pi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
      <InputText
        v-model="store.searchQuery"
        :placeholder="t('portal.searchSkillsPlaceholder')"
        class="w-full !pl-9 !py-2 !text-xs !rounded-xl"
      />
      <button
        v-if="store.searchQuery"
        type="button"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs cursor-pointer"
        @click="store.searchQuery = ''"
      >
        <i class="pi pi-times"></i>
      </button>
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
    <div v-else-if="store.activeTab === 'installed'" class="flex items-center gap-2 pb-1">
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer"
        :class="store.installedFilter === 'all' ? 'bg-emerald-500 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'"
        @click="store.setInstalledFilter('all')"
      >
        {{ t('portal.all') }}
      </button>
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer"
        :class="store.installedFilter === 'global' ? 'bg-emerald-500 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'"
        @click="store.setInstalledFilter('global')"
      >
        {{ t('portal.global') }}
      </button>
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer"
        :class="store.installedFilter === 'project' ? 'bg-emerald-500 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'"
        @click="store.setInstalledFilter('project')"
      >
        {{ t('portal.project') }}
      </button>
    </div>

    <!-- Skills Cards List -->
    <div class="flex-1 overflow-y-auto space-y-2.5 pr-1">
      <!-- Loading state -->
      <div v-if="store.isLoading" class="text-center py-12 text-slate-400">
        <i class="pi pi-spin pi-spinner text-2xl mb-2 text-emerald-500 block"></i>
        <span class="text-xs">Đang tải danh sách skill...</span>
      </div>

      <!-- Marketplace Tab list -->
      <template v-else-if="store.activeTab === 'marketplace'">
        <div
          v-for="skill in store.filteredMarketplaceSkills"
          :key="skill.name"
          class="p-3.5 rounded-2xl border transition-all cursor-pointer flex flex-col gap-2.5"
          :class="store.selectedSkillName === skill.name ? 'border-emerald-500 bg-emerald-50/40 dark:bg-emerald-950/20 shadow-xs' : 'border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900/60'"
          @click="handleSelectSkill(skill)"
        >
          <!-- Card top -->
          <div class="flex items-start justify-between gap-2.5">
            <div class="flex items-center gap-2.5 min-w-0">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-sm shadow-xs flex-shrink-0">
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

            <div class="flex items-center gap-1.5">
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
              <Button
                v-if="!skill.installed"
                type="button"
                :label="t('portal.installBtn')"
                icon="pi pi-download"
                class="!py-1 !px-2.5 !text-[11px] !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-xs cursor-pointer !rounded-lg"
                @click="handleOpenInstall(skill, $event)"
              />
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
          :key="installed.name"
          class="p-3.5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between gap-3"
          :class="store.selectedSkillName === installed.name ? 'border-emerald-500 bg-emerald-50/40 dark:bg-emerald-950/20 shadow-xs' : 'border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900/60'"
          @click="handleSelectInstalled(installed)"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-sm shadow-xs flex-shrink-0">
              <i class="pi pi-bolt"></i>
            </div>
            <div class="min-w-0">
              <h3 class="text-xs font-bold text-slate-900 dark:text-white truncate">
                {{ installed.name }}
              </h3>
              <div class="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                <Tag
                  :value="installed.scope === 'global' ? 'Global' : 'Project'"
                  :severity="installed.scope === 'global' ? 'info' : 'warn'"
                  class="!text-[9px] !py-0.5 !px-1.5"
                />
                <span>v{{ installed.version }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-3" @click.stop>
            <InputSwitch
              :modelValue="installed.enabled"
              @update:modelValue="(val) => handleToggleInstalled(installed.name, val)"
            />
          </div>
        </div>

        <div v-if="store.filteredInstalledSkills.length === 0" class="text-center py-12 text-xs text-slate-400">
          {{ t('portal.noInstalledSkills') }}
        </div>
      </template>
    </div>
  </div>
</template>
