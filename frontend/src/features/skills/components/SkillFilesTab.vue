<script setup lang="ts">
import { useSkillStore } from '../stores/skillStore'
import { AxIcon } from '@/components/ui'

const store = useSkillStore()
</script>

<template>
  <div class="space-y-3">
    <div class="text-xs text-slate-500 dark:text-[#868A91] mb-2">
      Danh sách tệp tin đính kèm trong gói Skill:
    </div>

    <div
      v-for="file in (store.skillDetail?.files || [
        { fileName: 'SKILL.md', fileSize: 1536 },
        { fileName: 'metadata.json', fileSize: 412 },
        { fileName: 'handler.ts', fileSize: 2840 }
      ])"
      :key="file.fileName"
      class="p-3.5 rounded-xl border border-slate-200/80 dark:border-[#393B40] bg-slate-50 dark:bg-[#1E1F22] flex items-center justify-between text-xs"
    >
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-[#3574F0]/15 text-[#3574F0] flex items-center justify-center font-bold">
          <AxIcon name="code" size="sm" />
        </div>
        <div>
          <span class="font-mono font-bold text-slate-800 dark:text-[#DFE1E5] block">{{ file.fileName }}</span>
          <span class="text-[10px] text-slate-400 dark:text-[#868A91]">Sẵn sàng thực thi</span>
        </div>
      </div>
      <span class="font-mono text-slate-500 dark:text-[#868A91] text-[11px] px-2 py-0.5 rounded-md bg-white dark:bg-[#2B2D30] border border-slate-200 dark:border-[#43454A]">
        {{ String(file.fileSize) }} bytes
      </span>
    </div>
  </div>
</template>
