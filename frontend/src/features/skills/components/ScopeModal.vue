<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import { useToast } from 'primevue/usetoast'
import { useSkillStore } from '../stores/skillStore'
import { nativeBridge } from '@/services/nativeBridge'
import { useI18n } from '@/i18n'
import { AxIcon } from '@/components/ui'

const store = useSkillStore()
const { t } = useI18n()
const toast = useToast()

const scopeType = ref<'global' | 'project'>('global')
const selectedProject = ref<string>('')
const customProjectPath = ref<string>('')
const isInstalling = ref(false)

const projectOptions = computed(() => {
  return store.recentProjects.map((p) => ({ label: p, value: p }))
})

// Sync dropdown selection to custom input
watch(selectedProject, (val) => {
  if (val) {
    customProjectPath.value = val
  }
})

// Reset modal inputs on open
watch(
  () => store.showScopeModal,
  (visible) => {
    if (visible) {
      if (store.pendingChangeScopeFrom) {
        if (store.pendingChangeScopeFrom.scope === 'project') {
          scopeType.value = 'global'
          selectedProject.value = ''
          customProjectPath.value = ''
        } else {
          scopeType.value = 'project'
          const defaultProj = store.currentProject || store.recentProjects[0] || ''
          selectedProject.value = defaultProj
          customProjectPath.value = defaultProj
        }
      } else {
        scopeType.value = 'global'
        selectedProject.value = ''
        customProjectPath.value = ''
      }
      isInstalling.value = false
    }
  }
)

const effectiveProjectPath = computed(() => {
  return (customProjectPath.value?.trim() || selectedProject.value?.trim() || '')
})

const isConfirmDisabled = computed(() => {
  if (isInstalling.value) return true
  if (scopeType.value === 'project' && !effectiveProjectPath.value) return true
  return false
})

async function handleBrowseFolder() {
  const res = await nativeBridge.selectFolder()
  if (res.ok && res.path) {
    customProjectPath.value = res.path
    selectedProject.value = res.path
    store.addProject(res.path)
  }
}

async function handleConfirmInstall() {
  if (!store.pendingInstallSkill) return
  if (scopeType.value === 'project' && !effectiveProjectPath.value) return

  isInstalling.value = true
  try {
    const skill = store.pendingInstallSkill
    const targetDir = scopeType.value === 'project'
      ? effectiveProjectPath.value
      : '.'

    if (store.pendingChangeScopeFrom) {
      const oldScope = store.pendingChangeScopeFrom.scope
      const oldProjectPath = store.pendingChangeScopeFrom.projectPath
      if (oldScope !== scopeType.value || (oldScope === 'project' && oldProjectPath !== targetDir)) {
        await nativeBridge.uninstallSkill(skill.name, oldScope === 'project' ? oldProjectPath : undefined)
      }
    }

    await store.installSkill(skill.name, skill.installedVersion || 1, scopeType.value, targetDir)
    store.pendingChangeScopeFrom = null
    store.showScopeModal = false
    store.pendingInstallSkill = null
    toast.add({
      severity: 'success',
      summary: t('common.success'),
      detail: t('portal.installSuccessMsg', { name: skill.name }),
      life: 3000,
    })
  } catch (err: any) {
    console.error('Install failed:', err)
    toast.add({
      severity: 'error',
      summary: t('common.error'),
      detail: err?.message || 'Cài đặt thất bại',
      life: 3000,
    })
  } finally {
    isInstalling.value = false
  }
}

function handleClose() {
  store.pendingChangeScopeFrom = null
  store.showScopeModal = false
  store.pendingInstallSkill = null
}
</script>

