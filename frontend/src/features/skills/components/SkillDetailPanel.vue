<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import InputSwitch from 'primevue/inputswitch'
import { useSkillStore } from '../stores/skillStore'
import { useConfirm } from 'primevue/useconfirm'

const store = useSkillStore()
const confirm = useConfirm()

const activeDetailTab = ref<'overview' | 'files' | 'versions'>('overview')

function handleInstall() {
  if (store.selectedSkill) {
    store.pendingInstallSkill = store.selectedSkill
    store.showScopeModal = true
  }
}

function handleToggle(enabled: boolean) {
  if (store.selectedSkill) {
    store.toggleSkill(store.selectedSkill.name, enabled)
  }
}

function handleUninstall() {
  if (!store.selectedSkill) return

  confirm.require({
    message: `Bạn có chắc chắn muốn gỡ cài đặt skill "${store.selectedSkill.name}" không?`,
    header: 'Xác nhận Gỡ cài đặt',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Gỡ cài đặt',
    rejectLabel: 'Hủy',
    accept: () => {
      if (store.selectedSkill) {
        store.uninstallSkill(store.selectedSkill.name)
      }
    },
  })
}
</script>

<template>
  <div class="h-full flex flex-col p-6 overflow-hidden bg-slate-50/50 dark:bg-slate-950/40">
    <div v-if="!store.selectedSkill" class="flex-1 flex flex-col items-center justify-center text-slate-400">
      <i class="pi pi-box text-4xl mb-3 text-slate-300 dark:text-slate-700"></i>
      <p class="text-sm">Chọn một Skill từ danh sách để xem thông tin chi tiết</p>
    </div>

    <div v-else class="h-full flex flex-col space-y-5 overflow-hidden">
      <!-- Detail Header Card -->
      <div class="p-5 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 shadow-sm flex items-start justify-between gap-4">
        <div class="flex items-start gap-4 min-w-0">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-2xl shadow-md shadow-emerald-500/20 flex-shrink-0">
            <i class="pi pi-box"></i>
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h1 class="text-lg font-extrabold text-slate-900 dark:text-white tracking-tight truncate">
                {{ store.selectedSkill.name }}
              </h1>
              <Tag value="APPROVED" severity="success" class="!text-[10px] !py-0.5 !px-2 !font-bold" />
              <Tag :value="store.selectedSkill.scope || 'PUBLIC'" severity="info" class="!text-[10px] !py-0.5 !px-2 !font-bold" />
            </div>

            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2">
              <span>Tác giả: <strong class="text-slate-700 dark:text-slate-300">{{ store.selectedSkill.creatorName }}</strong></span>
              <span>&bull;</span>
              <span>Phiên bản: <strong class="text-slate-700 dark:text-slate-300">v{{ store.selectedSkill.installedVersion || 1 }}</strong></span>
            </p>

            <div class="flex items-center gap-3 mt-2 text-xs text-slate-500">
              <span class="flex items-center gap-1 text-amber-500 font-bold">
                <i class="pi pi-star-fill text-xs"></i>
                {{ store.selectedSkill.avgRating || 5.0 }} ({{ String(store.selectedSkill.ratingCount || 0) }})
              </span>
              <span>&bull;</span>
              <span>{{ String(store.selectedSkill.viewCount || 0) }} lượt xem</span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-3 flex-shrink-0">
          <template v-if="!store.selectedSkill.installed">
            <Button
              type="button"
              label="Cài đặt Skill"
              icon="pi pi-download"
              class="!py-2.5 !px-4 !text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/25 cursor-pointer !rounded-xl"
              @click="handleInstall"
            />
          </template>
          <template v-else>
            <div class="flex items-center gap-2.5 bg-slate-100 dark:bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
              <span class="text-xs font-semibold text-slate-600 dark:text-slate-300">
                {{ store.selectedSkill.enabled ? 'Đang kích hoạt' : 'Đã vô hiệu hóa' }}
              </span>
              <InputSwitch
                :modelValue="store.selectedSkill.enabled"
                @update:modelValue="handleToggle"
              />
            </div>
            <Button
              type="button"
              icon="pi pi-trash"
              label="Gỡ cài đặt"
              variant="outlined"
              severity="danger"
              class="!py-2.5 !px-3 !text-xs !rounded-xl cursor-pointer"
              @click="handleUninstall"
            />
          </template>
        </div>
      </div>

      <!-- Scope Card (If installed) -->
      <div
        v-if="store.selectedSkill.installed"
        class="p-3.5 rounded-2xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-800/60 flex items-center justify-between text-xs"
      >
        <div class="flex items-center gap-2.5">
          <i class="pi pi-info-circle text-emerald-600 dark:text-emerald-400 text-sm"></i>
          <div>
            <span class="font-bold text-slate-900 dark:text-white">
              Phạm vi cài đặt: {{ store.selectedSkill.installScope === 'project' ? 'Theo Dự án (Project)' : 'Toàn cục (Global)' }}
            </span>
            <span class="block text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              Tự động đồng bộ cờ <code class="font-mono bg-white dark:bg-slate-900 px-1 py-0.5 rounded border border-slate-200 dark:border-slate-800">disabledSkills</code> vào file config của AIPRO.
            </span>
          </div>
        </div>
        <Tag
          :value="store.selectedSkill.installScope === 'project' ? 'PROJECT' : 'GLOBAL'"
          severity="success"
          class="!text-[10px] !font-bold"
        />
      </div>

      <!-- Navigation Tabs inside Detail -->
      <div class="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
        <button
          type="button"
          class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
          :class="activeDetailTab === 'overview' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="activeDetailTab = 'overview'"
        >
          <i class="pi pi-file-edit text-xs"></i>
          <span>Tổng quan (Overview)</span>
        </button>

        <button
          type="button"
          class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
          :class="activeDetailTab === 'files' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="activeDetailTab = 'files'"
        >
          <i class="pi pi-folder text-xs"></i>
          <span>Tệp đính kèm (Files)</span>
        </button>

        <button
          type="button"
          class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
          :class="activeDetailTab === 'versions' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="activeDetailTab = 'versions'"
        >
          <i class="pi pi-history text-xs"></i>
          <span>Phiên bản (What's New)</span>
        </button>
      </div>

      <!-- Detail Tab Content Area -->
      <div class="flex-1 overflow-y-auto bg-white dark:bg-slate-900/60 rounded-3xl border border-slate-200/90 dark:border-slate-800 p-6 min-h-0">
        <!-- Overview Tab -->
        <div v-if="activeDetailTab === 'overview'" class="space-y-4">
          <div class="prose dark:prose-invert max-w-none text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
            <h3 class="text-sm font-bold text-slate-900 dark:text-white mb-2">Mô tả Skill</h3>
            <p>{{ store.selectedSkill.description }}</p>

            <h3 class="text-sm font-bold text-slate-900 dark:text-white mt-4 mb-2">Tài liệu đặc tả (SKILL.md)</h3>
            <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 font-mono text-[11px] whitespace-pre-wrap">
              {{ store.skillDetail?.description || `# ${store.selectedSkill.name}\n\nSkill được đóng gói sẵn cho AIPRO Studio với quy trình kiểm thử nghiêm ngặt.` }}
            </div>
          </div>
        </div>

        <!-- Files Tab -->
        <div v-else-if="activeDetailTab === 'files'" class="space-y-2.5">
          <div
            v-for="file in (store.skillDetail?.files || [{ fileName: 'SKILL.md', fileSize: 1024 }])"
            :key="file.fileName"
            class="p-3.5 rounded-xl border border-slate-200/80 dark:border-slate-800 flex items-center justify-between text-xs"
          >
            <div class="flex items-center gap-2.5">
              <i class="pi pi-file text-emerald-500"></i>
              <span class="font-mono font-bold text-slate-800 dark:text-slate-200">{{ file.fileName }}</span>
            </div>
            <span class="font-mono text-slate-400 text-[11px]">{{ String(file.fileSize) }} bytes</span>
          </div>
        </div>

        <!-- Versions Tab -->
        <div v-else-if="activeDetailTab === 'versions'" class="space-y-3">
          <div
            v-for="ver in (store.skillVersions || [{ version: 1, name: 'v1.0.0', description: 'Phiên bản đầu tiên' }])"
            :key="ver.version"
            class="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 flex items-start justify-between gap-4"
          >
            <div>
              <div class="flex items-center gap-2">
                <Tag :value="`v${ver.version}`" severity="success" class="!text-[11px] !font-bold" />
                <span class="text-xs font-bold text-slate-800 dark:text-slate-200">{{ ver.name }}</span>
              </div>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                {{ ver.description }}
              </p>
            </div>

            <Button
              v-if="store.selectedSkill.installedVersion !== ver.version"
              type="button"
              label="Cài bản này"
              icon="pi pi-download"
              variant="outlined"
              class="!py-1.5 !px-3 !text-xs !rounded-xl cursor-pointer flex-shrink-0"
              @click="handleInstall"
            />
            <span v-else class="text-xs font-bold text-emerald-500 flex items-center gap-1 flex-shrink-0">
              <i class="pi pi-check"></i> Bản đang cài
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
