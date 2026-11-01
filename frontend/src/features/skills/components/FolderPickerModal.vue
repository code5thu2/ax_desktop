<script setup lang="ts">
import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { useSkillStore } from '../stores/skillStore'
import { nativeBridge } from '@/services/nativeBridge'

const store = useSkillStore()
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
    errorMsg.value = 'Vui lòng chọn hoặc nhập đường dẫn thư mục'
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
    header="Thêm Thư mục Dự án"
    :style="{ width: '460px' }"
  >
    <div class="space-y-4 py-2">
      <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
        Chọn thư mục dự án chứa workspace code của bạn để quản lý các Skill cục bộ trong thư mục <code class="font-mono text-[11px] bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">.aipro/skills</code>.
      </p>

      <div class="space-y-1.5">
        <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300">
          Đường dẫn thư mục dự án
        </label>
        <div class="flex gap-2">
          <InputText
            v-model="pathInput"
            placeholder="D:/AI_Projects/MyNewApp"
            class="flex-1 !rounded-xl !text-xs"
            :invalid="!!errorMsg"
            @input="errorMsg = null"
          />
          <Button
            type="button"
            icon="pi pi-folder-open"
            label="Chọn thư mục"
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
          label="Hủy"
          variant="text"
          class="!rounded-xl !text-xs cursor-pointer"
          @click="handleClose"
        />
        <Button
          type="button"
          label="Thêm Dự án"
          icon="pi pi-plus"
          class="!rounded-xl !text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/20 cursor-pointer"
          @click="handleConfirm"
        />
      </div>
    </template>
  </Dialog>
</template>
