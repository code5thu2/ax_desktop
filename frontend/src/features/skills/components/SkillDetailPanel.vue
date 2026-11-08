<script setup lang="ts">
import { ref, computed } from 'vue'
import Tag from 'primevue/tag'
import MarkdownIt from 'markdown-it'
import { useSkillStore } from '../stores/skillStore'
import { useConfirm } from 'primevue/useconfirm'
import { useI18n } from '@/i18n'

const store = useSkillStore()
const confirm = useConfirm()
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
    return 'text-emerald-500 dark:text-emerald-400'
  }
  return store.selectedSkill.enabled
    ? 'text-emerald-500 dark:text-emerald-400 font-bold'
    : 'text-amber-500 dark:text-amber-400 font-bold'
})

const activeDetailTab = ref<'overview' | 'tools' | 'files' | 'versions'>('overview')

function handleInstall() {
  if (store.selectedSkill) {
    const latestVer = store.skillVersions?.[0]?.version || store.skillDetail?.version || 1
    store.pendingInstallSkill = { ...store.selectedSkill, installedVersion: latestVer }
    store.showScopeModal = true
  }
}

function isCurrentInstalledVersion(verNumber: number): boolean {
  if (!store.selectedSkill?.installed) return false
  const currVer = store.selectedSkill.installedVersion ?? store.skillDetail?.installedVersion
  if (currVer === undefined || currVer === null) return false
  return verNumber === currVer
}

