<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '@/i18n'
import type { AuthScreen } from './types'
import { nativeBridge } from '@/services/nativeBridge'
import {
  LogOut,
  AlertTriangle,
  Check,
  Loader2,
  CheckCircle2,
} from 'lucide-vue-next'

const props = defineProps<{
  user?: {
    email?: string
    username?: string
    fullName?: string
  }
}>()

const emit = defineEmits<{
  (e: 'navigate', screen: AuthScreen): void
  (e: 'logged-out'): void
}>()

const { t } = useI18n()

const isLoggingOut = ref(false)
const logoutAllDevices = ref(false)
const logoutSuccess = ref(false)

async function handleLogout() {
  isLoggingOut.value = true

  try {
    await nativeBridge.logout()
    logoutSuccess.value = true
    setTimeout(() => {
      emit('logged-out')
      emit('navigate', 'login')
    }, 1200)
  } catch (e) {
    console.warn('Logout error:', e)
  } finally {
    isLoggingOut.value = false
  }
}

function handleCancel() {
  emit('navigate', 'login')
}
</script>

<template>
  <div class="w-full flex items-center justify-center py-6 px-4">
    <!-- Ambient radial glow background -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -left-12 w-56 h-56 bg-rose-500/10 dark:bg-rose-500/15 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -right-12 w-56 h-56 bg-amber-500/10 dark:bg-amber-500/15 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Auth Card (Adaptive Light/Dark Theme) -->
      <div class="relative bg-white dark:bg-[#2B2D30] border border-slate-200 dark:border-[#393B40] rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-200/60 dark:shadow-2xl dark:shadow-black/60 text-center transition-colors">
        <!-- Not Logged Out State -->
        <div v-if="!logoutSuccess">
          <!-- Sign-out Icon -->
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-rose-500/10 text-rose-500 dark:text-rose-400 border border-rose-500/20 shadow-lg shadow-rose-500/10 mb-4 ring-4 ring-rose-500/10">
            <LogOut :size="30" :stroke-width="2.2" />
          </div>

          <h1 class="text-2xl font-black text-slate-900 dark:text-[#DFE1E5] tracking-tight mb-1">
            {{ t('logout.title') }}
          </h1>
          <p class="text-xs text-slate-500 dark:text-[#868A91] mb-6 font-medium">
            {{ t('logout.subtitle') }}
          </p>

          <!-- User Identity Card -->
          <div class="p-4 rounded-2xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-200 dark:border-[#393B40] flex items-center gap-3.5 mb-6 text-left">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 text-white font-bold text-base flex items-center justify-center shadow-md flex-shrink-0">
              {{ (props.user?.username || 'AX').substring(0, 2).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-slate-900 dark:text-[#DFE1E5] truncate">
                  {{ props.user?.fullName || props.user?.username || 'Người dùng AX' }}
                </span>
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              </div>
              <div class="text-xs text-slate-500 dark:text-[#868A91] font-mono truncate">
                {{ props.user?.email || 'offline@aipro.local' }}
              </div>
            </div>
          </div>

          <!-- Question Prompt -->
          <div class="p-3.5 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-xs text-amber-800 dark:text-amber-300 mb-6 text-left leading-relaxed flex items-start gap-2.5">
            <AlertTriangle :size="16" class="text-amber-500 mt-0.5 flex-shrink-0" />
            <div>
              <div class="font-bold mb-0.5">{{ t('logout.confirmQuestion') }}</div>
              <div class="text-[11px] text-amber-700 dark:text-amber-300/80">{{ t('logout.warningDesc') }}</div>
            </div>
          </div>

          <!-- Checkbox: Logout all devices -->
          <div
            class="p-3.5 rounded-2xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-200 dark:border-[#393B40] text-left mb-6 flex items-center justify-between gap-3 cursor-pointer select-none group"
            @click="logoutAllDevices = !logoutAllDevices"
          >
            <div class="flex-1">
              <span class="text-xs font-semibold text-slate-700 dark:text-[#CED0D6] block">
                {{ t('logout.logoutAllDevices') }}
              </span>
              <p class="text-[10px] text-slate-400 dark:text-[#868A91] mt-0.5">
                {{ t('logout.logoutAllDevicesDesc') }}
              </p>
            </div>
            <div
              class="w-4 h-4 rounded-md border flex items-center justify-center transition-all flex-shrink-0"
              :class="logoutAllDevices ? 'bg-rose-500 border-rose-500 text-white' : 'border-slate-300 dark:border-[#43454A] bg-white dark:bg-[#2B2D30] group-hover:border-slate-400 dark:group-hover:border-slate-500'"
            >
              <Check v-if="logoutAllDevices" :size="11" :stroke-width="3" />
            </div>
          </div>

          <!-- Actions -->
          <div class="space-y-3">
            <button
              type="button"
              :disabled="isLoggingOut"
              class="w-full py-3.5 px-4 rounded-xl text-sm font-bold bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-600/25 transition-all active:scale-[0.98] cursor-pointer flex items-center justify-center gap-2 disabled:opacity-60"
              @click="handleLogout"
            >
              <Loader2 v-if="isLoggingOut" :size="16" class="animate-spin" />
              <LogOut v-else :size="15" />
              <span>{{ t('logout.confirmBtn') }}</span>
            </button>

            <button
              type="button"
              class="w-full py-2.5 px-4 rounded-xl border border-slate-300 dark:border-[#43454A] hover:border-slate-400 dark:hover:border-slate-500 bg-slate-50 hover:bg-slate-100 dark:bg-[#1E1F22] dark:hover:bg-[#393B40] text-xs font-semibold text-slate-700 dark:text-[#DFE1E5] transition-all flex items-center justify-center gap-2 cursor-pointer"
              @click="handleCancel"
            >
              <span>{{ t('common.cancel') }}</span>
            </button>
          </div>
        </div>

        <!-- Success Logged Out State -->
        <div v-else class="py-6">
          <div class="w-16 h-16 rounded-2xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center justify-center text-3xl mx-auto mb-4 shadow-sm ring-4 ring-emerald-500/10">
            <CheckCircle2 :size="32" />
          </div>
          <h2 class="text-xl font-bold text-slate-900 dark:text-[#DFE1E5] mb-2">
            {{ t('logout.successTitle') }}
          </h2>
          <p class="text-xs text-slate-500 dark:text-[#868A91]">
            {{ t('logout.redirecting') }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
