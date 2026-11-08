<script setup lang="ts">
import { computed } from 'vue'
import Tag from 'primevue/tag'
import { useSkillStore } from '../stores/skillStore'
import { useI18n } from '@/i18n'

const store = useSkillStore()
const { t } = useI18n()

const currentProjectSkills = computed(() => {
  if (!store.currentProject) return []
  return store.installedSkills.filter(
    (s) => s.scope === 'project' && s.projectPath === store.currentProject
  )
})

function handleSelectProject(path: string) {
  store.setCurrentProject(path)
}

function handleAddProject() {
  store.pickProjectFolder()
}

function handleRemoveProject(path: string, e: Event) {
  e.stopPropagation()
  store.removeProject(path)
}

function handleToggleSkill(skillName: string, enabled: boolean) {
  store.toggleSkill(skillName, enabled, store.currentProject || undefined)
}

function handleUninstall(skillName: string) {
  store.uninstallSkill(skillName, store.currentProject || undefined)
}

function handleOpenClone() {
  store.showCloneSkillModal = true
}
</script>

<template>
  <div class="h-full flex flex-col p-6 space-y-6 overflow-hidden">
    <!-- Top toolbar -->
    <div class="flex items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          {{ t('projects.title') }}
        </h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          {{ t('projects.subtitle') }}
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="py-1.5 px-3 text-xs font-semibold rounded-xl border border-slate-300 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-600 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 flex items-center gap-1.5 transition-all cursor-pointer"
          @click="handleOpenClone"
        >
          <i class="pi pi-copy text-xs"></i>
          <span>{{ t('projects.cloneBtn') }}</span>
        </button>
        <button
          type="button"
          class="py-1.5 px-3.5 text-xs font-bold rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white shadow-md shadow-emerald-500/20 flex items-center gap-1.5 transition-all cursor-pointer active:scale-95"
          @click="handleAddProject"
        >
          <i class="pi pi-plus text-xs"></i>
          <span>{{ t('projects.addBtn') }}</span>
        </button>
      </div>
    </div>

    <!-- Main Grid: Projects List + Current Project Skills -->
    <div class="flex-1 grid grid-cols-12 gap-6 min-h-0">
      <!-- Left: Recent Projects List -->
      <div class="col-span-5 flex flex-col bg-white dark:bg-slate-900/60 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 overflow-hidden">
        <div class="flex items-center justify-between mb-3 px-1">
          <span class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            {{ t('projects.recentTitle', { count: store.recentProjects.length }) }}
          </span>
        </div>

        <div class="flex-1 overflow-y-auto space-y-2 pr-1">
          <div
            v-for="projPath in store.recentProjects"
            :key="projPath"
            class="group p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between gap-2"
            :class="store.currentProject === projPath ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/20 shadow-xs' : 'border-slate-200/80 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40'"
            @click="handleSelectProject(projPath)"
          >
            <div class="min-w-0 flex items-center gap-2.5">
              <i class="pi pi-folder text-base" :class="store.currentProject === projPath ? 'text-emerald-500' : 'text-slate-400'"></i>
              <div class="min-w-0">
                <div class="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">
                  {{ projPath.split('/').pop() || projPath }}
                </div>
                <div class="text-[11px] font-mono text-slate-400 truncate">
                  {{ projPath }}
                </div>
              </div>
            </div>

            <button
              type="button"
              class="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-all cursor-pointer"
              :title="t('projects.removeTooltip')"
              @click="handleRemoveProject(projPath, $event)"
            >
              <i class="pi pi-trash text-xs"></i>
            </button>
          </div>

          <div v-if="store.recentProjects.length === 0" class="text-center py-10 text-xs text-slate-400">
            <i class="pi pi-folder text-3xl mb-2 text-slate-300 dark:text-slate-700 block"></i>
            {{ t('projects.noProjects') }}
          </div>
        </div>
      </div>

      <!-- Right: Active Project Skills -->
      <div class="col-span-7 flex flex-col bg-white dark:bg-slate-900/60 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 overflow-hidden">
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
          <div>
            <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
              {{ t('projects.workspaceTitle') }}
            </span>
            <div class="text-sm font-extrabold text-slate-900 dark:text-white font-mono truncate mt-0.5">
              {{ store.currentProject || t('projects.noProjectSelected') }}
            </div>
          </div>
          <Tag :value="`${currentProjectSkills.length} skills`" severity="success" class="!text-[11px] !font-bold" />
        </div>

        <div class="flex-1 overflow-y-auto space-y-2.5 pr-1">
          <div
            v-for="skill in currentProjectSkills"
            :key="skill.name"
            class="p-3.5 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex items-center justify-between gap-3"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white shadow-xs font-bold flex-shrink-0">
                <i class="pi pi-bolt text-sm"></i>
              </div>
              <div class="min-w-0">
                <div class="text-xs font-bold text-slate-900 dark:text-white truncate">
                  {{ skill.name }}
                </div>
                <div class="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5">
                  <span>v{{ skill.version }}</span>
                  <span>&bull;</span>
                  <span>{{ t('portal.installedAt') }}: {{ new Date(skill.installedAt).toLocaleDateString() }}</span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <button
                type="button"
                role="switch"
                :aria-checked="skill.enabled"
                class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
                :class="skill.enabled ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-slate-700'"
                @click="handleToggleSkill(skill.name, !skill.enabled)"
              >
                <span
                  class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out"
                  :class="skill.enabled ? 'translate-x-4' : 'translate-x-0'"
                />
              </button>
              <button
                type="button"
                class="p-2 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors cursor-pointer"
                :title="t('projects.uninstallBtn')"
                @click="handleUninstall(skill.name)"
              >
                <i class="pi pi-trash text-xs"></i>
              </button>
            </div>
          </div>

          <div v-if="currentProjectSkills.length === 0" class="text-center py-14 text-xs text-slate-400">
            <i class="pi pi-box text-3xl mb-2 text-slate-300 dark:text-slate-700 block"></i>
            {{ t('projects.noSkillsInWorkspace') }}<br />
            {{ t('projects.goToMarketplace') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
