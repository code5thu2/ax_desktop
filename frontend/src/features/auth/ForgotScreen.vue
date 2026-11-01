<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '@/i18n'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import type { AuthScreen } from './types'

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
    <!-- Zero-Jank Container (Static gradient, no infinite loops) -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -left-12 w-48 h-48 bg-emerald-500/10 dark:bg-emerald-500/15 rounded-full blur-2xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -right-12 w-48 h-48 bg-teal-500/10 dark:bg-teal-500/15 rounded-full blur-2xl pointer-events-none"></div>

      <div class="relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-300/30 dark:shadow-black/40">
        <!-- Not Submitted State -->
        <div v-if="!isSubmitted">
          <div class="text-center mb-6">
            <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-white shadow-lg shadow-emerald-500/25 mb-3.5">
              <i class="pi pi-key text-2xl font-bold"></i>
            </div>
            <h1 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-1">
              {{ t('forgot.title') }}
            </h1>
            <p class="text-xs text-slate-500 dark:text-slate-400">
              {{ t('forgot.subtitle') }}
            </p>
          </div>

          <!-- Form Error Alert -->
          <div
            v-if="formError"
            class="mb-4 p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-xs text-rose-700 dark:text-rose-300 flex items-center gap-2"
          >
            <i class="pi pi-exclamation-circle text-rose-500 text-sm flex-shrink-0"></i>
            <span>{{ formError }}</span>
          </div>

          <form @submit.prevent="handleSendResetLink" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                {{ t('forgot.emailLabel') }}
              </label>
              <div class="relative">
                <i class="pi pi-envelope absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs z-10"></i>
                <InputText
                  v-model="email"
                  type="email"
                  :invalid="!!emailError"
                  :placeholder="t('forgot.emailPlaceholder')"
                  class="w-full !pl-9 !py-2.5 !text-sm !rounded-xl transition-all"
                  @input="clearError"
                />
              </div>
              <p v-if="emailError" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-500 dark:text-rose-400">
                <i class="pi pi-times-circle text-[10px]"></i>
                <span>{{ emailError }}</span>
              </p>
            </div>

            <Button
              type="submit"
              :label="t('forgot.submitBtn')"
              icon="pi pi-send"
              iconPos="right"
              :loading="isLoading"
              class="w-full !py-3 !rounded-xl !text-sm !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-lg shadow-emerald-500/25 transition-transform active:scale-[0.99] cursor-pointer"
            />
          </form>
        </div>

        <!-- Submitted State (Inline Confirmation Card) -->
        <div v-else class="text-center py-4">
          <div class="w-16 h-16 rounded-2xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 flex items-center justify-center text-3xl mx-auto mb-4 shadow-sm">
            <i class="pi pi-check-circle"></i>
          </div>
          <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">
            {{ t('forgot.successTitle') }}
          </h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 mb-6 leading-relaxed">
            {{ t('forgot.successSubtitle', { email }) }}
          </p>

          <Button
            type="button"
            :label="t('forgot.tryAnotherEmail')"
            variant="outlined"
            class="w-full !py-2.5 !rounded-xl !text-xs !font-semibold mb-3 cursor-pointer"
            @click="isSubmitted = false"
          />
        </div>

        <!-- Back to login footer -->
        <div class="text-center mt-6 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
          <button
            type="button"
            class="text-xs font-bold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center justify-center gap-1.5 mx-auto cursor-pointer"
            @click="emit('navigate', 'login')"
          >
            <i class="pi pi-arrow-left text-[10px]"></i>
            <span>{{ t('common.backToLogin') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