function handleInstallVersion(version: number) {
  if (store.selectedSkill) {
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

// Sample tools tailored to the skill
const providedTools = computed(() => {
  const name = store.selectedSkill?.name || 'Skill'
  if (name.includes('Code')) {
    return [
      { name: 'analyze_syntax_ast', desc: 'Phân tích cây cú pháp trừu tượng (AST) của file nguồn TypeScript/Rust/Python.', params: 'filePath: string, depth?: number' },
      { name: 'generate_unit_tests', desc: 'Sinh mã kiểm thử tự động kèm mock fixtures theo tiêu chuẩn Vitest / Cargo test.', params: 'targetFile: string, framework: string' },
      { name: 'check_lint_diagnostics', desc: 'Kiểm tra chẩn đoán lỗi tĩnh và cảnh báo bảo mật thời gian thực.', params: 'workspaceDir: string' }
    ]
  }
  if (name.includes('Database') || name.includes('Query')) {
    return [
      { name: 'inspect_tables_schema', desc: 'Trích xuất cấu trúc bảng, khóa chính, khóa ngoại và chỉ mục indexes.', params: 'schemaName?: string, includeViews?: boolean' },
      { name: 'explain_query_plan', desc: 'Phân tích chi phí thực thi câu lệnh SQL qua EXPLAIN ANALYZE.', params: 'sql: string, format?: "json" | "text"' },
      { name: 'generate_migration_script', desc: 'Tự động tạo file migration tương thích PostgreSQL / MySQL / SQLite.', params: 'sourceTable: string, targetChanges: object' }
    ]
  }
  if (name.includes('Legal') || name.includes('Document')) {
    return [
      { name: 'search_statutes_database', desc: 'Tra cứu kho văn bản quy phạm pháp luật, nghị định, thông tư chính phủ.', params: 'query: string, lawType?: string, year?: number' },
      { name: 'verify_legal_validity', desc: 'Xác minh hiệu lực pháp lý (còn hiệu lực, hết hiệu lực, bị thay thế).', params: 'documentId: string' },
      { name: 'compare_contract_clauses', desc: 'So sánh các điều khoản hợp đồng đối chiếu với luật thương mại hiện hành.', params: 'clauseText: string, jurisdiction: string' }
    ]
  }
  return [
    { name: 'execute_core_routine', desc: 'Thực thi routine nghiệp vụ chính của Skill trong môi trường sandbox.', params: 'payload: any' },
    { name: 'get_environment_status', desc: 'Kiểm tra trạng thái kết nối và tài nguyên của runtime.', params: 'detailed?: boolean' }
  ]
})
</script>

<template>
  <div class="h-full flex flex-col p-6 overflow-hidden bg-slate-50/50 dark:bg-slate-950/40">
    <!-- Empty State -->
    <div v-if="!store.selectedSkill" class="flex-1 flex flex-col items-center justify-center text-slate-400">
      <div class="w-16 h-16 rounded-3xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-300 dark:text-slate-600 mb-4 shadow-inner">
        <i class="pi pi-box text-3xl"></i>
      </div>
      <p class="text-sm font-semibold text-slate-700 dark:text-slate-300">{{ t('portal.selectSkillHint') }}</p>
      <p class="text-xs text-slate-400 mt-1">Chọn một skill từ danh mục bên trái để xem đặc tả chi tiết</p>
    </div>

    <!-- Active Skill Content -->
    <div v-else class="h-full flex flex-col space-y-4 overflow-hidden">
      <!-- 1. HERO HEADER CARD -->
      <div class="p-5 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 shadow-sm flex items-start justify-between gap-5 flex-shrink-0">
        <div class="flex items-start gap-4 min-w-0">
          <!-- Radiant Brand Icon -->
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 flex items-center justify-center text-white font-bold text-2xl shadow-xl shadow-emerald-500/25 ring-4 ring-emerald-500/10 flex-shrink-0">
            <i class="pi pi-box"></i>
          </div>

          <div class="min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h1 class="text-lg font-black text-slate-900 dark:text-white tracking-tight truncate">
                {{ store.selectedSkill.name }}
              </h1>
              <Tag value="APPROVED" severity="success" class="!text-[10px] !py-0.5 !px-2 !font-bold" />
              <Tag value="SANDBOXED" severity="info" class="!text-[10px] !py-0.5 !px-2 !font-bold" />
              <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                v{{ (store.selectedSkill.installed ? store.selectedSkill.installedVersion : (store.skillDetail?.version || store.skillVersions?.[0]?.version)) || 1 }}.0.0
              </span>
            </div>

            <!-- Author & Metadata Line -->
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2 flex-wrap">
              <span>{{ t('portal.authorLabel') }}: <strong class="text-slate-700 dark:text-slate-200 font-semibold">{{ store.selectedSkill.creatorName }}</strong></span>
              <span>&bull;</span>
              <span>Cập nhật: <strong class="text-slate-700 dark:text-slate-200 font-semibold">Tháng 11/2026</strong></span>
            </p>

            <div class="flex items-center gap-3 mt-2 text-xs text-slate-500">
              <span class="flex items-center gap-1 text-amber-500 font-bold">
                <i class="pi pi-star-fill text-xs"></i>
                {{ store.selectedSkill.avgRating || 5.0 }} ({{ String(store.selectedSkill.ratingCount || 1) }})
              </span>
              <span>&bull;</span>
              <span>{{ String(store.selectedSkill.viewCount || 100) }} {{ t('portal.views') }}</span>
              <span>&bull;</span>
              <span class="text-emerald-500 font-semibold flex items-center gap-1">
                <i class="pi pi-shield text-[10px]"></i> 100% Offline-Safe
              </span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-2.5 flex-shrink-0">
          <button
            v-if="!store.selectedSkill.installed"
            type="button"
            class="py-2.5 px-5 text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white rounded-xl shadow-md shadow-emerald-500/25 transition-all flex items-center gap-2 cursor-pointer active:scale-95"
            @click="handleInstall"
          >
            <i class="pi pi-download text-xs"></i>
            <span>{{ t('portal.installSkillBtn') }}</span>
          </button>

          <template v-else>
            <!-- Toggle Switch Pill -->
            <div class="flex items-center gap-2.5 bg-slate-100 dark:bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
              <span class="flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-200">
                <span class="w-2 h-2 rounded-full" :class="store.selectedSkill.enabled ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'"></span>
                {{ store.selectedSkill.enabled ? t('portal.activeStatus') : t('portal.disabledStatus') }}
              </span>
              <button
                type="button"
                role="switch"
                :aria-checked="store.selectedSkill.enabled"
                class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
                :class="store.selectedSkill.enabled ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-slate-700'"
                @click="handleToggle(!store.selectedSkill.enabled)"
              >
                <span
                  class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out"
                  :class="store.selectedSkill.enabled ? 'translate-x-4' : 'translate-x-0'"
                />
              </button>
            </div>

            <!-- Re-scope / Install to other workspace -->
            <button
              type="button"
              class="py-1.5 px-3 text-xs font-semibold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-all flex items-center gap-1.5 cursor-pointer"
              :title="t('portal.changeScopeTitle')"
              @click="handleInstall"
            >
              <i class="pi pi-sliders-h text-xs"></i>
              <span>{{ t('portal.changeScope') }}</span>
            </button>

            <!-- Uninstall Button -->
            <button
              type="button"
              class="py-1.5 px-3 text-xs font-bold text-rose-500 border border-rose-300 dark:border-rose-900/60 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-xl transition-all flex items-center gap-1.5 cursor-pointer"
              @click="handleUninstall"
            >
              <i class="pi pi-trash text-xs"></i>
              <span>{{ t('portal.uninstallBtn') }}</span>
            </button>
          </template>
        </div>
      </div>

      <!-- 2. SCOPE BANNER -->
      <div
        v-if="store.selectedSkill.installed"
        class="p-3 rounded-2xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-800/60 flex items-center justify-between text-xs flex-shrink-0"
      >
        <div class="flex items-center gap-2.5">
          <i class="pi pi-shield text-emerald-600 dark:text-emerald-400 text-sm"></i>
          <div>
            <span class="font-bold text-slate-900 dark:text-white">
              {{ t('portal.scopeInfoTitle') }} {{ store.selectedSkill.installScope === 'project' ? t('portal.project') : t('portal.global') }}
            </span>
            <span class="block text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              {{ store.selectedSkill.installScope === 'project' ? 'Skill được đóng gói độc lập trong thư mục dự án và nạp tự động khi mở Workspace.' : t('portal.scopeInfoDesc') }}
            </span>
          </div>
        </div>
        <Tag
          :value="store.selectedSkill.installScope === 'project' ? 'PROJECT SCOPED' : 'GLOBAL SCOPED'"
          severity="success"
          class="!text-[10px] !font-bold"
        />
      </div>

      <!-- 3. DETAIL TABS SWITCHER -->
      <div class="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2 flex-shrink-0">
        <button
          type="button"
          class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
          :class="activeDetailTab === 'overview' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="activeDetailTab = 'overview'"
        >
          <i class="pi pi-file-edit text-xs text-emerald-500"></i>
          <span>{{ t('portal.tabOverview') }}</span>
        </button>

        <button
          type="button"
          class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
          :class="activeDetailTab === 'tools' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="activeDetailTab = 'tools'"
        >
          <i class="pi pi-bolt text-xs text-amber-500"></i>
          <span>Công cụ &amp; Lệnh kích hoạt</span>
          <span class="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">{{ providedTools.length }}</span>
        </button>

        <button
          type="button"
          class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
          :class="activeDetailTab === 'files' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="activeDetailTab = 'files'"
        >
          <i class="pi pi-folder text-xs text-teal-400"></i>
          <span>{{ t('portal.tabFiles') }}</span>
          <span class="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">{{ (store.skillDetail?.files?.length || 2) }}</span>
        </button>

        <button
          type="button"
          class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2"
          :class="activeDetailTab === 'versions' ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="activeDetailTab = 'versions'"
        >
          <i class="pi pi-history text-xs text-blue-400"></i>
          <span>{{ t('portal.tabVersions') }}</span>
        </button>
      </div>

      <!-- 4. TAB CONTENT CONTAINER (BENTO GRID ARCHITECTURE) -->
      <div class="flex-1 overflow-y-auto bg-white dark:bg-slate-900/60 rounded-3xl border border-slate-200/90 dark:border-slate-800 p-6 min-h-0 space-y-6">
        <!-- TAB 1: OVERVIEW (Mô tả Markdown/HTML & Thông số Kỹ thuật) -->
        <div v-if="activeDetailTab === 'overview'" class="space-y-5">
          <!-- Description Container (Hỗ trợ HTML và Markdown) -->
          <div class="p-6 rounded-2xl bg-slate-50/70 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 min-h-[220px]">
            <div
              v-if="renderedDescription"
              class="prose prose-sm dark:prose-invert max-w-none text-slate-700 dark:text-slate-300 leading-relaxed font-normal skill-markdown-body"
              v-html="renderedDescription"
            ></div>
            <div v-else class="text-xs text-slate-400 italic">
              {{ t('portal.noDescription') }}
            </div>
          </div>

          <!-- Thông số Kỹ thuật (Chuẩn cấu trúc như bên MCP) -->
          <div>
            <h3 class="text-sm font-bold text-slate-900 dark:text-white mt-4 mb-2">
              {{ t('portal.specsTitle') }}
            </h3>
            <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
              <div>
                <span class="text-slate-400 block mb-0.5">{{ t('portal.extensionType') }}</span>
                <span class="font-bold text-slate-800 dark:text-white">AIPRO Skill</span>
              </div>
              <div>
                <span class="text-slate-400 block mb-0.5">Giao thức thực thi</span>
                <span class="font-bold text-slate-800 dark:text-white">JSON-RPC 2.0 (Stdio IPC)</span>
              </div>
              <div>
                <span class="text-slate-400 block mb-0.5">{{ t('portal.versionLabel') }}</span>
                <span class="font-mono text-slate-800 dark:text-white">v{{ skillDisplayVersion }}</span>
              </div>
              <div>
                <span class="text-slate-400 block mb-0.5">{{ t('portal.statusLabel') }}</span>
                <span class="font-bold" :class="skillStatusColorClass">
                  {{ skillStatusText }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 2: TOOLS & ACTIONS -->
        <div v-else-if="activeDetailTab === 'tools'" class="space-y-4">
          <div class="text-xs text-slate-500 dark:text-slate-400">
            Skill này đăng ký <strong>{{ providedTools.length }}</strong> công cụ độc quyền vào hệ sinh thái AIPRO:
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="tool in providedTools"
              :key="tool.name"
              class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between"
            >
              <div>
                <div class="flex items-center justify-between gap-2 mb-2">
                  <span class="font-mono font-bold text-xs text-emerald-600 dark:text-emerald-400">
                    {{ tool.name }}
                  </span>
                  <Tag value="TOOL" severity="success" class="!text-[9px] !py-0 !px-1.5" />
                </div>
                <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-3">
                  {{ tool.desc }}
                </p>
              </div>

              <div class="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[11px] font-mono text-slate-500 dark:text-slate-400">
                <span class="text-slate-400 block text-[10px] uppercase font-bold mb-0.5">Tham số đầu vào:</span>
                <code>{{ tool.params }}</code>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 3: FILES -->
        <div v-else-if="activeDetailTab === 'files'" class="space-y-3">
          <div class="text-xs text-slate-500 dark:text-slate-400 mb-2">
            Danh sách tệp tin đính kèm trong gói Skill:
          </div>

          <div
            v-for="file in (store.skillDetail?.files || [
              { fileName: 'SKILL.md', fileSize: 1536 },
              { fileName: 'metadata.json', fileSize: 412 },
              { fileName: 'handler.ts', fileSize: 2840 }
            ])"
            :key="file.fileName"
            class="p-3.5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 flex items-center justify-between text-xs"
          >
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center font-bold">
                <i class="pi pi-file"></i>
              </div>
              <div>
                <span class="font-mono font-bold text-slate-800 dark:text-slate-200 block">{{ file.fileName }}</span>
                <span class="text-[10px] text-slate-400">Sẵn sàng thực thi</span>
              </div>
            </div>
            <span class="font-mono text-slate-400 text-[11px] px-2 py-1 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              {{ String(file.fileSize) }} bytes
            </span>
          </div>
        </div>

        <!-- TAB 4: VERSIONS -->
        <div v-else-if="activeDetailTab === 'versions'" class="space-y-3">
          <div
            v-for="ver in (store.skillVersions || [
              { version: 1, name: 'v1.0.0 (Bản phát hành chính thức)', description: 'Tích hợp đầy đủ tiêu chuẩn bảo mật, Stdio IPC và giao diện Bento UX.' }
            ])"
            :key="ver.version"
            class="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 flex items-start justify-between gap-4"
          >
            <div>
              <div class="flex items-center gap-2">
                <Tag :value="`v${ver.version}.0.0`" severity="success" class="!text-[11px] !font-bold" />
                <span class="text-xs font-bold text-slate-800 dark:text-slate-200">{{ ver.name }}</span>
              </div>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                {{ ver.description }}
              </p>
            </div>

            <!-- Status indicator or Install Button -->
            <span
              v-if="isCurrentInstalledVersion(ver.version)"
              class="text-xs font-bold text-emerald-500 flex items-center gap-1 flex-shrink-0"
            >
              <i class="pi pi-check"></i> {{ t('portal.currentInstalledVersion') }}
            </span>
            <button
              v-else
              type="button"
              class="py-1.5 px-3 text-xs font-semibold rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all cursor-pointer flex items-center gap-1.5 flex-shrink-0"
              @click="handleInstallVersion(ver.version)"
            >
              <i class="pi pi-download text-[10px]"></i>
              <span>{{ store.selectedSkill?.installed ? t('portal.installThisVersion') : t('portal.installSkillBtn') }}</span>
            </button>
          </div>
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
  background-color: #0f172a;
  color: #e2e8f0;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  overflow-x: auto;
  font-family: monospace;
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.skill-markdown-body code:not(pre code)) {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-family: monospace;
  font-size: 0.8rem;
}

:deep(.skill-markdown-body blockquote) {
  border-left: 3px solid #10b981;
  padding-left: 0.75rem;
  margin-left: 0;
  margin-bottom: 0.75rem;
  color: #94a3b8;
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
  color: #0ea5e9;
  text-decoration: underline;
}
</style>
