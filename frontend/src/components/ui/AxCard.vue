<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  layer?: 1 | 2
  interactive?: boolean
  selected?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  layer: 1,
  interactive: false,
  selected: false,
  padding: 'md',
})

const layerClass = computed(() => {
  return props.layer === 2
    ? 'bg-white dark:bg-[#393B40] shadow-sm'
    : 'bg-white dark:bg-[#2B2D30]'
})

const paddingClass = computed(() => {
  switch (props.padding) {
    case 'none':
      return 'p-0'
    case 'sm':
      return 'p-3'
    case 'lg':
      return 'p-6'
    case 'md':
    default:
      return 'p-4 sm:p-5'
  }
})
</script>

<template>
  <div
    class="rounded-xl border transition-all duration-150 relative overflow-hidden"
    :class="[
      layerClass,
      paddingClass,
      props.selected
        ? '!border-[#3574F0] ring-1 ring-[#3574F0]/40 dark:shadow-[0_0_15px_-3px_rgba(53,116,240,0.3)]'
        : 'border-slate-200/90 dark:border-[#393B40]',
      props.interactive
        ? 'hover:border-slate-300 dark:hover:border-[#43454A] dark:hover:bg-[#313438] cursor-pointer'
        : '',
    ]"
  >
    <slot />
  </div>
</template>