<template>
  <Dialog
    v-model:visible="store.showScopeModal"
    modal
    :header="store.pendingChangeScopeFrom ? t('portal.changeScopeModalTitle') : t('scopeModal.title')"
    :style="{ width: '500px' }"
    :closable="!isInstalling"
    class="p-dialog-custom"
  >
    <div class="space-y-5 py-2">
      <div v-if="store.pendingInstallSkill" class="p-3.5 rounded-2xl bg-emerald-50/60 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white shadow-sm font-bold flex-shrink-0">
          <AxIcon name="puzzle" size="md" />
        </div>
        <div class="min-w-0 flex-1">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white truncate">
            {{ store.pendingInstallSkill.name }}
          </h4>
          <p class="text-[11px] text-slate-500 dark:text-slate-400 truncate mt-0.5">
            {{ t('scopeModal.authorLabel') }}: {{ store.pendingInstallSkill.creatorName }} &bull; {{ t('scopeModal.versionLabel') }}: v{{ store.pendingInstallSkill.installedVersion || 1 }}
          </p>
        </div>
      </div>

      <!-- Scope selection -->
      <div class="space-y-3">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {{ t('scopeModal.scopeTitle') }}
        </label>

        <!-- Global Option -->
        <div
          class="flex items-start gap-3 p-3.5 rounded-2xl border transition-all cursor-pointer"
          :class="scopeType === 'global' ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/25 shadow-xs' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40'"
          @click="scopeType = 'global'"
        >
          <div
            class="w-4 h-4 rounded-full border-2 flex items-center justify-center mt-0.5 flex-shrink-0 transition-all"
            :class="scopeType === 'global' ? 'border-emerald-500 bg-emerald-500' : 'border-slate-400 dark:border-slate-600'"
          >
            <div v-if="scopeType === 'global'" class="w-1.5 h-1.5 rounded-full bg-white"></div>
          </div>
          <div class="flex-1 text-xs">
            <span class="font-bold text-slate-900 dark:text-white block cursor-pointer">
              {{ t('scopeModal.globalTitle') }}
            </span>
            <p class="text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed text-[11px]">
              {{ t('scopeModal.globalDesc') }}
            </p>
          </div>
        </div>

        <!-- Project Option -->
        <div
          class="flex items-start gap-3 p-3.5 rounded-2xl border transition-all cursor-pointer"
          :class="scopeType === 'project' ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/25 shadow-xs' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40'"
          @click="scopeType = 'project'"
        >
          <div
            class="w-4 h-4 rounded-full border-2 flex items-center justify-center mt-0.5 flex-shrink-0 transition-all"
            :class="scopeType === 'project' ? 'border-emerald-500 bg-emerald-500' : 'border-slate-400 dark:border-slate-600'"
          >
            <div v-if="scopeType === 'project'" class="w-1.5 h-1.5 rounded-full bg-white"></div>
          </div>
          <div class="flex-1 text-xs">
            <span class="font-bold text-slate-900 dark:text-white block cursor-pointer">
              {{ t('scopeModal.projectTitle') }}
            </span>
            <p class="text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed text-[11px]">
              {{ t('scopeModal.projectDesc') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Project Picker (Only shown when project scope selected) -->
      <div v-if="scopeType === 'project'" class="space-y-2 pt-1">
        <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300">
          {{ t('scopeModal.targetFolderLabel') }}
        </label>

        <div v-if="projectOptions.length > 0" class="mb-2 relative">
          <select
            v-model="selectedProject"
            class="w-full appearance-none text-xs py-2.5 pl-3.5 pr-9 rounded-xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-300 dark:border-[#393B40] text-slate-800 dark:text-[#DFE1E5] focus:outline-none focus:ring-2 focus:ring-[#3574F0]/25 focus:border-[#3574F0] font-medium cursor-pointer shadow-xs transition-all"
          >
            <option value="" disabled>{{ t('scopeModal.recentProjectsPlaceholder') }}</option>
            <option v-for="opt in projectOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
          <AxIcon name="chevron-down" size="xs" class="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 dark:text-[#868A91] pointer-events-none" />
        </div>

        <div class="flex gap-2">
          <input
            v-model="customProjectPath"
            type="text"
            :placeholder="t('scopeModal.customPathPlaceholder')"
            class="flex-1 text-xs py-2 px-3 rounded-xl bg-slate-50 dark:bg-[#1E1F22] border text-slate-900 dark:text-[#DFE1E5] focus:outline-none font-mono"
            :class="!effectiveProjectPath ? 'border-amber-400 dark:border-amber-600 focus:border-amber-500' : 'border-slate-300 dark:border-[#393B40] focus:border-emerald-500'"
          />
          <button
            type="button"
            class="py-2 px-3 text-xs font-semibold rounded-xl border border-slate-300 dark:border-[#393B40] hover:border-slate-400 dark:hover:border-slate-500 bg-white dark:bg-[#1E1F22] text-slate-700 dark:text-[#DFE1E5] flex items-center gap-1.5 transition-all cursor-pointer flex-shrink-0"
            @click="handleBrowseFolder"
          >
            <AxIcon name="folder-open" size="xs" />
            <span>{{ t('scopeModal.browseBtn') }}</span>
          </button>
        </div>

        <!-- Validation warning if project path is missing -->
        <p v-if="!effectiveProjectPath" class="text-[11px] text-amber-600 dark:text-amber-400 flex items-center gap-1.5 font-medium pt-1">
          <AxIcon name="alert" size="xs" class="text-amber-500 flex-shrink-0" />
          <span>{{ t('scopeModal.projectRequiredHint') }}</span>
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <button
          type="button"
          class="py-2 px-3 text-xs font-semibold rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer"
          :disabled="isInstalling"
          @click="handleClose"
        >
          {{ t('scopeModal.cancelBtn') }}
        </button>
        <button
          type="button"
          class="py-2 px-4 text-xs font-bold bg-emerald-500 hover:bg-emerald-600 active:bg-emerald-700 text-white rounded-xl shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          :disabled="isConfirmDisabled"
          @click="handleConfirmInstall"
        >
          <AxIcon v-if="isInstalling" name="spinner" size="xs" class="animate-spin" />
          <AxIcon v-else name="check" size="xs" />
          <span>{{ isInstalling ? t('scopeModal.installingBtn') : (store.pendingChangeScopeFrom ? t('portal.confirmChangeScope') : t('scopeModal.confirmBtn')) }}</span>
        </button>
      </div>
    </template>
  </Dialog>
</template>
