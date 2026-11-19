<script setup lang="ts">
import { computed } from 'vue'
import AxIcon from './AxIcon.vue'

interface Props {
  modelValue?: string | number
  placeholder?: string
  type?: string
  icon?: string
  ijIcon?: string
  error?: string
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '',
  type: 'text',
  disabled: false,
  size: 'md',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'h-7 text-xs py-1 rounded-md'
    case 'lg':
      return 'h-10 text-sm py-2 rounded-lg'
    case 'md':
    default:
      return 'h-8 text-xs py-1.5 rounded-lg'
  }
})

const paddingClass = computed(() => {
  return props.icon || props.ijIcon ? 'pl-8 pr-3' : 'px-3'
})
</script>

<template>
  <div class="relative w-full flex flex-col gap-1">
    <div class="relative flex items-center w-full">
      <AxIcon
        v-if="props.ijIcon"
        :name="props.ijIcon"
        size="sm"
        class="absolute left-2.5 text-[#868A91] pointer-events-none"
      />
      <i
        v-else-if="props.icon"
        :class="[
          props.icon,
          'absolute left-2.5 text-slate-400 dark:text-[#868A91] pointer-events-none text-xs flex-shrink-0',
        ]"
      />
      <input
        :type="props.type"
        :value="props.modelValue"
        :placeholder="props.placeholder"
        :disabled="props.disabled"
        class="w-full bg-slate-50 dark:bg-[#1E1F22] border text-slate-900 dark:text-[#DFE1E5] placeholder:text-slate-400 dark:placeholder:text-[#868A91] transition-all focus:outline-none focus:ring-2 focus:ring-[#3574F0]/30 focus:border-[#3574F0] disabled:opacity-50 disabled:cursor-not-allowed"
        :class="[
          sizeClass,
          paddingClass,
          props.error
            ? 'border-[#FA5252] focus:ring-[#FA5252]/30 focus:border-[#FA5252]'
            : 'border-slate-200 dark:border-[#393B40]',
        ]"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />
    </div>
    <span v-if="props.error" class="text-[11px] text-[#FA5252] font-medium pl-1">
      {{ props.error }}
    </span>
  </div>
</template>
