<script setup lang="ts">
import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import { usePluginStore } from '../../stores/pluginStore'
import { useI18n } from '@/i18n'
import { AxButton, AxInput, AxIcon } from '@/components/ui'

const emit = defineEmits<{
  (e: 'success', name: string, count: number): void
}>()

const pluginStore = usePluginStore()
const { t } = useI18n()

const gitRepoUrl = ref('')
const gitBranch = ref('main')
const gitToken = ref('')
const gitName = ref('')
const gitDesc = ref('')
const isGitImporting = ref(false)
const gitImportError = ref('')

async function handleGitImport() {
  if (!gitRepoUrl.value.trim()) return
  isGitImporting.value = true
  gitImportError.value = ''
  try {
    const res = await pluginStore.importFromGit(
      gitRepoUrl.value.trim(),
      gitBranch.value.trim() || 'main',
      gitToken.value.trim() || undefined,
      gitName.value.trim() || undefined,
      gitDesc.value.trim() || undefined
    )
    pluginStore.showGitImportModal = false
    const name = res.name
    const count = res.tools_count
    gitRepoUrl.value = ''
    gitToken.value = ''
    gitName.value = ''
    gitDesc.value = ''
    emit('success', name, count)
  } catch (err: any) {
    gitImportError.value = err.message || 'Lỗi khi nhập Git'
  } finally {
    isGitImporting.value = false
  }
}
</script>

<template>
  <Dialog
    v-model:visible="pluginStore.showGitImportModal"
    modal
    :header="t('mcpStudio.gitModalTitle')"
    :style="{ width: '540px' }"
    class="p-dialog-custom"
  >
    <div class="space-y-3.5 text-xs py-2">
      <p class="text-slate-500 dark:text-[#868A91] leading-relaxed">
        {{ t('mcpStudio.gitModalTitle') }}
      </p>

      <div v-if="gitImportError" class="p-3 rounded-lg bg-[#FA5252]/10 border border-[#FA5252]/30 text-[#FA5252] flex items-center gap-1.5">
        <AxIcon name="alert" size="xs" />
        <span>{{ gitImportError }}</span>
      </div>

      <div>
        <label class="block font-bold mb-1 text-slate-700 dark:text-[#DFE1E5]">
          Git Repository URL <span class="text-[#FA5252]">*</span>
        </label>
        <AxInput
          v-model="gitRepoUrl"
          ijIcon="git"
          placeholder="https://github.com/my-org/my-mcp.git"
        />
      </div>

      <div class="grid grid-cols-2 gap-2.5">
        <div>
          <label class="block font-bold mb-1 text-slate-700 dark:text-[#DFE1E5]">{{ t('mcpStudio.gitBranchLabel') }}</label>
          <AxInput
            v-model="gitBranch"
            placeholder="main"
          />
        </div>
        <div>
          <label class="block font-bold mb-1 text-slate-700 dark:text-[#DFE1E5]">{{ t('mcpStudio.displayNameLabel') }}</label>
          <AxInput
            v-model="gitName"
            placeholder="VD: Database Tools"
          />
        </div>
      </div>

      <div>
        <label class="block font-bold mb-1 text-slate-700 dark:text-[#DFE1E5]">{{ t('mcpStudio.authTokenLabel') }}</label>
        <AxInput
          v-model="gitToken"
          type="password"
          placeholder="ghp_xxxx"
        />
      </div>

      <div>
        <label class="block font-bold mb-1 text-slate-700 dark:text-[#DFE1E5]">{{ t('mcpStudio.shortDescLabel') }}</label>
        <AxInput
          v-model="gitDesc"
          :placeholder="t('mcpStudio.descPlaceholder')"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <AxButton
          variant="ghost"
          size="sm"
          :disabled="isGitImporting"
          @click="pluginStore.showGitImportModal = false"
        >
          {{ t('common.cancel') }}
        </AxButton>
        <AxButton
          variant="primary"
          size="sm"
          ijIcon="check"
          :loading="isGitImporting"
          :disabled="!gitRepoUrl.trim() || isGitImporting"
          @click="handleGitImport"
        >
          <span>{{ isGitImporting ? t('mcpStudio.importing') : t('mcpStudio.submitImportBtn') }}</span>
        </AxButton>
      </div>
    </template>
  </Dialog>
</template>
