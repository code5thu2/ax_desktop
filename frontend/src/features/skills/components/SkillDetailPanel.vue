<script setup lang="ts">
import { ref } from 'vue'
import Tag from 'primevue/tag'
import { useSkillStore } from '../stores/skillStore'
import { useConfirm } from 'primevue/useconfirm'
import { useI18n } from '@/i18n'
import { AxIcon } from '@/components/ui'

import SkillDetailHeader from './SkillDetailHeader.vue'
import SkillOverviewTab from './SkillOverviewTab.vue'
import SkillToolsTab from './SkillToolsTab.vue'
import SkillFilesTab from './SkillFilesTab.vue'
import SkillVersionsTab from './SkillVersionsTab.vue'

const store = useSkillStore()
const confirm = useConfirm()
const { t } = useI18n()

const activeDetailTab = ref<'overview' | 'tools' | 'files' | 'versions'>('overview')

function handleInstall() {
  if (store.selectedSkill) {
    store.pendingChangeScopeFrom = null
    const latestVer = store.skillVersions?.[0]?.version || store.skillDetail?.version || 1
    store.pendingInstallSkill = { ...store.selectedSkill, installedVersion: latestVer }
    store.showScopeModal = true
  }
}

function handleChangeScope() {
  if (store.selectedSkill) {
    const latestVer = store.selectedSkill.installedVersion || store.skillVersions?.[0]?.version || store.skillDetail?.version || 1
    store.pendingInstallSkill = { ...store.selectedSkill, installedVersion: latestVer }
    store.pendingChangeScopeFrom = {
      scope: (store.selectedSkill.installScope as 'global' | 'project') || (store.selectedSkill.scope?.toLowerCase() === 'project' ? 'project' : 'global'),
      projectPath: store.selectedSkill.installedProjects?.[0]
    }
    store.showScopeModal = true
  }
}

function handleInstallVersion(version: number) {
  if (store.selectedSkill) {
    store.pendingChangeScopeFrom = null
    store.pendingInstallSkill = { ...store.selectedSkill, installedVersion: version }
    store.showScopeModal = true
  }
}

function handleToggle(enabled: boolean) {
  if (store.selectedSkill) {
    store.toggleSkill(store.selectedSkill.name, enabled, store.selectedSkill.installedProjects?.[0])
  }
}

function handleUninstall() {
  if (!store.selectedSkill) return

  confirm.require({
    message: t('portal.confirmUninstallMsg', { name: store.selectedSkill.name }),
    header: t('portal.confirmUninstallTitle'),
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: t('portal.uninstallBtn'),
    rejectLabel: t('common.cancel'),
    accept: () => {
      if (store.selectedSkill) {
        store.uninstallSkill(store.selectedSkill.name, store.selectedSkill.installedProjects?.[0])
      }
    },
  })
}
</script>

