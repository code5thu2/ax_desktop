<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from '@/i18n'
import { nativeBridge } from '@/services/nativeBridge'

interface Props {
  duration?: number
}

const props = withDefaults(defineProps<Props>(), {
  duration: 1500, // Hiển thị ít nhất 1.5s
})

const emit = defineEmits<{
  (e: 'complete'): void
}>()

const { t } = useI18n()

const progress = ref(0)
const statusText = ref(t('splash.step1'))
const appVersion = ref('1.0.2')
let animationTimer: ReturnType<typeof setInterval> | null = null

const steps = [
  { at: 0, key: 'splash.step1' },
  { at: 25, key: 'splash.step2' },
  { at: 60, key: 'splash.step3' },
  { at: 90, key: 'splash.step4' },
]

onMounted(async () => {
  try {
    const info = await nativeBridge.getAppInfo()
    if (info?.version) {
      appVersion.value = info.version
    }
  } catch {}

  const isTest = typeof process !== 'undefined' && (process.env?.NODE_ENV === 'test' || Boolean(process.env?.VITEST))
  const actualDuration = isTest ? 100 : Math.max(1500, props.duration)

  const startTime = Date.now()
  const interval = 25 // 40fps progress tick

  animationTimer = setInterval(() => {
    const elapsed = Date.now() - startTime
    const percent = Math.min(100, Math.floor((elapsed / actualDuration) * 100))
    progress.value = percent

    // Update dynamic status texts
    for (let i = steps.length - 1; i >= 0; i--) {
      if (percent >= steps[i].at) {
        statusText.value = t(steps[i].key)
        break
      }
    }

    if (percent >= 100) {
      if (animationTimer) {
        clearInterval(animationTimer)
        animationTimer = null
      }
      setTimeout(() => {
        emit('complete')
      }, isTest ? 10 : 200)
    }
  }, interval)
})

onUnmounted(() => {
  if (animationTimer) {
    clearInterval(animationTimer)
  }
})
</script>

<template>
  <div
    data-testid="splash-screen"
    class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#090A0F] text-slate-100 select-none overflow-hidden font-sans"
  >
    <!-- Atmospheric Ambient Auras -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[550px] bg-gradient-to-tr from-emerald-600/20 via-teal-600/15 to-transparent rounded-full blur-3xl"></div>
    </div>

    <!-- Centered Content -->
    <div class="relative z-10 flex flex-col items-center text-center max-w-md w-full px-6">
      <!-- Glowing Hexacore Logo -->
      <div class="mb-6 relative flex items-center justify-center">
        <div class="w-20 h-20 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 p-0.5 shadow-2xl shadow-emerald-500/30 animate-pulse">
          <div class="w-full h-full bg-[#0d1117] rounded-[14px] flex items-center justify-center text-white">
            <svg class="w-10 h-10 drop-shadow-[0_0_12px_rgba(16,185,129,0.8)]" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="splash-logo-grad" x1="12" y1="12" x2="52" y2="52" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#10b981" />
                  <stop offset="50%" stop-color="#14b8a6" />
                  <stop offset="100%" stop-color="#38bdf8" />
                </linearGradient>
              </defs>
              <path d="M 32 8 L 52 19 L 52 45 L 32 56 L 12 45 L 12 19 Z" fill="url(#splash-logo-grad)" stroke="rgba(255, 255, 255, 0.4)" stroke-width="1.5" />
              <path d="M 32 20 L 32 44 M 20 27 L 44 37 M 44 27 L 20 37" stroke="#ffffff" stroke-width="2" stroke-linecap="round" />
            </svg>
          </div>
        </div>
      </div>

      <!-- App Title with Badges -->
      <div class="flex items-center justify-center gap-2 mb-1.5 flex-wrap">
        <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-emerald-300 bg-clip-text text-transparent">
          AX Desktop
        </h1>
        <span class="inline-flex items-center justify-center leading-none text-[9px] font-bold tracking-wider px-2 py-1 rounded-full text-center bg-emerald-950/80 text-emerald-300 border border-emerald-800/40 font-mono">
          AIPRO SUPER STUDIO
        </span>
        <span class="hidden text-[9px] font-mono">ENTERPRISE</span>
      </div>

      <p class="text-xs text-slate-400 font-medium mb-5 tracking-wide">
        Skill Marketplace &bull; MCP Protocol Studio
      </p>

      <!-- Current Step Status -->
      <div class="h-6 flex items-center justify-center mb-4">
        <p class="text-xs text-emerald-400/90 font-medium transition-all duration-200">
          {{ statusText }}
        </p>
      </div>

      <!-- Sleek Glowing Progress Bar -->
      <div class="w-64 sm:w-72 h-1.5 rounded-full bg-white/[0.08] overflow-hidden relative mb-2.5 shadow-inner">
        <div
          class="h-full rounded-full bg-gradient-to-r from-emerald-400 via-teal-400 to-sky-400 transition-all duration-75 ease-out shadow-[0_0_14px_rgba(16,185,129,0.9)]"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>

      <!-- Percentage Indicator -->
      <div class="text-[11px] font-mono text-slate-500 tracking-wider">
        {{ progress }}%
      </div>
    </div>

    <!-- Bottom Footer Tag -->
    <div class="absolute bottom-6 inset-x-0 text-center">
      <span class="text-[10px] text-slate-500 font-mono tracking-wide">
        AX Desktop • Super App Architecture • v{{ appVersion }}
      </span>
    </div>
  </div>
</template>
