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

const sourceProject = ref<string>(store.currentProject || '')
const targetProject = ref<string>('')
const selectedSkillNames = ref<string[]>([])
const isCloning = ref(false)
const errorMsg = ref<string | null>(null)

const projectOptions = computed(() => {
  return store.recentProjects.map((p) => ({ label: p, value: p }))
})

// Strictly filter ONLY project-scoped skills belonging to the selected source project.
const availableSkillsToClone = computed(() => {
  if (!sourceProject.value) return []
  const normSource = sourceProject.value.replace(/\\/g, '/').toLowerCase()
  return store.installedSkills
    .filter(
      (s) =>
        s.scope === 'project' &&
        s.projectPath &&
        s.projectPath.replace(/\\/g, '/').toLowerCase() === normSource
    )
    .map((s) => s.name)
})

watch(sourceProject, () => {
  selectedSkillNames.value = []
})

async function handleBrowseTargetFolder() {
  const res = await nativeBridge.selectFolder()
  if (res.ok && res.path) {
    targetProject.value = res.path
    store.addProject(res.path)
  }
}

async function handleConfirmClone() {
  errorMsg.value = null

  if (!sourceProject.value) {
    errorMsg.value = t('cloneModal.errorSourceEmpty')
    return
  }
  if (!targetProject.value) {
    errorMsg.value = t('cloneModal.errorTargetEmpty')
    return
  }
  if (sourceProject.value.replace(/\\/g, '/').toLowerCase() === targetProject.value.replace(/\\/g, '/').toLowerCase()) {
    errorMsg.value = t('cloneModal.errorSameProject')
    return
  }
  if (selectedSkillNames.value.length === 0) {
    errorMsg.value = t('cloneModal.errorNoSkillsSelected')
    return
  }

  isCloning.value = true
  try {
    const count = selectedSkillNames.value.length
    await store.cloneSkills(sourceProject.value, targetProject.value, selectedSkillNames.value)
    store.showCloneSkillModal = false
    selectedSkillNames.value = []
    toast.add({
      severity: 'success',
      summary: t('common.success'),
      detail: t('portal.cloneSuccessMsg', { count }),
      life: 3000,
    })
  } catch (err: any) {
    errorMsg.value = err?.message || String(err)
    toast.add({
      severity: 'error',
      summary: t('common.error'),
      detail: err?.message || 'Sao chép thất bại',
      life: 3000,
    })
  } finally {
    isCloning.value = false
  }
}

function handleClose() {
  errorMsg.value = null
  selectedSkillNames.value = []
  store.showCloneSkillModal = false
}
</script>

