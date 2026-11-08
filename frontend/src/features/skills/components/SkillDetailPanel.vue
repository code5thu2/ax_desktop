<script setup lang="ts">
import { ref, computed } from 'vue'
import Tag from 'primevue/tag'
import { useSkillStore } from '../stores/skillStore'
import { useConfirm } from 'primevue/useconfirm'
import { useI18n } from '@/i18n'

const store = useSkillStore()
const confirm = useConfirm()
const { t } = useI18n()

const activeDetailTab = ref<'overview' | 'tools' | 'files' | 'versions'>('overview')
const copiedCode = ref(false)
const copiedPromptIdx = ref<number | null>(null)

function handleInstall() {
  if (store.selectedSkill) {
    store.pendingInstallSkill = store.selectedSkill
    store.showScopeModal = true
  }
}

function isCurrentInstalledVersion(verNumber: number): boolean {
  if (!store.selectedSkill?.installed) return false
  const currVer = store.selectedSkill.installedVersion ?? 1
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

function copySkillSpec() {
  const content = store.skillDetail?.description || `# ${store.selectedSkill?.name}\n\nSkill được đóng gói chuẩn cho AIPRO Studio với quy trình kiểm thử nghiêm ngặt.`
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(content)
  }
  copiedCode.value = true
  setTimeout(() => {
    copiedCode.value = false
  }, 2000)
}

function copyPrompt(text: string, idx: number) {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(text)
  }
  copiedPromptIdx.value = idx
  setTimeout(() => {
    copiedPromptIdx.value = null
  }, 2000)
}

