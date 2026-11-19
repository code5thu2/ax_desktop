<script setup lang="ts">
import { ref } from 'vue'
import { usePluginStore } from '../stores/pluginStore'
import { useI18n } from '@/i18n'
import { AxButton, AxIcon } from '@/components/ui'

const pluginStore = usePluginStore()
const { t } = useI18n()

const testingToolName = ref<string | null>(null)
const toolOutputs = ref<Record<string, any>>({})
const toolInputArgs = ref<Record<string, string>>({})
const showToolArgsInput = ref<Record<string, boolean>>({})

function toggleToolArgs(toolName: string) {
  showToolArgsInput.value[toolName] = !showToolArgsInput.value[toolName]
}

async function runToolTest(toolName: string) {
  testingToolName.value = toolName
  try {
    let args: Record<string, any> = {}
    if (toolInputArgs.value[toolName]?.trim()) {
      try {
        args = JSON.parse(toolInputArgs.value[toolName].trim())
      } catch (jsonErr: any) {
        toolOutputs.value[toolName] = { error: `JSON tham số không hợp lệ: ${jsonErr.message}` }
        return
      }
    }
    const res = await pluginStore.executeToolDirectly(toolName, args)
    toolOutputs.value[toolName] = res.result || res
  } catch (err: any) {
    toolOutputs.value[toolName] = { error: err.message || 'Gọi tool thất bại' }
  } finally {
    testingToolName.value = null
  }
}
</script>

<template>
  <div v-if="pluginStore.selectedPlugin" class="space-y-3">
    <div class="text-xs text-slate-500 dark:text-[#868A91] mb-2">
      {{ t('mcpStudio.toolsDirectNotice', { count: pluginStore.selectedPlugin.tools?.length || 0 }) }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div
        v-for="tool in pluginStore.selectedPlugin.tools"
        :key="tool.name"
        class="p-4 rounded-xl border border-slate-200/80 dark:border-[#393B40] bg-slate-50/50 dark:bg-[#2B2D30] flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between gap-2 mb-1.5">
            <div class="flex items-center gap-2">
              <span class="font-mono font-bold text-xs text-[#3574F0] dark:text-[#56A8F5]">
                {{ tool.name }}
              </span>
              <span class="text-[9px] px-1.5 py-0.5 rounded bg-[#3574F0]/10 text-[#3574F0] dark:text-[#56A8F5] font-mono font-bold">
                tool
              </span>
            </div>

            <div class="flex items-center gap-1.5">
              <AxButton
                variant="success"
                size="sm"
                ijIcon="run"
                :loading="testingToolName === tool.name"
                @click="runToolTest(tool.name)"
              >
                <span>{{ t('mcpStudio.runTestBtn') }}</span>
              </AxButton>

              <button
                type="button"
                class="p-1 rounded-md hover:bg-slate-200 dark:hover:bg-[#393B40] text-slate-400 dark:text-[#868A91] text-xs cursor-pointer"
                :title="showToolArgsInput[tool.name] ? t('mcpStudio.collapseArgs') : t('mcpStudio.inputJsonArgs')"
                @click="toggleToolArgs(tool.name)"
              >
                <AxIcon :name="showToolArgsInput[tool.name] ? 'close' : 'settings'" size="xs" />
              </button>
            </div>
          </div>

          <p class="text-xs text-slate-600 dark:text-[#CED0D6] mb-2 leading-relaxed">
            {{ tool.description }}
          </p>

          <!-- Parameters Input Box -->
          <div v-if="showToolArgsInput[tool.name]" class="mt-2 mb-2 p-2.5 rounded-lg bg-white dark:bg-[#1E1F22] border border-slate-200 dark:border-[#393B40]">
            <label class="block text-[10px] font-bold text-slate-500 dark:text-[#868A91] mb-1">{{ t('mcpStudio.jsonArgsLabel') }}</label>
            <textarea
              v-model="toolInputArgs[tool.name]"
              rows="2"
              class="w-full text-xs font-mono p-2 rounded bg-slate-50 dark:bg-[#2B2D30] border border-slate-200 dark:border-[#393B40] text-slate-800 dark:text-[#DFE1E5] focus:outline-none focus:border-[#3574F0]"
              :placeholder="t('mcpStudio.paramsPlaceholder')"
            ></textarea>
          </div>

          <!-- Output display -->
          <div
            v-if="toolOutputs[tool.name]"
            class="mt-2 p-2.5 rounded-lg bg-[#1E1F22] text-[#5FAD65] font-mono text-[10px] overflow-x-auto max-h-36 border border-[#393B40]"
          >
            <div class="text-[9px] text-[#868A91] mb-1 font-bold">{{ t('mcpStudio.testResult') }}</div>
            <pre>{{ typeof toolOutputs[tool.name] === 'object' ? JSON.stringify(toolOutputs[tool.name], null, 2) : toolOutputs[tool.name] }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
