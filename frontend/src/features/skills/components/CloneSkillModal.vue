<script setup lang="ts">
import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import Checkbox from 'primevue/checkbox'
import { useSkillStore } from '../stores/skillStore'

const store = useSkillStore()

const sourceProject = ref<string>(store.currentProject || '')
const targetProject = ref<string>('')
const selectedSkillNames = ref<string[]>([])
const isCloning = ref(false)
const errorMsg = ref<string | null>(null)

const projectOptions = computed(() => {
  return store.recentProjects.map((p) => ({ label: p, value: p }))
})

// Filter installed skills belonging to source project (or global)
const availableSkillsToClone = computed(() => {
  return store.installedSkills.map((s) => s.name)
})

async function handleConfirmClone() {
  errorMsg.value = null

  if (!sourceProject.value) {
    errorMsg.value = 'Vui lòng chọn Dự án nguồn'
    return
  }
  if (!targetProject.value) {
    errorMsg.value = 'Vui lòng chọn hoặc nhập Dự án đích'
    return
  }
  if (sourceProject.value === targetProject.value) {
    errorMsg.value = 'Dự án nguồn và dự án đích không được trùng nhau'
    return
  }
  if (selectedSkillNames.value.length === 0) {
    errorMsg.value = 'Vui lòng chọn ít nhất một skill để sao chép'
    return
  }

  isCloning.value = true
  try {
    await store.cloneSkills(sourceProject.value, targetProject.value, selectedSkillNames.value)
    store.showCloneSkillModal = false
    selectedSkillNames.value = []
  } catch (err: any) {
    errorMsg.value = err?.message || String(err)
  } finally {
    isCloning.value = false
  }
}

function handleClose() {
  errorMsg.value = null
  selectedSkillNames.value = []
  store.showCloneSkillModal = false
}
</script>

<template>
  <Dialog
    v-model:visible="store.showCloneSkillModal"
    modal
    header="Sao chép Skill giữa các Dự án"
    :style="{ width: '500px' }"
  >
    <div class="space-y-4 py-2">
      <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
        Nhân bản các Skill đã cấu hình từ workspace nguồn sang workspace đích mà không cần tải lại từ máy chủ.
      </p>

      <div class="space-y-3">
        <!-- Source project -->
        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Dự án Nguồn (Source)
          </label>
          <Dropdown
            v-model="sourceProject"
            :options="projectOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Chọn dự án nguồn"
            class="w-full !rounded-xl !text-xs"
          />
        </div>

        <!-- Target project -->
        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Dự án Đích (Target)
          </label>
          <Dropdown
            v-model="targetProject"
            :options="projectOptions.filter(p => p.value !== sourceProject)"
            optionLabel="label"
            optionValue="value"
            placeholder="Chọn dự án đích"
            class="w-full !rounded-xl !text-xs"
          />
        </div>

        <!-- Skills to clone -->
        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Chọn Skill cần sao chép
          </label>
          <div class="max-h-40 overflow-y-auto space-y-2 p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50">
            <div
              v-for="skillName in availableSkillsToClone"
              :key="skillName"
              class="flex items-center gap-2.5 text-xs text-slate-700 dark:text-slate-300 cursor-pointer"
            >
              <Checkbox
                v-model="selectedSkillNames"
                :value="skillName"
                :inputId="`clone-${skillName}`"
              />
              <label :for="`clone-${skillName}`" class="cursor-pointer font-medium select-none truncate">
                {{ skillName }}
              </label>
            </div>
            <div v-if="availableSkillsToClone.length === 0" class="text-xs text-slate-400 text-center py-2">
              Không có skill khả dụng để sao chép
            </div>
          </div>
        </div>

        <p v-if="errorMsg" class="text-xs text-rose-500 font-semibold">
          {{ errorMsg }}
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 pt-2">
        <Button
          type="button"
          label="Hủy"
          variant="text"
          :disabled="isCloning"
          class="!rounded-xl !text-xs cursor-pointer"
          @click="handleClose"
        />
        <Button
          type="button"
          label="Sao chép ngay"
          icon="pi pi-copy"
          :loading="isCloning"
          :disabled="selectedSkillNames.length === 0"
          class="!rounded-xl !text-xs !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-md shadow-emerald-500/20 cursor-pointer disabled:opacity-50"
          @click="handleConfirmClone"
        />
      </div>
    </template>
  </Dialog>
</template>
