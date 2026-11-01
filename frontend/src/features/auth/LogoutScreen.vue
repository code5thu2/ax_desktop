<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '@/i18n'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import type { AuthScreen } from './types'
import { nativeBridge } from '@/services/nativeBridge'

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
    <!-- Zero-Jank Container (Static gradient, no infinite loops) -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -left-12 w-48 h-48 bg-rose-500/10 dark:bg-rose-500/15 rounded-full blur-2xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -right-12 w-48 h-48 bg-amber-500/10 dark:bg-amber-500/15 rounded-full blur-2xl pointer-events-none"></div>

      <div class="relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-300/30 dark:shadow-black/40 text-center">
        <!-- Not Logged Out State -->
        <div v-if="!logoutSuccess">
          <!-- Sign-out Icon -->
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-rose-500/10 text-rose-500 border border-rose-500/20 shadow-lg shadow-rose-500/10 mb-4">
            <i class="pi pi-power-off text-3xl font-bold"></i>
          </div>

          <h1 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-1">
            {{ t('logout.title') }}
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mb-6">
            {{ t('logout.subtitle') }}
          </p>

          <!-- User Identity Card -->
          <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 flex items-center gap-3.5 mb-6 text-left">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-white font-bold text-base flex items-center justify-center shadow-md flex-shrink-0">
              {{ (props.user?.username || 'AX').substring(0, 2).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-slate-900 dark:text-white truncate">
                  {{ props.user?.fullName || props.user?.username || 'Người dùng AX' }}
                </span>
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              </div>
              <div class="text-xs text-slate-500 dark:text-slate-400 font-mono truncate">
                {{ props.user?.email || 'thang@aipro.studio' }}
              </div>
            </div>
          </div>

          <!-- Question Prompt -->
          <div class="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-700 dark:text-amber-300 mb-6 text-left leading-relaxed flex items-start gap-2.5">
            <i class="pi pi-exclamation-triangle text-amber-500 text-sm mt-0.5 flex-shrink-0"></i>
            <div>
              <div class="font-bold mb-0.5">{{ t('logout.confirmQuestion') }}</div>
              <div class="text-[11px] text-amber-600/90 dark:text-amber-300/80">{{ t('logout.warningDesc') }}</div>
            </div>
          </div>

          <!-- Checkbox: Logout all devices -->
          <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60 text-left mb-6 flex items-center justify-between gap-3">
            <div class="flex-1">
              <label for="logout-all" class="text-xs font-semibold text-slate-700 dark:text-slate-300 block cursor-pointer">
                {{ t('logout.logoutAllDevices') }}
              </label>
              <p class="text-[10px] text-slate-400 mt-0.5">
                {{ t('logout.logoutAllDesc') }}
              </p>
            </div>
            <Checkbox v-model="logoutAllDevices" :binary="true" inputId="logout-all" />
          </div>

          <!-- Actions -->
          <div class="space-y-3">
            <Button
              type="button"
              :label="t('logout.confirmBtn')"
              icon="pi pi-power-off"
              iconPos="right"
              :loading="isLoggingOut"
              class="w-full !py-3 !rounded-xl !text-sm !font-bold !bg-rose-500 hover:!bg-rose-600 !border-0 shadow-lg shadow-rose-500/25 transition-transform active:scale-[0.99] cursor-pointer"
              @click="handleLogout"
            />
            <Button
              type="button"
              :label="t('logout.cancelBtn')"
              variant="outlined"
              class="w-full !py-2.5 !rounded-xl !text-xs !font-semibold cursor-pointer"
              @click="handleCancel"
            />
          </div>
        </div>

        <!-- Logged Out Successfully -->
        <div v-else class="py-6">
          <div class="w-16 h-16 rounded-2xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 flex items-center justify-center text-3xl mx-auto mb-4 shadow-sm">
            <i class="pi pi-check"></i>
          </div>
          <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">
            {{ t('logout.successTitle') }}
          </h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 mb-6">
            {{ t('logout.successDesc') }}
          </p>
          <div class="inline-flex items-center gap-2 text-xs text-slate-400">
            <i class="pi pi-spin pi-spinner text-xs"></i>
            <span>{{ t('logout.redirecting') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
