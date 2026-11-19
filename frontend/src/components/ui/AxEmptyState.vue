<script setup lang="ts">
import AxButton from './AxButton.vue'

interface Props {
  icon?: string
  title: string
  description?: string
  actionText?: string
  actionIcon?: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: 'pi pi-inbox',
  description: '',
  actionText: '',
  actionIcon: '',
})

const emit = defineEmits<{
  (e: 'action'): void
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center p-8 text-center animate-fade-in my-auto">
    <!-- Icon Container with Glow Ring -->
    <div
      class="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-surface-850 border border-slate-200 dark:border-slate-800 flex items-center justify-center mb-4 shadow-sm"
    >
      <i :class="[props.icon, 'text-2xl text-slate-400 dark:text-slate-500']" />
    </div>

    <!-- Title & Description -->
    <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-1">
      {{ props.title }}
    </h3>
    <p v-if="props.description" class="text-xs text-slate-500 dark:text-slate-400 max-w-sm mb-5 leading-relaxed">
      {{ props.description }}
    </p>

    <!-- Optional CTA Button -->
    <AxButton
      v-if="props.actionText"
      variant="primary"
      size="sm"
      :icon="props.actionIcon"
      @click="emit('action')"
    >
      {{ props.actionText }}
    </AxButton>

    <slot />
  </div>
</template>
