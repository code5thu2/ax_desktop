<script setup lang="ts">
import { computed } from 'vue'
import AxIcon from './AxIcon.vue'

export type BadgeVariant = 'blue' | 'green' | 'amber' | 'red' | 'purple' | 'neutral'
export type BadgeSize = 'sm' | 'md'

interface Props {
  variant?: BadgeVariant
  size?: BadgeSize
  dot?: boolean
  icon?: string
  ijIcon?: string
  iconName?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'blue',
  size: 'md',
  dot: false,
})

const activeIconName = computed(() => {
  return props.iconName || props.ijIcon || (props.icon && !props.icon.startsWith('pi ') ? props.icon : null)
})

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'green':
      return 'bg-[#5FAD65]/15 text-[#36A15E] dark:text-[#5FAD65] border-[#5FAD65]/30'
    case 'amber':
      return 'bg-[#E3A83F]/15 text-[#D48800] dark:text-[#F2C55C] border-[#E3A83F]/30'
    case 'red':
      return 'bg-[#FA5252]/15 text-[#FA5252] dark:text-[#FA5252] border-[#FA5252]/30'
    case 'purple':
      return 'bg-[#C77DBB]/15 text-[#B052A3] dark:text-[#C77DBB] border-[#C77DBB]/30'
    case 'neutral':
      return 'bg-slate-100 dark:bg-[#393B40] text-slate-600 dark:text-[#868A91] border-slate-200 dark:border-[#43454A]'
    case 'blue':
    default:
      return 'bg-[#3574F0]/15 text-[#3574F0] dark:text-[#56A8F5] border-[#3574F0]/30'
  }
})

const dotColorClass = computed(() => {
  switch (props.variant) {
    case 'green':
      return 'bg-[#5FAD65] shadow-[0_0_6px_rgba(95,173,101,0.8)]'
    case 'amber':
      return 'bg-[#E3A83F] shadow-[0_0_6px_rgba(227,168,63,0.8)]'
    case 'red':
      return 'bg-[#FA5252] shadow-[0_0_6px_rgba(250,82,82,0.8)]'
    case 'purple':
      return 'bg-[#C77DBB] shadow-[0_0_6px_rgba(199,125,187,0.8)]'
    case 'neutral':
      return 'bg-[#868A91]'
    case 'blue':
    default:
      return 'bg-[#3574F0] shadow-[0_0_6px_rgba(53,116,240,0.8)]'
  }
})

const sizeClasses = computed(() => {
  return props.size === 'sm'
    ? 'text-[10px] px-1.5 py-0.5 gap-1 rounded font-mono'
    : 'text-xs px-2 py-0.5 gap-1.5 rounded-md font-medium'
})
</script>

<template>
  <span
    class="inline-flex items-center border select-none transition-colors"
    :class="[variantClasses, sizeClasses]"
  >
    <span v-if="props.dot" class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="dotColorClass" />
    <AxIcon v-if="activeIconName" :name="activeIconName" size="xs" class="text-current" />
    <i v-else-if="props.icon" :class="[props.icon, 'text-[11px] flex-shrink-0']" />
    <slot />
  </span>
</template>
