<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AppLogo from '@/components/common/AppLogo.vue'

interface Props {
  duration?: number
}

const props = withDefaults(defineProps<Props>(), {
  duration: 3000,
})

const emit = defineEmits<{
  (e: 'complete'): void
}>()

const progress = ref(0)
const statusText = ref('Đang khởi động MCP Protocol Studio...')
let animationTimer: ReturnType<typeof setInterval> | null = null

const steps = [
  { at: 0, text: 'Đang khởi tạo MCP Protocol Studio...' },
  { at: 25, text: 'Đang tải danh mục MCP Servers & Tools...' },
  { at: 60, text: 'Đang kết nối MCP Pure HTTP Gateway...' },
  { at: 90, text: 'Sắp hoàn tất, sẵn sàng làm việc...' },
]

onMounted(() => {
  const isTest = typeof process !== 'undefined' && (process.env?.NODE_ENV === 'test' || Boolean(process.env?.VITEST))
  const actualDuration = isTest ? 100 : props.duration

  const startTime = Date.now()
  const interval = 25 // 40fps progress tick

  animationTimer = setInterval(() => {
    const elapsed = Date.now() - startTime
    const percent = Math.min(100, Math.floor((elapsed / actualDuration) * 100))
    progress.value = percent

    // Update dynamic status texts
    for (let i = steps.length - 1; i >= 0; i--) {
      if (percent >= steps[i].at) {
        statusText.value = steps[i].text
        break
      }
    }

    if (percent >= 100) {
      if (animationTimer) {
        clearInterval(animationTimer)
        animationTimer = null
      }
      // Small pause at 100% before triggering exit transition
      setTimeout(() => {
        emit('complete')
      }, isTest ? 10 : 250)
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
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-violet-600/25 via-indigo-600/15 to-transparent rounded-full blur-3xl"></div>
    </div>

    <!-- Centered Content -->
    <div class="relative z-10 flex flex-col items-center text-center max-w-md w-full px-6">
      <!-- Breathing Logo -->
      <div class="mb-7 relative flex items-center justify-center">
        <AppLogo :size="100" :ambient="true" :breathing="true" />
      </div>

      <!-- App Title with ENTERPRISE badge -->
      <div class="flex items-center justify-center gap-2.5 mb-2">
        <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-emerald-300 bg-clip-text text-transparent">
          MCP PROTOCOL STUDIO
        </h1>
        <span class="inline-flex items-center justify-center leading-none text-[9px] font-bold tracking-wider px-2 py-1 rounded-full text-center bg-emerald-950/80 text-emerald-300 border border-emerald-800/40 font-mono">
          ENTERPRISE
        </span>
      </div>

      <!-- Current Step Status -->
      <div class="h-6 flex items-center justify-center mb-5">
        <p class="text-xs text-slate-400 font-medium transition-all duration-200">
          {{ statusText }}
        </p>
      </div>

      <!-- Sleek Glowing Progress Bar -->
      <div class="w-64 sm:w-72 h-1.5 rounded-full bg-white/[0.08] overflow-hidden relative mb-3 shadow-inner">
        <div
          class="h-full rounded-full bg-gradient-to-r from-sky-400 via-indigo-500 to-violet-500 transition-all duration-75 ease-out shadow-[0_0_12px_rgba(99,102,241,0.8)]"
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
        MCP Protocol Studio Native • Enterprise Edition • v1.0.0
      </span>
    </div>
  </div>
</template>
