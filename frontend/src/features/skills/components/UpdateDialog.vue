<script setup lang="ts">
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { useSkillStore } from '../stores/skillStore'

const store = useSkillStore()

function handleOpenRelease() {
  if (store.availableUpdate?.downloadUrl) {
    window.open(store.availableUpdate.downloadUrl, '_blank')
  } else {
    window.open('https://github.com/code5thu2/ax_desktop/releases', '_blank')
  }
  store.showUpdateDialog = false
}
</script>

<template>
  <Dialog
    v-model:visible="store.showUpdateDialog"
    modal
    header="Bản cập nhật mới sẵn sàng"
    :style="{ width: '450px' }"
  >
    <div class="space-y-4 py-2">
      <div class="flex items-center gap-3.5 p-3.5 rounded-2xl bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800/60">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-sky-500/20 font-bold">
          <i class="pi pi-cloud-download text-2xl"></i>
        </div>
        <div>
          <h4 class="text-sm font-bold text-slate-900 dark:text-white">
            AX Desktop {{ store.availableUpdate?.latestVersion || 'v1.1.0' }}
          </h4>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            Phiên bản hiện tại: {{ store.availableUpdate?.currentVersion || 'v1.0.0' }}
          </p>
        </div>
      </div>

      <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
        Một phiên bản mới của AX Desktop đã được phát hành trên GitHub (<code class="font-mono text-emerald-600 dark:text-emerald-400">code5thu2/ax_desktop</code>) với nhiều cải tiến hiệu năng và tính năng mới.
      </p>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <Button
          type="button"
          label="Để sau"
          variant="text"
          class="!rounded-xl !text-xs cursor-pointer"
          @click="store.showUpdateDialog = false"
        />
        <Button
          type="button"
          label="Tải về Cập nhật"
          icon="pi pi-download"
          class="!rounded-xl !text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/20 cursor-pointer"
          @click="handleOpenRelease"
        />
      </div>
    </template>
  </Dialog>
</template>
