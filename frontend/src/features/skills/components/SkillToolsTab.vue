<script setup lang="ts">
import { computed } from 'vue'
import Tag from 'primevue/tag'
import { useSkillStore } from '../stores/skillStore'
import { useI18n } from '@/i18n'

const store = useSkillStore()
const { t } = useI18n()

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
  <div class="space-y-3">
    <div class="text-xs text-slate-500 dark:text-[#868A91]">
      {{ t('portal.toolsCountNotice', { count: providedTools.length }) }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div
        v-for="tool in providedTools"
        :key="tool.name"
        class="p-4 rounded-xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-200/80 dark:border-[#393B40] flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between gap-2 mb-2">
            <span class="font-mono font-bold text-xs text-[#3574F0] dark:text-[#56A8F5]">
              {{ tool.name }}
            </span>
            <Tag value="TOOL" severity="success" class="!text-[9px] !py-0 !px-1.5 dark:bg-[#5FAD65]/20 dark:text-[#5FAD65]" />
          </div>
          <p class="text-xs text-slate-600 dark:text-[#CED0D6] leading-relaxed mb-3">
            {{ tool.desc }}
          </p>
        </div>

        <div class="p-2.5 rounded-lg bg-white dark:bg-[#2B2D30] border border-slate-200 dark:border-[#43454A] text-[11px] font-mono text-slate-500 dark:text-[#868A91]">
          <span class="text-slate-400 dark:text-[#868A91] block text-[10px] uppercase font-bold mb-0.5">{{ t('portal.toolInputParams') }}</span>
          <code class="text-[#DFE1E5]">{{ tool.params }}</code>
        </div>
      </div>
    </div>
  </div>
</template>