// Generate sample prompts tailored to the skill
const samplePrompts = computed(() => {
  const name = store.selectedSkill?.name || 'Skill'
  if (name.includes('Code')) {
    return [
      `@${name.toLowerCase().replace(/\s+/g, '-')} Hãy phân tích kiến trúc mã nguồn và kiểm tra lỗi tiềm ẩn trong module hiện tại.`,
      `@${name.toLowerCase().replace(/\s+/g, '-')} Viết bộ unit tests hoàn chỉnh với độ bao phủ 100% cho file đang mở.`,
      `/refactor --target=src/components --pattern=solid`
    ]
  }
  if (name.includes('Database') || name.includes('Query')) {
    return [
      `@${name.toLowerCase().replace(/\s+/g, '-')} Kiểm tra schema các bảng hiện tại và tối ưu hóa index cho các truy vấn chậm.`,
      `@${name.toLowerCase().replace(/\s+/g, '-')} Viết câu lệnh migration an toàn để thêm cột metadata JSONB vào bảng users.`,
      `/db-inspect --schema=public --explain`
    ]
  }
  if (name.includes('Legal') || name.includes('Document')) {
    return [
      `@${name.toLowerCase().replace(/\s+/g, '-')} Tra cứu quy định mới nhất về giấy phép kinh doanh thương mại điện tử tại Việt Nam.`,
      `@${name.toLowerCase().replace(/\s+/g, '-')} Rà soát các điều khoản miễn trừ trách nhiệm trong dự thảo hợp đồng đối tác.`,
      `/legal-audit --standard=vn-commercial-law`
    ]
  }
  return [
    `@${name.toLowerCase().replace(/\s+/g, '-')} Kích hoạt skill và thực thi tác vụ mặc định.`,
    `@${name.toLowerCase().replace(/\s+/g, '-')} Liệt kê tất cả các tham số cấu hình hỗ trợ.`,
    `/execute --verbose`
  ]
})

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
                v{{ store.selectedSkill.installedVersion || 1 }}.0.0
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
              title="Đổi phạm vi hoặc cài thêm vào dự án khác"
              @click="handleInstall"
            >
              <i class="pi pi-sliders-h text-xs"></i>
              <span>Đổi phạm vi</span>
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
          <span>{{ t('portal.tabOverview') }} &amp; Đặc tả</span>
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
        <!-- TAB 1: OVERVIEW & SPEC -->
        <div v-if="activeDetailTab === 'overview'" class="space-y-6">
          <!-- Bento Grid: Top 2-Column Split -->
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <!-- Left: Description & Capability Highlights (7 cols) -->
            <div class="lg:col-span-7 p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between">
              <div>
                <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2 flex items-center gap-2">
                  <i class="pi pi-info-circle text-emerald-500"></i>
                  <span>{{ t('portal.skillDescTitle') }}</span>
                </h3>
                <p class="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
                  {{ store.selectedSkill.description }}
                </p>
              </div>

              <!-- Feature Bullets -->
              <div class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700/60 space-y-2">
                <div class="text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Tính năng cốt lõi:</div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600 dark:text-slate-300">
                  <div class="flex items-center gap-2">
                    <i class="pi pi-check-circle text-emerald-500 text-xs"></i>
                    <span>Tự động nhận diện ngữ cảnh dự án</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <i class="pi pi-check-circle text-emerald-500 text-xs"></i>
                    <span>Hỗ trợ Stdio JSON-RPC protocol</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <i class="pi pi-check-circle text-emerald-500 text-xs"></i>
                    <span>Không rò rỉ dữ liệu (Zero Telemetry)</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <i class="pi pi-check-circle text-emerald-500 text-xs"></i>
                    <span>Tương thích đa tác nhân (Multi-Agent)</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Environment & Security Matrix (5 cols) -->
            <div class="lg:col-span-5 p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800">
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3 flex items-center gap-2">
                <i class="pi pi-sliders-h text-teal-400"></i>
                <span>Ma trận Môi trường &amp; Quyền hạn</span>
              </h3>

              <div class="space-y-2.5 text-xs">
                <div class="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span class="text-slate-400">Phạm vi thực thi</span>
                  <span class="font-bold text-slate-800 dark:text-white uppercase">{{ store.selectedSkill.installScope || store.selectedSkill.scope || 'GLOBAL' }}</span>
                </div>

                <div class="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span class="text-slate-400">Hỗ trợ IDE / CLI</span>
                  <span class="font-bold text-emerald-500">Claude, Cursor, AIPRO</span>
                </div>

                <div class="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span class="text-slate-400">Giao thức IPC</span>
                  <span class="font-mono text-slate-800 dark:text-white">Stdio (JSON-RPC 2.0)</span>
                </div>

                <div class="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span class="text-slate-400">Mức độ bảo mật</span>
                  <span class="font-bold text-emerald-400 flex items-center gap-1">
                    <i class="pi pi-lock text-[10px]"></i> Sandboxed
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Bento Card 3: Terminal Code Viewer (SKILL.md) -->
          <div class="rounded-2xl border border-slate-800 overflow-hidden shadow-2xl bg-slate-950">
            <!-- macOS-style Terminal Header -->
            <div class="h-10 bg-slate-900 px-4 flex items-center justify-between border-b border-slate-800">
              <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-rose-500/80"></span>
                <span class="w-3 h-3 rounded-full bg-amber-500/80"></span>
                <span class="w-3 h-3 rounded-full bg-emerald-500/80"></span>
                <span class="ml-2 font-mono text-xs text-slate-400 font-semibold">
                  aipro/skills/{{ store.selectedSkill.name.toLowerCase().replace(/\s+/g, '-') }}/SKILL.md
                </span>
              </div>

              <button
                type="button"
                class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all flex items-center gap-1.5 cursor-pointer border border-slate-700/60"
                @click="copySkillSpec"
              >
                <i :class="copiedCode ? 'pi pi-check text-emerald-400' : 'pi pi-copy text-slate-400'"></i>
                <span>{{ copiedCode ? 'Đã sao chép!' : 'Sao chép đặc tả' }}</span>
              </button>
            </div>

            <!-- Terminal Code Body -->
            <div class="p-5 font-mono text-xs text-emerald-300/90 leading-relaxed overflow-x-auto max-h-80 whitespace-pre-wrap select-text">
{{ store.skillDetail?.description || `# ${store.selectedSkill.name}

## 1. Description & Context
${store.selectedSkill.description}

## 2. Trigger Rules & Directives
- Auto-activated when relevant source code or query patterns match.
- Fully compatible with Cursor, Claude Code, and AIPRO Super Studio runtime.
- Executes within safe sandbox boundaries without unauthorized network calls.` }}
            </div>
          </div>

          <!-- Bento Card 4: Quick Trigger Prompts -->
          <div class="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800">
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3 flex items-center gap-2">
              <i class="pi pi-send text-emerald-500"></i>
              <span>Lệnh &amp; Câu hỏi mẫu để kích hoạt nhanh trong AI Chat</span>
            </h3>

            <div class="space-y-2">
              <div
                v-for="(prompt, idx) in samplePrompts"
                :key="idx"
                class="group p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3 transition-colors hover:border-emerald-500/50"
              >
                <div class="flex items-center gap-2.5 min-w-0 font-mono text-xs text-slate-800 dark:text-slate-200">
                  <span class="text-emerald-500 font-bold">$</span>
                  <span class="truncate">{{ prompt }}</span>
                </div>
                <button
                  type="button"
                  class="px-2.5 py-1 rounded-lg text-[11px] font-semibold text-slate-400 group-hover:text-emerald-400 group-hover:bg-emerald-500/10 transition-all flex items-center gap-1 cursor-pointer flex-shrink-0"
                  @click="copyPrompt(prompt, idx)"
                >
                  <i :class="copiedPromptIdx === idx ? 'pi pi-check text-emerald-400' : 'pi pi-copy'"></i>
                  <span>{{ copiedPromptIdx === idx ? 'Đã chép' : 'Sao chép' }}</span>
                </button>
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
