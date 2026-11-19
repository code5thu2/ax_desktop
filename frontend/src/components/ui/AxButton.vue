<script setup lang="ts">
import { computed } from 'vue'
import AxIcon from './AxIcon.vue'

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success'
export type ButtonSize = 'sm' | 'md' | 'lg'

interface Props {
  variant?: ButtonVariant
  size?: ButtonSize
  icon?: string
  ijIcon?: string
  iconName?: string
  iconPos?: 'left' | 'right'
  loading?: boolean
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  iconPos: 'left',
  loading: false,
  disabled: false,
  type: 'button',
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const activeIconName = computed(() => {
  return props.iconName || props.ijIcon || (props.icon && !props.icon.startsWith('pi ') ? props.icon : null)
})

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'bg-[#3574F0] hover:bg-[#3064D0] text-white font-medium shadow-sm hover:shadow-glow-blue active:bg-[#2855B3]'
    case 'success':
      return 'bg-[#5FAD65] hover:bg-[#4E9B54] text-white font-medium shadow-sm hover:shadow-glow-green active:bg-[#3E8043]'
    case 'secondary':
      return 'bg-slate-100 hover:bg-slate-200 text-slate-800 dark:bg-[#2B2D30] dark:hover:bg-[#393B40] dark:text-[#DFE1E5] border border-slate-200 dark:border-[#43454A]'
    case 'outline':
      return 'bg-transparent hover:bg-slate-100 dark:hover:bg-[#393B40] text-slate-700 dark:text-[#DFE1E5] border border-slate-300 dark:border-[#43454A]'
    case 'ghost':
      return 'bg-transparent hover:bg-slate-100 dark:hover:bg-[#393B40] text-slate-600 dark:text-[#868A91] hover:text-slate-900 dark:hover:text-[#DFE1E5]'
    case 'danger':
      return 'bg-[#FA5252] hover:bg-[#E03E3E] text-white font-medium shadow-sm active:bg-[#C92A2A]'
    default:
      return ''
  }
})

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'text-xs px-2.5 py-1 gap-1.5 h-7 rounded-md'
    case 'lg':
      return 'text-sm px-4.5 py-2.5 gap-2.5 h-10 rounded-lg'
    case 'md':
    default:
      return 'text-xs px-3.5 py-1.5 gap-2 h-8 rounded-lg'
  }
})
</script>

<template>
  <button
    :type="props.type"
    :disabled="props.disabled || props.loading"
    class="inline-flex items-center justify-center font-medium transition-all duration-150 cursor-pointer select-none active:scale-[0.98] disabled:opacity-45 disabled:cursor-not-allowed disabled:pointer-events-none focus:outline-none focus-visible:ring-2 focus-visible:ring-[#3574F0]/50"
    :class="[variantClasses, sizeClasses]"
    @click="emit('click', $event)"
  >
    <!-- Loading spinner -->
    <AxIcon
      v-if="props.loading"
      name="refresh"
      :size="props.size === 'sm' ? 'sm' : 'md'"
      class="animate-spin text-current"
    />

    <!-- Lucide Icon Left -->
    <AxIcon
      v-else-if="activeIconName && props.iconPos === 'left'"
      :name="activeIconName"
      :size="props.size === 'sm' ? 'sm' : 'md'"
      class="text-current"
    />

    <!-- Fallback PrimeIcons Left -->
    <i
      v-else-if="props.icon && props.iconPos === 'left'"
      :class="[props.icon, 'text-current text-xs flex-shrink-0']"
    />

    <!-- Slot Content -->
    <span v-if="$slots.default" class="truncate">
      <slot />
    </span>

    <!-- Lucide Icon Right -->
    <AxIcon
      v-if="!props.loading && activeIconName && props.iconPos === 'right'"
      :name="activeIconName"
      :size="props.size === 'sm' ? 'sm' : 'md'"
      class="text-current"
    />

    <!-- Fallback PrimeIcons Right -->
    <i
      v-else-if="!props.loading && props.icon && props.iconPos === 'right'"
      :class="[props.icon, 'text-current text-xs flex-shrink-0']"
    />
  </button>
</template>
