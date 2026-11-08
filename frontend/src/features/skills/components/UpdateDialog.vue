<script setup lang="ts">
import Dialog from 'primevue/dialog'
import { computed } from 'vue'
import { useSkillStore } from '../stores/skillStore'
import { useI18n } from '@/i18n'

const store = useSkillStore()
const { t } = useI18n()

const formattedProgressSize = computed(() => {
  if (!store.updateBytesTotal) return ''
  const dlMb = (store.updateBytesDownloaded / (1024 * 1024)).toFixed(1)
  const totMb = (store.updateBytesTotal / (1024 * 1024)).toFixed(1)
  return `${dlMb} MB / ${totMb} MB`
})

function handleLater() {
  if (store.isUpdating) return
  store.showUpdateDialog = false
}

function handleStartUpdate() {
  store.applyAutoUpdate()
}
</script>

<template>
  <Dialog
    v-model:visible="store.showUpdateDialog"
    modal
    :closable="!store.isUpdating"
    :dismissable-mask="!store.isUpdating"
    :header="t('updateModal.title')"
    :style="{ width: '480px' }"
    class="p-dialog-custom"
  >
    <div class="space-y-4 py-2">
      <!-- Release Version Banner -->
      <div class="flex items-center gap-3.5 p-3.5 rounded-2xl bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800/60">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-sky-500/20 font-bold flex-shrink-0">
          <i :class="store.isUpdating ? 'pi pi-spin pi-cog text-2xl' : 'pi pi-cloud-download text-2xl'"></i>
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <h4 class="text-sm font-bold text-slate-900 dark:text-white truncate">
              AX Desktop {{ store.availableUpdate?.latestVersion || 'v1.1.0' }}
            </h4>
            <span class="px-2 py-0.5 text-[10px] font-bold bg-sky-500/10 text-sky-600 dark:text-sky-400 rounded-md border border-sky-500/20">
              Mới nhất
            </span>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            {{ t('updateModal.currentVersion', { version: store.availableUpdate?.currentVersion || 'v1.0.0' }) }}
          </p>
        </div>
      </div>

      <!-- Description or Release Notes -->
      <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
        {{ store.availableUpdate?.releaseNotes || t('updateModal.desc') }}
      </p>

      <!-- Active Download & Installation Progress -->
      <div v-if="store.isUpdating" class="p-3.5 rounded-xl bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-2.5">
        <div class="flex items-center justify-between text-xs">
          <span class="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-2">
            <i class="pi pi-spin pi-spinner text-sky-500"></i>
            {{ store.updateStatusText || t('updateModal.updating') }}
          </span>
          <span class="font-bold text-sky-600 dark:text-sky-400 tabular-nums">
            {{ store.updateProgress }}%
          </span>
        </div>

        <div class="h-2 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-sky-500 via-indigo-500 to-emerald-500 transition-all duration-300 rounded-full"
            :style="{ width: `${store.updateProgress}%` }"
          ></div>
        </div>

        <div v-if="formattedProgressSize" class="text-right text-[11px] text-slate-400 dark:text-slate-500 tabular-nums">
          {{ formattedProgressSize }}
        </div>
      </div>

      <!-- Error Message if update fails -->
      <div
        v-if="store.updateError"
        class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 flex items-start gap-2.5 text-xs text-rose-700 dark:text-rose-300"
      >
        <i class="pi pi-exclamation-circle text-base flex-shrink-0 mt-0.5"></i>
        <div class="flex-1">
          <p class="font-semibold">Cập nhật không thành công</p>
          <p class="mt-0.5 opacity-90">{{ store.updateError }}</p>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <!-- Error State Actions -->
        <template v-if="store.updateError">
          <button
            type="button"
            class="py-2 px-3 text-xs font-semibold rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer"
            @click="store.showUpdateDialog = false"
          >
            {{ t('updateModal.closeBtn') }}
          </button>
          <button
            type="button"
            class="py-2 px-4 text-xs font-bold bg-sky-500 hover:bg-sky-600 active:bg-sky-700 text-white rounded-xl shadow-md shadow-sky-500/20 transition-all flex items-center gap-1.5 cursor-pointer"
            @click="handleStartUpdate"
          >
            <i class="pi pi-refresh text-xs"></i>
            <span>{{ t('updateModal.retryBtn') }}</span>
          </button>
        </template>

        <!-- Updating State Actions -->
        <template v-else-if="store.isUpdating">
          <button
            type="button"
            disabled
            class="py-2 px-4 text-xs font-bold bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400 rounded-xl flex items-center gap-2 cursor-not-allowed opacity-80"
          >
            <i class="pi pi-spin pi-spinner text-xs"></i>
            <span>{{ store.updateProgress >= 100 ? t('updateModal.installing') : t('updateModal.updating') }}</span>
          </button>
        </template>

        <!-- Normal Prompt Actions -->
        <template v-else>
          <button
            type="button"
            class="py-2 px-3 text-xs font-semibold rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer"
            @click="handleLater"
          >
            {{ t('updateModal.laterBtn') }}
          </button>
          <button
            type="button"
            class="py-2 px-4 text-xs font-bold bg-emerald-500 hover:bg-emerald-600 active:bg-emerald-700 text-white rounded-xl shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1.5 cursor-pointer"
            @click="handleStartUpdate"
          >
            <i class="pi pi-cloud-download text-xs"></i>
            <span>{{ t('updateModal.downloadBtn') }}</span>
          </button>
        </template>
      </div>
    </template>
  </Dialog>
</template>
