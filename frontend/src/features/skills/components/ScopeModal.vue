<script setup lang="ts">
import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import RadioButton from 'primevue/radiobutton'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import { useSkillStore } from '../stores/skillStore'
import { nativeBridge } from '@/services/nativeBridge'

const store = useSkillStore()

const scopeType = ref<'global' | 'project'>('global')
const selectedProject = ref<string>('')
const customProjectPath = ref<string>('')
const isInstalling = ref(false)

const projectOptions = computed(() => {
  return store.recentProjects.map((p) => ({ label: p, value: p }))
})

async function handleBrowseFolder() {
  const res = await nativeBridge.selectFolder()
  if (res.ok && res.path) {
    customProjectPath.value = res.path
    selectedProject.value = res.path
    store.addProject(res.path)
  }
}

async function handleConfirmInstall() {
  if (!store.pendingInstallSkill) return

  isInstalling.value = true
  try {
    const skill = store.pendingInstallSkill
    const targetDir = scopeType.value === 'project'
      ? (selectedProject.value || customProjectPath.value || store.currentProject || '.')
      : '.'

    await store.installSkill(skill.name, skill.installedVersion || 1, scopeType.value, targetDir)
    store.showScopeModal = false
    store.pendingInstallSkill = null
  } catch (err: any) {
    console.error('Install failed:', err)
  } finally {
    isInstalling.value = false
  }
}

function handleClose() {
  store.showScopeModal = false
  store.pendingInstallSkill = null
}
</script>

<template>
  <Dialog
    v-model:visible="store.showScopeModal"
    modal
    header="Chọn phạm vi cài đặt Skill"
    :style="{ width: '480px' }"
    :closable="!isInstalling"
    class="p-dialog-custom"
  >
    <div class="space-y-5 py-2">
      <div v-if="store.pendingInstallSkill" class="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white shadow-sm font-bold">
          <i class="pi pi-box text-lg"></i>
        </div>
        <div class="min-w-0 flex-1">
          <h4 class="text-sm font-bold text-slate-900 dark:text-white truncate">
            {{ store.pendingInstallSkill.name }}
          </h4>
          <p class="text-xs text-slate-500 dark:text-slate-400 truncate">
            Tác giả: {{ store.pendingInstallSkill.creatorName }} &bull; Phiên bản: {{ store.pendingInstallSkill.installedVersion || 1 }}
          </p>
        </div>
      </div>

      <!-- Scope selection -->
      <div class="space-y-3">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Phạm vi áp dụng
        </label>

        <!-- Global Option -->
        <div
          class="flex items-start gap-3 p-3.5 rounded-xl border transition-all cursor-pointer"
          :class="scopeType === 'global' ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/20' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40'"
          @click="scopeType = 'global'"
        >
          <RadioButton v-model="scopeType" value="global" inputId="scope-global" class="mt-0.5" />
          <div class="flex-1 text-xs">
            <label for="scope-global" class="font-bold text-slate-900 dark:text-white block cursor-pointer">
              Toàn cục (Global)
            </label>
            <p class="text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">
              Cài vào thư mục hệ thống <code class="font-mono text-[11px] bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">~/.aipro/skills</code>, dùng chung cho tất cả các dự án.
            </p>
          </div>
        </div>

        <!-- Project Option -->
        <div
          class="flex items-start gap-3 p-3.5 rounded-xl border transition-all cursor-pointer"
          :class="scopeType === 'project' ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/20' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40'"
          @click="scopeType = 'project'"
        >
          <RadioButton v-model="scopeType" value="project" inputId="scope-project" class="mt-0.5" />
          <div class="flex-1 text-xs">
            <label for="scope-project" class="font-bold text-slate-900 dark:text-white block cursor-pointer">
              Theo Dự án (Project Workspace)
            </label>
            <p class="text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">
              Cài cục bộ vào thư mục <code class="font-mono text-[11px] bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">&lt;project&gt;/.aipro/skills</code> để đóng gói độc lập theo repo.
            </p>
          </div>
        </div>
      </div>

      <!-- Project Picker (Only shown when project scope selected) -->
      <div v-if="scopeType === 'project'" class="space-y-2 pt-1 animate-fadeIn">
        <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300">
          Thư mục Dự án đích
        </label>

        <div v-if="projectOptions.length > 0" class="mb-2">
          <Dropdown
            v-model="selectedProject"
            :options="projectOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Chọn từ danh sách gần đây"
            class="w-full !rounded-xl !text-xs"
          />
        </div>

        <div class="flex gap-2">
          <InputText
            v-model="customProjectPath"
            placeholder="Hoặc nhập đường dẫn dự án (VD: D:/AI_Projects/MyApp)"
            class="flex-1 !rounded-xl !text-xs"
          />
          <Button
            type="button"
            icon="pi pi-folder-open"
            label="Chọn..."
            variant="outlined"
            class="!rounded-xl !text-xs cursor-pointer flex-shrink-0"
            @click="handleBrowseFolder"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <Button
          type="button"
          label="Hủy bỏ"
          variant="text"
          :disabled="isInstalling"
          class="!rounded-xl !text-xs cursor-pointer"
          @click="handleClose"
        />
        <Button
          type="button"
          label="Xác nhận Cài đặt"
          icon="pi pi-check"
          :loading="isInstalling"
          class="!rounded-xl !text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/20 cursor-pointer"
          @click="handleConfirmInstall"
        />
      </div>
    </template>
  </Dialog>
</template>
