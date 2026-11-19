<script setup lang="ts">
import Dialog from 'primevue/dialog'
import { useI18n } from '@/i18n'
import type { PluginItem } from '../../types/plugin'
import { AxButton, AxInput } from '@/components/ui'

const props = defineProps<{
  visible: boolean
  plugin: PluginItem | null
  isEditing: boolean
  envValues: Record<string, string>
}>()

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void
  (e: 'confirm'): void
}>()

const { t } = useI18n()
</script>

<template>
  <Dialog
    :visible="props.visible"
    modal
    :header="t('mcpStudio.envModalTitle') + ': ' + (props.plugin?.name || '')"
    :style="{ width: '500px' }"
    class="p-dialog-custom"
    @update:visible="emit('update:visible', $event)"
  >
    <div v-if="props.plugin" class="space-y-3.5 text-xs py-2">
      <p class="text-slate-500 dark:text-[#868A91] leading-relaxed">
        {{ props.isEditing
            ? 'Cập nhật lại các biến môi trường cho MCP server này (.env):'
            : 'MCP này yêu cầu các biến môi trường để hoạt động. Vui lòng xác nhận:' }}
      </p>

      <div v-for="req in props.plugin.envRequirements" :key="req.key">
        <label class="block font-bold mb-1 text-slate-700 dark:text-[#DFE1E5]">
          {{ req.label || req.key }}
          <span v-if="req.required" class="text-[#FA5252]">*</span>
        </label>
        <AxInput
          v-model="props.envValues[req.key]"
          :type="req.key.toLowerCase().includes('token') || req.key.toLowerCase().includes('key') || req.key.toLowerCase().includes('pass') ? 'password' : 'text'"
          :placeholder="req.default || req.key"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <AxButton
          variant="ghost"
          size="sm"
          @click="emit('update:visible', false)"
        >
          {{ t('common.cancel') }}
        </AxButton>
        <AxButton
          variant="primary"
          size="sm"
          ijIcon="check"
          @click="emit('confirm')"
        >
          <span>{{ t('mcpStudio.saveEnvBtn') }}</span>
        </AxButton>
      </div>
    </template>
  </Dialog>
</template>
