<script setup lang="ts">
import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
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
    :style="{ width: '460px' }"
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
          <InputText
            v-model="pathInput"
            :placeholder="t('folderPicker.pathPlaceholder')"
            class="flex-1 !rounded-xl !text-xs"
            :invalid="!!errorMsg"
            @input="errorMsg = null"
          />
          <Button
            type="button"
            icon="pi pi-folder-open"
            :label="t('folderPicker.browseBtn')"
            variant="outlined"
            class="!rounded-xl !text-xs cursor-pointer flex-shrink-0"
            @click="handleBrowse"
          />
        </div>
        <p v-if="errorMsg" class="text-[11px] text-rose-500 font-semibold mt-1">
          {{ errorMsg }}
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <Button
          type="button"
          :label="t('folderPicker.cancelBtn')"
          variant="text"
          class="!rounded-xl !text-xs cursor-pointer"
          @click="handleClose"
        />
        <Button
          type="button"
          :label="t('folderPicker.addBtn')"
          icon="pi pi-plus"
          class="!rounded-xl !text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/20 cursor-pointer"
          @click="handleConfirm"
        />
      </div>
    </template>
  </Dialog>
</template>
