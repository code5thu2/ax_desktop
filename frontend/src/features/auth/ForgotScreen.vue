<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '@/i18n'
import type { AuthScreen } from './types'
import {
  KeyRound,
  Mail,
  Send,
  ArrowLeft,
  CheckCircle2,
  Loader2,
  XCircle,
} from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'navigate', screen: AuthScreen): void
}>()

const { t } = useI18n()

const email = ref('')
const isLoading = ref(false)
const isSubmitted = ref(false)
const emailError = ref<string | null>(null)
const formError = ref<string | null>(null)

function validate(): boolean {
  emailError.value = null
  formError.value = null

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value.trim()) {
    emailError.value = t('forgot.errorEmailEmpty')
    return false
  } else if (!emailRegex.test(email.value.trim())) {
    emailError.value = t('forgot.errorEmail')
    return false
  }
  return true
}

function clearError() {
  emailError.value = null
  formError.value = null
}

async function handleSendResetLink() {
  if (!validate()) return

  isLoading.value = true
  await new Promise((r) => setTimeout(r, 600))
  isLoading.value = false
  isSubmitted.value = true
}
</script>

<template>
  <div class="w-full flex items-center justify-center py-6 px-4">
    <!-- Ambient radial glow background -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -left-12 w-56 h-56 bg-emerald-500/10 dark:bg-emerald-500/15 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -right-12 w-56 h-56 bg-teal-500/10 dark:bg-teal-500/15 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Auth Card (Adaptive Light/Dark Theme) -->
      <div class="relative bg-white dark:bg-[#2B2D30] border border-slate-200 dark:border-[#393B40] rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-200/60 dark:shadow-2xl dark:shadow-black/60 transition-colors">
        <!-- Not Submitted State -->
        <div v-if="!isSubmitted">
          <div class="text-center mb-6">
            <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 text-white shadow-lg shadow-emerald-500/25 ring-4 ring-emerald-500/10 mb-3.5">
              <KeyRound :size="28" :stroke-width="2.2" class="text-white" />
            </div>
            <h1 class="text-2xl font-black text-slate-900 dark:text-[#DFE1E5] tracking-tight mb-1">
              {{ t('forgot.title') }}
            </h1>
            <p class="text-xs text-slate-500 dark:text-[#868A91] font-medium">
              {{ t('forgot.subtitle') }}
            </p>
          </div>

          <form @submit.prevent="handleSendResetLink" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-[#CED0D6] mb-1.5">
                {{ t('forgot.emailLabel') }}
              </label>
              <div class="relative">
                <Mail :size="15" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 dark:text-[#868A91] z-10 pointer-events-none" />
                <input
                  v-model="email"
                  type="email"
                  :placeholder="t('forgot.emailPlaceholder')"
                  class="w-full pl-9 pr-3 py-2.5 text-sm rounded-xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-300 dark:border-[#393B40] text-slate-900 dark:text-[#DFE1E5] placeholder:text-slate-400 dark:placeholder:text-[#6C707E] focus:outline-none focus:ring-2 focus:ring-emerald-500/25 focus:border-emerald-500 focus:bg-white dark:focus:bg-[#1E1F22] transition-all shadow-xs"
                  :class="{ '!border-rose-500 !ring-rose-500/20': !!emailError }"
                  @input="clearError"
                />
              </div>
              <p v-if="emailError" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-600 dark:text-rose-400">
                <XCircle :size="12" />
                <span>{{ emailError }}</span>
              </p>
            </div>

            <button
              type="submit"
              :disabled="isLoading"
              class="w-full py-3.5 px-4 rounded-xl text-sm font-bold bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/25 dark:shadow-emerald-500/30 transition-all active:scale-[0.98] cursor-pointer flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <Loader2 v-if="isLoading" :size="16" class="animate-spin" />
              <span>{{ t('forgot.submitBtn') }}</span>
              <Send v-if="!isLoading" :size="14" />
            </button>
          </form>
        </div>

        <!-- Submitted State (Inline Confirmation Card) -->
        <div v-else class="text-center py-4">
          <div class="w-16 h-16 rounded-2xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center justify-center text-3xl mx-auto mb-4 shadow-sm">
            <CheckCircle2 :size="32" />
          </div>
          <h2 class="text-xl font-bold text-slate-900 dark:text-[#DFE1E5] mb-2">
            {{ t('forgot.successTitle') }}
          </h2>
          <p class="text-xs text-slate-500 dark:text-[#868A91] mb-6 leading-relaxed">
            {{ t('forgot.successSubtitle', { email }) }}
          </p>

          <button
            type="button"
            class="w-full py-2.5 px-4 rounded-xl border border-slate-300 dark:border-[#43454A] hover:border-slate-400 dark:hover:border-slate-500 bg-slate-50 hover:bg-slate-100 dark:bg-[#1E1F22] dark:hover:bg-[#393B40] text-xs font-semibold text-slate-700 dark:text-[#DFE1E5] transition-all flex items-center justify-center gap-2 mb-3 cursor-pointer"
            @click="isSubmitted = false"
          >
            <span>{{ t('forgot.tryAnotherEmail') }}</span>
          </button>
        </div>

        <!-- Back to login footer -->
        <div class="text-center mt-6 pt-4 border-t border-slate-100 dark:border-[#393B40]">
          <button
            type="button"
            class="text-xs font-bold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 hover:underline flex items-center justify-center gap-1.5 mx-auto cursor-pointer"
            @click="emit('navigate', 'login')"
          >
            <ArrowLeft :size="13" />
            <span>{{ t('common.backToLogin') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