<template>
  <div class="h-full flex flex-col p-6 overflow-hidden bg-slate-50/50 dark:bg-[#1E1F22]">
    <!-- Empty State -->
    <div v-if="!store.selectedSkill" class="flex-1 flex flex-col items-center justify-center text-slate-400 dark:text-[#868A91]">
      <div class="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-[#2B2D30] border border-slate-200 dark:border-[#393B40] flex items-center justify-center text-slate-400 dark:text-[#868A91] mb-3 shadow-sm">
        <AxIcon name="puzzle" size="lg" />
      </div>
      <p class="text-sm font-semibold text-slate-700 dark:text-[#DFE1E5]">{{ t('portal.selectSkillHint') }}</p>
      <p class="text-xs text-slate-400 dark:text-[#868A91] mt-1">Chọn một skill từ danh mục bên trái để xem đặc tả chi tiết</p>
    </div>

    <!-- Active Skill Content -->
    <div v-else class="h-full flex flex-col space-y-4 overflow-hidden">
      <!-- 1. HERO HEADER CARD -->
      <SkillDetailHeader
        @install="handleInstall"
        @change-scope="handleChangeScope"
        @toggle="handleToggle"
        @uninstall="handleUninstall"
      />

      <!-- 2. SCOPE BANNER -->
      <div
        v-if="store.selectedSkill.installed"
        class="p-3.5 rounded-xl bg-[#3574F0]/10 dark:bg-[#2E436E]/30 border border-[#3574F0]/25 flex items-center justify-between text-xs flex-shrink-0"
      >
        <div class="flex items-center gap-2.5">
          <AxIcon name="folder" size="sm" class="text-[#3574F0] dark:text-[#56A8F5]" />
          <div>
            <span class="font-bold text-slate-900 dark:text-[#DFE1E5]">
              {{ t('portal.scopeInfoTitle') }} {{ store.selectedSkill.installScope === 'project' ? t('portal.project') : t('portal.global') }}
            </span>
            <span class="block text-[11px] text-slate-500 dark:text-[#868A91] mt-0.5">
              {{ store.selectedSkill.installScope === 'project' ? 'Skill được đóng gói độc lập trong thư mục dự án và nạp tự động khi mở Workspace.' : t('portal.scopeInfoDesc') }}
            </span>
          </div>
        </div>
        <Tag
          :value="store.selectedSkill.installScope === 'project' ? 'PROJECT SCOPED' : 'GLOBAL SCOPED'"
          severity="success"
          class="!text-[10px] !font-bold dark:bg-[#5FAD65]/20 dark:text-[#5FAD65]"
        />
      </div>

      <!-- 3. DETAIL TABS SWITCHER -->
      <div class="flex items-center gap-2 border-b border-slate-200 dark:border-[#393B40] pb-2 flex-shrink-0">
        <button
          type="button"
          class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
          :class="activeDetailTab === 'overview' 
            ? 'bg-white dark:bg-[#2B2D30] text-[#3574F0] dark:text-[#56A8F5] shadow-xs border border-slate-200 dark:border-[#393B40]' 
            : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
          @click="activeDetailTab = 'overview'"
        >
          <AxIcon name="code" size="xs" />
          <span>{{ t('portal.tabOverview') }}</span>
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
          :class="activeDetailTab === 'tools' 
            ? 'bg-white dark:bg-[#2B2D30] text-[#3574F0] dark:text-[#56A8F5] shadow-xs border border-slate-200 dark:border-[#393B40]' 
            : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
          @click="activeDetailTab = 'tools'"
        >
          <AxIcon name="terminal" size="xs" />
          <span>Công cụ &amp; Lệnh</span>
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
          :class="activeDetailTab === 'files' 
            ? 'bg-white dark:bg-[#2B2D30] text-[#3574F0] dark:text-[#56A8F5] shadow-xs border border-slate-200 dark:border-[#393B40]' 
            : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
          @click="activeDetailTab = 'files'"
        >
          <AxIcon name="folder" size="xs" />
          <span>{{ t('portal.tabFiles') }}</span>
          <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 dark:bg-[#1E1F22] text-slate-500 dark:text-[#868A91]">{{ (store.skillDetail?.files?.length || 2) }}</span>
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
          :class="activeDetailTab === 'versions' 
            ? 'bg-white dark:bg-[#2B2D30] text-[#3574F0] dark:text-[#56A8F5] shadow-xs border border-slate-200 dark:border-[#393B40]' 
            : 'text-slate-500 hover:text-slate-800 dark:hover:text-[#DFE1E5]'"
          @click="activeDetailTab = 'versions'"
        >
          <AxIcon name="branches" size="xs" />
          <span>{{ t('portal.tabVersions') }}</span>
        </button>
      </div>

      <!-- 4. TAB CONTENT CONTAINER -->
      <div class="flex-1 overflow-y-auto bg-white dark:bg-[#2B2D30] rounded-2xl border border-slate-200/90 dark:border-[#393B40] p-5 min-h-0 space-y-5">
        <SkillOverviewTab v-if="activeDetailTab === 'overview'" />
        <SkillToolsTab v-else-if="activeDetailTab === 'tools'" />
        <SkillFilesTab v-else-if="activeDetailTab === 'files'" />
        <SkillVersionsTab v-else-if="activeDetailTab === 'versions'" @install-version="handleInstallVersion" />
      </div>
    </div>
  </div>
</template>
