<script setup lang="ts">
import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import { usePluginStore } from '../../stores/pluginStore'
import { useI18n } from '@/i18n'
import { AxButton, AxInput } from '@/components/ui'

const emit = defineEmits<{
  (e: 'success', name: string, count: number): void
}>()

const pluginStore = usePluginStore()
const { t } = useI18n()

const uploadFile = ref<File | null>(null)
const uploadName = ref('')
const uploadDesc = ref('')
const isUploading = ref(false)
const uploadError = ref('')

function onUploadFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    uploadFile.value = input.files[0]
  }
}

async function handleUploadSubmit() {
  if (!uploadFile.value) return
  isUploading.value = true
  uploadError.value = ''
  try {
    const res = await pluginStore.uploadCustomMCP(
      uploadFile.value,
      uploadName.value.trim() || undefined,
      uploadDesc.value.trim() || undefined
    )
    pluginStore.showUploadModal = false
    const name = res.name
    const count = res.tools_count
    uploadFile.value = null
    uploadName.value = ''
    uploadDesc.value = ''
    emit('success', name, count)
  } catch (err: any) {
    uploadError.value = err.message || 'Lỗi upload code'
  } finally {
    isUploading.value = false
  }
}
</script>

<template>
  <Dialog
    v-model:visible="pluginStore.showUploadModal"
    modal
    :header="t('mcpStudio.uploadModalTitle')"
    :style="{ width: '540px' }"
    class="p-dialog-custom"
  >
    <div class="space-y-3.5 text-xs py-2">
      <p class="text-slate-500 dark:text-[#868A91] leading-relaxed">
        {{ t('mcpStudio.uploadModalTitle') }}
      </p>

      <div v-if="uploadError" class="p-3 rounded-lg bg-[#FA5252]/10 border border-[#FA5252]/30 text-[#FA5252]">
        <i class="pi pi-exclamation-triangle mr-1"></i>
        <span>{{ uploadError }}</span>
      </div>

      <div>
        <label class="block font-bold mb-1 text-slate-700 dark:text-[#DFE1E5]">
          Chọn Tệp (.py / .zip) <span class="text-[#FA5252]">*</span>
        </label>
        <input
          type="file"
          accept=".py,.zip"
          class="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-[#3574F0]/15 file:text-[#3574F0] hover:file:bg-[#3574F0]/25 cursor-pointer dark:bg-[#1E1F22] p-2 rounded-lg border border-slate-200 dark:border-[#393B40]"
          @change="onUploadFileChange"
        />
      </div>

      <div>
        <label class="block font-bold mb-1 text-slate-700 dark:text-[#DFE1E5]">Tên Hiển Thị</label>
        <AxInput
          v-model="uploadName"
          placeholder="VD: Custom File Server"
        />
      </div>

      <div>
        <label class="block font-bold mb-1 text-slate-700 dark:text-[#DFE1E5]">Mô Tả</label>
        <AxInput
          v-model="uploadDesc"
          placeholder="Mô tả công cụ..."
        />
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <AxButton
          variant="ghost"
          size="sm"
          :disabled="isUploading"
          @click="pluginStore.showUploadModal = false"
        >
          {{ t('common.cancel') }}
        </AxButton>
        <AxButton
          variant="primary"
          size="sm"
          ijIcon="download"
          :loading="isUploading"
          :disabled="!uploadFile || isUploading"
          @click="handleUploadSubmit"
        >
          <span>{{ isUploading ? t('mcpStudio.uploading') : t('mcpStudio.submitUploadBtn') }}</span>
        </AxButton>
      </div>
    </template>
  </Dialog>
</template>
