<script setup lang="ts">
import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import { useSkillStore } from '../stores/skillStore'
import { nativeBridge } from '@/services/nativeBridge'
import { useI18n } from '@/i18n'

const store = useSkillStore()
const { t } = useI18n()

const pathInput = ref('')
const errorMsg = ref<string | null>(null)

async function handleBrowse() {
  const res = await nativeBridge.selectFolder()
  if (res.ok && res.path) {
    pathInput.value = res.path
  }
}

function handleConfirm() {
  if (!pathInput.value.trim()) {
    errorMsg.value = t('folderPicker.errorEmpty')
    return
  }
  store.addProject(pathInput.value.trim())
  pathInput.value = ''
  errorMsg.value = null
  store.showFolderPickerModal = false
}

function handleClose() {
  errorMsg.value = null
  pathInput.value = ''
  store.showFolderPickerModal = false
}
</script>

<template>
  <Dialog
    v-model:visible="store.showFolderPickerModal"
    modal
    :header="t('folderPicker.title')"
    :style="{ width: '480px' }"
    class="p-dialog-custom"
  >
    <div class="space-y-4 py-2">
      <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
        {{ t('folderPicker.desc') }}
      </p>

      <div class="space-y-1.5">
        <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300">
          {{ t('folderPicker.pathLabel') }}
        </label>
        <div class="flex gap-2">
          <input
            v-model="pathInput"
            type="text"
            :placeholder="t('folderPicker.pathPlaceholder')"
            class="flex-1 text-xs py-2 px-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:border-emerald-500 font-mono"
            :class="{ '!border-rose-500': !!errorMsg }"
            @input="errorMsg = null"
          />
          <button
            type="button"
            class="py-2 px-3 text-xs font-semibold rounded-xl border border-slate-300 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-600 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 flex items-center gap-1.5 transition-all cursor-pointer flex-shrink-0"
            @click="handleBrowse"
          >
            <i class="pi pi-folder-open text-xs"></i>
            <span>{{ t('folderPicker.browseBtn') }}</span>
          </button>
        </div>
        <p v-if="errorMsg" class="text-[11px] text-rose-500 font-semibold mt-1">
          {{ errorMsg }}
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <button
          type="button"
          class="py-2 px-3 text-xs font-semibold rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer"
          @click="handleClose"
        >
          {{ t('common.cancel') }}
        </button>
        <button
          type="button"
          class="py-2 px-4 text-xs font-bold bg-emerald-500 hover:bg-emerald-600 active:bg-emerald-700 text-white rounded-xl shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1.5 cursor-pointer"
          @click="handleConfirm"
        >
          <i class="pi pi-check text-xs"></i>
          <span>{{ t('folderPicker.confirmBtn') }}</span>
        </button>
      </div>
    </template>
  </Dialog>
</template>
