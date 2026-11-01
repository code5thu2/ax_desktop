<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'hero' | number
  glow?: boolean
  breathing?: boolean
  ambient?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  glow: true,
  breathing: false,
  ambient: false,
})

// Dynamic unique ID for SVG definitions to avoid collisions
const uid = Math.random().toString(36).substring(2, 9)
const gradId = `ai-logo-grad-${uid}`
const filterId = `ai-logo-glow-${uid}`

const sizeClasses = computed(() => {
  if (typeof props.size === 'number') {
    return ''
  }
  switch (props.size) {
    case 'xs': return 'w-4 h-4'
    case 'sm': return 'w-6 h-6'
    case 'md': return 'w-8 h-8'
    case 'lg': return 'w-12 h-12'
    case 'xl': return 'w-16 h-16'
    case '2xl': return 'w-20 h-20'
    case 'hero': return 'w-24 h-24'
    default: return 'w-8 h-8'
  }
})

const sizeStyle = computed(() => {
  if (typeof props.size === 'number') {
    return { width: `${props.size}px`, height: `${props.size}px` }
  }
  return {}
})
</script>

<template>
  <div
    class="relative inline-flex items-center justify-center select-none"
    :class="[
      breathing ? 'logo-breathing-wrapper' : '',
    ]"
  >
    <!-- Ambient glowing aura -->
    <div
      v-if="ambient || breathing"
      class="absolute rounded-full pointer-events-none -z-10"
      :class="[
        breathing ? 'aura-breathing bg-gradient-to-tr from-indigo-500/40 via-violet-500/45 to-sky-400/35 blur-2xl' : 'bg-indigo-500/30 blur-xl',
        typeof size === 'number' ? 'w-full h-full scale-150' :
        (size === 'hero' || size === '2xl' ? 'w-36 h-36' : (size === 'xl' || size === 'lg' ? 'w-24 h-24' : 'w-12 h-12'))
      ]"
    ></div>

    <!-- Emblem SVG -->
    <svg
      :class="[
        sizeClasses,
        glow && !breathing ? 'drop-shadow-[0_0_20px_rgba(99,102,241,0.65)]' : '',
        breathing ? 'svg-breathing' : '',
      ]"
      :style="sizeStyle"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient :id="gradId" x1="32" y1="8" x2="32" y2="54" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#38bdf8" />
          <stop offset="35%" stop-color="#6366f1" />
          <stop offset="100%" stop-color="#7c3aed" />
        </linearGradient>
        <filter :id="filterId" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="1.2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <!-- Rounded delta / chevron shape -->
      <path
        d="M 32 8 C 35 8 38 11 40 15 L 53 43 C 55 47.5 53 52 48.5 53.5 C 45 54.5 39 50 32 46 C 25 50 19 54.5 15.5 53.5 C 11 52 9 47.5 11 43 L 24 15 C 26 11 29 8 32 8 Z"
        :fill="`url(#${gradId})`"
        stroke="rgba(255, 255, 255, 0.4)"
        stroke-width="1.2"
      />

      <!-- Glowing 4-point star in center -->
      <path
        d="M 32 19 C 32 25.5 34.5 28 41 28 C 34.5 28 32 30.5 32 37 C 32 30.5 29.5 28 23 28 C 29.5 28 32 25.5 32 19 Z"
        fill="#ffffff"
        :filter="`url(#${filterId})`"
      />
    </svg>
  </div>
</template>

<style scoped>
@keyframes logoPulseBreathing {
  0%, 100% {
    transform: scale(1);
    filter: drop-shadow(0 0 18px rgba(99, 102, 241, 0.55)) drop-shadow(0 0 35px rgba(56, 189, 248, 0.3));
  }
  50% {
    transform: scale(1.09);
    filter: drop-shadow(0 0 34px rgba(99, 102, 241, 0.95)) drop-shadow(0 0 70px rgba(168, 85, 247, 0.7)) drop-shadow(0 0 95px rgba(56, 189, 248, 0.5));
  }
}

@keyframes auraBreathing {
  0%, 100% {
    opacity: 0.35;
    transform: scale(0.9);
  }
  50% {
    opacity: 0.9;
    transform: scale(1.35);
  }
}

.svg-breathing {
  animation: logoPulseBreathing 2.6s ease-in-out infinite;
}

.aura-breathing {
  animation: auraBreathing 2.6s ease-in-out infinite;
}
</style>
