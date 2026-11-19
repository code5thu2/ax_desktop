<script setup lang="ts">
import Tag from 'primevue/tag'
import { useSkillStore } from '../stores/skillStore'
import { useI18n } from '@/i18n'
import { AxButton, AxIcon } from '@/components/ui'

const emit = defineEmits<{
  (e: 'install-version', version: number): void
}>()

const store = useSkillStore()
const { t } = useI18n()

function isCurrentInstalledVersion(verNumber: number): boolean {
  if (!store.selectedSkill?.installed) return false
  const currVer = store.selectedSkill.installedVersion ?? store.skillDetail?.installedVersion
  if (currVer === undefined || currVer === null) return false
  return verNumber === currVer
}
</script>

<template>
  <div class="space-y-3">
    <div
      v-for="ver in (store.skillVersions || [
        { version: 1, name: 'v1.0.0 (Bản phát hành chính thức)', description: 'Tích hợp đầy đủ tiêu chuẩn bảo mật, Stdio IPC và giao diện IntelliJ New UI.' }
      ])"
      :key="ver.version"
      class="p-4 rounded-xl border border-slate-200/80 dark:border-[#393B40] bg-slate-50 dark:bg-[#1E1F22] flex items-start justify-between gap-4"
    >
      <div>
        <div class="flex items-center gap-2">
          <Tag :value="`v${ver.version}.0.0`" severity="success" class="!text-[11px] !font-bold dark:bg-[#5FAD65]/20 dark:text-[#5FAD65]" />
          <span class="text-xs font-bold text-slate-800 dark:text-[#DFE1E5]">{{ ver.name }}</span>
        </div>
        <p class="text-xs text-slate-500 dark:text-[#868A91] mt-1.5 leading-relaxed">
          {{ ver.description }}
        </p>
      </div>

      <!-- Status indicator or Install Button -->
      <span
        v-if="isCurrentInstalledVersion(ver.version)"
        class="text-xs font-bold text-[#5FAD65] flex items-center gap-1 flex-shrink-0"
      >
        <AxIcon name="check" size="xs" /> {{ t('portal.currentInstalledVersion') }}
      </span>
      <AxButton
        v-else
        variant="secondary"
        size="sm"
        ijIcon="download"
        class="flex-shrink-0"
        @click="emit('install-version', ver.version)"
      >
        <span>{{ store.selectedSkill?.installed ? t('portal.installThisVersion') : t('portal.installSkillBtn') }}</span>
      </AxButton>
    </div>
  </div>
</template>
