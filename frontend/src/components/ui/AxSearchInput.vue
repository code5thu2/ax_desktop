<script setup lang="ts">
import AxIcon from './AxIcon.vue'

interface Props {
  modelValue?: string
  placeholder?: string
  shortcut?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: 'Tìm kiếm...',
  shortcut: '',
})

const emit = defineEmits<{
  (e: 'update:modelValue', val: string): void
}>()

function clear() {
  emit('update:modelValue', '')
}
</script>

<template>
  <div class="relative flex items-center w-full">
    <AxIcon name="search" size="sm" class="absolute left-2.5 text-slate-400 dark:text-[#868A91] pointer-events-none" />
    <input
      type="text"
      :value="props.modelValue"
      :placeholder="props.placeholder"
      class="w-full h-8 pl-8 pr-8 bg-slate-50 dark:bg-[#1E1F22] border border-slate-200 dark:border-[#393B40] rounded-lg text-xs text-slate-900 dark:text-[#DFE1E5] placeholder:text-slate-400 dark:placeholder:text-[#868A91] transition-all focus:outline-none focus:ring-2 focus:ring-[#3574F0]/30 focus:border-[#3574F0]"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <!-- Clear button or shortcut badge -->
    <div class="absolute right-2 flex items-center">
      <button
        v-if="props.modelValue"
        type="button"
        class="w-4 h-4 rounded flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-[#DFE1E5] transition-colors cursor-pointer"
        @click="clear"
      >
        <AxIcon name="close" size="xs" />
      </button>
      <span
        v-else-if="props.shortcut"
        class="text-[10px] font-mono text-slate-400 dark:text-[#868A91] bg-slate-200/60 dark:bg-[#2B2D30] px-1 py-0.5 rounded border border-slate-300/40 dark:border-[#43454A] pointer-events-none select-none"
      >
        {{ props.shortcut }}
      </span>
    </div>
  </div>
</template>
