<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import { useSkillStore } from '../stores/skillStore'
import { useI18n } from '@/i18n'

const store = useSkillStore()
const { t } = useI18n()

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
})

const renderedDescription = computed(() => {
  const content = store.skillDetail?.description || store.selectedSkill?.description || ''
  return md.render(content)
})

const skillDisplayVersion = computed(() => {
  if (!store.selectedSkill) return '1.0.0'
  const v = store.selectedSkill.installed
    ? (store.selectedSkill.installedVersion ?? store.skillDetail?.version ?? 1)
    : (store.skillDetail?.version ?? store.skillVersions?.[0]?.version ?? 1)
  return typeof v === 'number' ? `${v}.0.0` : String(v).replace(/^v/, '')
})

const skillStatusText = computed(() => {
  if (!store.selectedSkill?.installed) {
    return t('portal.notInstalled')
  }
  return store.selectedSkill.enabled
    ? t('portal.activeStatus')
    : t('portal.disabledStatus')
})

const skillStatusColorClass = computed(() => {
  if (!store.selectedSkill?.installed) {
    return 'text-[#5FAD65]'
  }
  return store.selectedSkill.enabled
    ? 'text-[#5FAD65] font-bold'
    : 'text-[#E3A83F] font-bold'
})
</script>

<template>
  <div v-if="store.selectedSkill" class="space-y-4">
    <!-- Description Container (Markdown) -->
    <div class="p-5 rounded-xl bg-slate-50/70 dark:bg-[#1E1F22] border border-slate-200/80 dark:border-[#393B40] min-h-[200px]">
      <div
        v-if="renderedDescription"
        class="prose prose-sm dark:prose-invert max-w-none text-slate-700 dark:text-[#CED0D6] leading-relaxed font-normal skill-markdown-body"
        v-html="renderedDescription"
      ></div>
      <div v-else class="text-xs text-slate-400 dark:text-[#868A91] italic">
        {{ t('portal.noDescription') }}
      </div>
    </div>

    <!-- Thông số Kỹ thuật -->
    <div>
      <h3 class="text-sm font-bold text-slate-900 dark:text-[#DFE1E5] mb-2">
        {{ t('portal.specsTitle') }}
      </h3>
      <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-200/80 dark:border-[#393B40] grid grid-cols-2 gap-3 text-[11px]" :class="store.selectedSkill.installed ? 'sm:grid-cols-5' : 'sm:grid-cols-4'">
        <div>
          <span class="text-slate-400 dark:text-[#868A91] block mb-0.5">{{ t('portal.extensionType') }}</span>
          <span class="font-bold text-slate-800 dark:text-[#DFE1E5]">AIPRO Skill</span>
        </div>
        <div v-if="store.selectedSkill.installed">
          <span class="text-slate-400 dark:text-[#868A91] block mb-0.5">{{ t('portal.executionScope') }}</span>
          <span class="font-bold text-slate-800 dark:text-[#DFE1E5]">
            {{ store.selectedSkill.installScope === 'project' ? t('portal.project') : t('portal.global') }}
          </span>
        </div>
        <div>
          <span class="text-slate-400 dark:text-[#868A91] block mb-0.5">{{ t('portal.executionProtocol') }}</span>
          <span class="font-bold text-slate-800 dark:text-[#DFE1E5]">JSON-RPC 2.0 (Stdio IPC)</span>
        </div>
        <div>
          <span class="text-slate-400 dark:text-[#868A91] block mb-0.5">{{ t('portal.versionLabel') }}</span>
          <span class="font-mono text-slate-800 dark:text-[#DFE1E5]">v{{ skillDisplayVersion }}</span>
        </div>
        <div>
          <span class="text-slate-400 dark:text-[#868A91] block mb-0.5">{{ t('portal.statusLabel') }}</span>
          <span :class="skillStatusColorClass">
            {{ skillStatusText }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.skill-markdown-body) {
  font-size: 0.875rem;
  line-height: 1.65;
}

:deep(.skill-markdown-body h1) {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: inherit;
}

:deep(.skill-markdown-body h2) {
  font-size: 1.1rem;
  font-weight: 700;
  margin-top: 0.875rem;
  margin-bottom: 0.375rem;
  color: inherit;
}

:deep(.skill-markdown-body h3) {
  font-size: 0.95rem;
  font-weight: 600;
  margin-top: 0.75rem;
  margin-bottom: 0.25rem;
  color: inherit;
}

:deep(.skill-markdown-body p) {
  margin-bottom: 0.75rem;
}

:deep(.skill-markdown-body ul),
:deep(.skill-markdown-body ol) {
  margin-left: 1.25rem;
  margin-bottom: 0.75rem;
}

:deep(.skill-markdown-body ul) {
  list-style-type: disc;
}

:deep(.skill-markdown-body ol) {
  list-style-type: decimal;
}

:deep(.skill-markdown-body li) {
  margin-bottom: 0.25rem;
}

:deep(.skill-markdown-body pre) {
  background-color: #191A1C;
  color: #DFE1E5;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  font-family: monospace;
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
  border: 1px solid #393B40;
}

:deep(.skill-markdown-body code:not(pre code)) {
  background-color: rgba(53, 116, 240, 0.1);
  color: #3574F0;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-family: monospace;
  font-size: 0.8rem;
}

:deep(.skill-markdown-body blockquote) {
  border-left: 3px solid #3574F0;
  padding-left: 0.75rem;
  margin-left: 0;
  margin-bottom: 0.75rem;
  color: #868A91;
  font-style: italic;
}

:deep(.skill-markdown-body table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0.75rem;
}

:deep(.skill-markdown-body th),
:deep(.skill-markdown-body td) {
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 0.5rem 0.75rem;
  text-align: left;
}

:deep(.skill-markdown-body th) {
  background-color: rgba(148, 163, 184, 0.1);
  font-weight: 600;
}

:deep(.skill-markdown-body a) {
  color: #3574F0;
  text-decoration: underline;
}
</style>