<template>
  <Dialog
    v-model:visible="store.showCloneSkillModal"
    modal
    :header="t('cloneModal.title')"
    :style="{ width: '520px' }"
    class="p-dialog-custom"
  >
    <div class="space-y-4 py-2">
      <div class="p-3 rounded-xl bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800/60 text-xs text-sky-800 dark:text-sky-300 leading-relaxed flex items-start gap-2">
        <AxIcon name="info" size="xs" class="text-sky-500 mt-0.5 flex-shrink-0" />
        <span>{{ t('cloneModal.banner') }}</span>
      </div>

      <div class="space-y-3">
        <!-- Source project -->
        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            {{ t('cloneModal.sourceProjectLabel') }}
          </label>
          <div class="relative">
            <select
              v-model="sourceProject"
              class="w-full appearance-none text-xs py-2.5 pl-3.5 pr-9 rounded-xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-300 dark:border-[#393B40] text-slate-800 dark:text-[#DFE1E5] focus:outline-none focus:ring-2 focus:ring-[#3574F0]/25 focus:border-[#3574F0] font-medium cursor-pointer shadow-xs transition-all"
            >
              <option value="" disabled>{{ t('cloneModal.sourceProjectPlaceholder') }}</option>
              <option v-for="opt in projectOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
            <AxIcon name="chevron-down" size="xs" class="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 dark:text-[#868A91] pointer-events-none" />
          </div>
        </div>

        <!-- Target project -->
        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            {{ t('cloneModal.targetProjectLabel') }}
          </label>
          <div class="flex gap-2">
            <input
              v-model="targetProject"
              type="text"
              :placeholder="t('cloneModal.targetProjectPlaceholder')"
              class="flex-1 text-xs py-2 px-3 rounded-xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-300 dark:border-[#393B40] text-slate-900 dark:text-[#DFE1E5] focus:outline-none focus:border-emerald-500 font-mono"
            />
            <button
              type="button"
              class="py-2 px-3 text-xs font-semibold rounded-xl border border-slate-300 dark:border-[#393B40] hover:border-slate-400 dark:hover:border-slate-500 bg-white dark:bg-[#1E1F22] text-slate-700 dark:text-[#DFE1E5] flex items-center gap-1.5 transition-all cursor-pointer flex-shrink-0"
              @click="handleBrowseTargetFolder"
            >
              <AxIcon name="folder-open" size="xs" />
              <span>{{ t('scopeModal.browseBtn') }}</span>
            </button>
          </div>
        </div>

        <!-- Skills to clone -->
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">
              {{ t('cloneModal.availableSkillsLabel', { count: availableSkillsToClone.length }) }}
            </label>
            <button
              v-if="availableSkillsToClone.length > 0"
              type="button"
              class="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 hover:underline cursor-pointer"
              @click="selectedSkillNames = selectedSkillNames.length === availableSkillsToClone.length ? [] : [...availableSkillsToClone]"
            >
              {{ selectedSkillNames.length === availableSkillsToClone.length ? t('cloneModal.deselectAll') : t('cloneModal.selectAll') }}
            </button>
          </div>

          <div class="max-h-48 overflow-y-auto space-y-2 p-3 rounded-xl border border-slate-200 dark:border-[#393B40] bg-slate-50 dark:bg-[#1E1F22]/60">
            <div
              v-for="skillName in availableSkillsToClone"
              :key="skillName"
              class="flex items-center justify-between p-2 rounded-lg hover:bg-white dark:hover:bg-[#2B2D30] transition-colors cursor-pointer"
              @click="selectedSkillNames = selectedSkillNames.includes(skillName) ? selectedSkillNames.filter(n => n !== skillName) : [...selectedSkillNames, skillName]"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <div
                  class="w-4 h-4 rounded border flex items-center justify-center transition-all flex-shrink-0"
                  :class="selectedSkillNames.includes(skillName) ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-slate-400 dark:border-slate-600 bg-white dark:bg-[#2B2D30]'"
                >
                  <AxIcon v-if="selectedSkillNames.includes(skillName)" name="check" size="xs" />
                </div>
                <span class="text-xs font-bold text-slate-800 dark:text-slate-200 truncate select-none">
                  {{ skillName }}
                </span>
              </div>
              <span class="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-200 dark:border-emerald-800">
                Project Scope
              </span>
            </div>

            <div v-if="!sourceProject" class="text-xs text-slate-400 text-center py-4">
              {{ t('cloneModal.selectSourcePrompt') }}
            </div>
            <div v-else-if="availableSkillsToClone.length === 0" class="text-xs text-amber-600 dark:text-amber-400 text-center py-4 leading-relaxed font-medium">
              <AxIcon name="alert" size="sm" class="mx-auto mb-1 text-amber-500" />
              {{ t('cloneModal.noAvailableSkills') }}
            </div>
          </div>
        </div>

        <p v-if="errorMsg" class="text-xs text-rose-500 font-semibold">
          {{ errorMsg }}
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <button
          type="button"
          class="py-2 px-3 text-xs font-semibold rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer"
          :disabled="isCloning"
          @click="handleClose"
        >
          {{ t('cloneModal.cancelBtn') }}
        </button>
        <button
          type="button"
          class="py-2 px-4 text-xs font-bold bg-emerald-500 hover:bg-emerald-600 active:bg-emerald-700 text-white rounded-xl shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
          :disabled="selectedSkillNames.length === 0 || isCloning"
          @click="handleConfirmClone"
        >
          <AxIcon v-if="isCloning" name="spinner" size="xs" class="animate-spin" />
          <AxIcon v-else name="copy" size="xs" />
          <span>{{ isCloning ? t('cloneModal.cloningBtn') : t('cloneModal.cloneBtn', { count: selectedSkillNames.length }) }}</span>
        </button>
      </div>
    </template>
  </Dialog>
</template>
