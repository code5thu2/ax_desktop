<script setup lang="ts">
import { computed } from 'vue'
import Tag from 'primevue/tag'
import { useSkillStore } from '../stores/skillStore'
import { useI18n } from '@/i18n'
import { AxButton, AxIcon } from '@/components/ui'

const emit = defineEmits<{
  (e: 'install'): void
  (e: 'change-scope'): void
  (e: 'toggle', enabled: boolean): void
  (e: 'uninstall'): void
}>()

const store = useSkillStore()
const { t, locale } = useI18n()

const skillUpdatedDate = computed(() => {
  const d = store.selectedSkill?.createdAt
  if (!d) return t('portal.today')
  try {
    const parsed = new Date(d)
    if (isNaN(parsed.getTime())) return String(d)
    const loc = locale.value === 'vi' ? 'vi-VN' : (locale.value === 'ko' ? 'ko-KR' : 'en-US')
    return parsed.toLocaleDateString(loc, { month: '2-digit', year: 'numeric' })
  } catch {
    return t('portal.today')
  }
})
</script>

<template>
  <div
    v-if="store.selectedSkill"
    class="p-5 rounded-2xl bg-white dark:bg-[#2B2D30] border border-slate-200/90 dark:border-[#393B40] shadow-sm flex items-start justify-between gap-5 flex-shrink-0"
  >
    <div class="flex items-start gap-4 min-w-0">
      <!-- IntelliJ Brand Icon -->
      <div class="w-12 h-12 rounded-xl bg-[#3574F0]/15 dark:bg-[#3574F0]/25 text-[#3574F0] flex items-center justify-center font-bold text-xl shadow-sm border border-[#3574F0]/30 flex-shrink-0">
        <AxIcon name="puzzle" size="lg" />
      </div>

      <div class="min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <h1 class="text-base font-extrabold text-slate-900 dark:text-[#DFE1E5] tracking-tight truncate">
            {{ store.selectedSkill.name }}
          </h1>
          <Tag value="APPROVED" severity="success" class="!text-[10px] !py-0.5 !px-2 !font-bold dark:bg-[#5FAD65]/20 dark:text-[#5FAD65]" />
          <Tag value="SANDBOXED" class="!text-[10px] !py-0.5 !px-2 !font-bold dark:bg-[#393B40] dark:text-[#DFE1E5]" />
          <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-slate-100 dark:bg-[#1E1F22] text-slate-600 dark:text-[#868A91] border border-slate-200 dark:border-[#43454A]">
            v{{ (store.selectedSkill.installed ? store.selectedSkill.installedVersion : (store.skillDetail?.version || store.skillVersions?.[0]?.version)) || 1 }}.0.0
          </span>
        </div>

        <!-- Author & Metadata Line -->
        <p class="text-xs text-slate-500 dark:text-[#868A91] mt-1 flex items-center gap-2 flex-wrap">
          <span>{{ t('portal.authorLabel') }}: <strong class="text-slate-700 dark:text-[#DFE1E5] font-semibold">{{ store.selectedSkill.creatorName }}</strong></span>
          <span>&bull;</span>
          <span>{{ t('portal.updatedDate') }}: <strong class="text-slate-700 dark:text-[#DFE1E5] font-semibold">{{ skillUpdatedDate }}</strong></span>
        </p>

        <div class="flex items-center gap-3 mt-2 text-xs text-slate-500 dark:text-[#868A91]">
          <span class="flex items-center gap-1 text-[#E3A83F] font-bold">
            <AxIcon name="star" size="xs" class="fill-[#E3A83F] text-[#E3A83F]" />
            {{ store.selectedSkill.avgRating || 5.0 }} ({{ String(store.selectedSkill.ratingCount || 1) }})
          </span>
          <span>&bull;</span>
          <span>{{ String(store.selectedSkill.viewCount || 100) }} {{ t('portal.views') }}</span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center gap-2.5 flex-shrink-0">
      <AxButton
        v-if="!store.selectedSkill.installed"
        variant="primary"
        size="md"
        ijIcon="download"
        @click="emit('install')"
      >
        <span>{{ t('portal.installSkillBtn') }}</span>
      </AxButton>

      <template v-else>
        <!-- Toggle Switch Pill -->
        <div class="flex items-center gap-2 bg-slate-100 dark:bg-[#1E1F22] px-3 py-1.5 rounded-lg border border-slate-200 dark:border-[#43454A]">
          <span class="flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-[#DFE1E5]">
            <span class="w-2 h-2 rounded-full" :class="store.selectedSkill.enabled ? 'bg-[#5FAD65] shadow-[0_0_6px_rgba(95,173,101,0.8)]' : 'bg-slate-500'"></span>
            {{ store.selectedSkill.enabled ? t('portal.activeStatus') : t('portal.disabledStatus') }}
          </span>
          <button
            type="button"
            role="switch"
            :aria-checked="store.selectedSkill.enabled"
            class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
            :class="store.selectedSkill.enabled ? 'bg-[#5FAD65]' : 'bg-slate-300 dark:bg-[#43454A]'"
            @click="emit('toggle', !store.selectedSkill.enabled)"
          >
            <span
              class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out"
              :class="store.selectedSkill.enabled ? 'translate-x-4' : 'translate-x-0'"
            />
          </button>
        </div>

        <!-- Re-scope / Install to other workspace -->
        <AxButton
          variant="secondary"
          size="md"
          ijIcon="settings"
          :title="t('portal.changeScopeTitle')"
          @click="emit('change-scope')"
        >
          <span>{{ t('portal.changeScope') }}</span>
        </AxButton>

        <!-- Uninstall Button -->
        <AxButton
          variant="danger"
          size="md"
          ijIcon="trash"
          @click="emit('uninstall')"
        >
          <span>{{ t('portal.uninstallBtn') }}</span>
        </AxButton>
      </template>
    </div>
  </div>
</template>
