<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from '@/i18n'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import type { AuthScreen } from './types'
import { nativeBridge } from '@/services/nativeBridge'

const emit = defineEmits<{
  (e: 'navigate', screen: AuthScreen): void
  (e: 'registered', payload: { email: string; username: string; password: string }): void
}>()

const { t } = useI18n()

// Fields: username, email, password, confirmPassword
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const isLoading = ref(false)
const formError = ref<string | null>(null)
const formSuccess = ref<string | null>(null)

const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

function clearError(field: keyof typeof errors) {
  errors[field] = ''
  formError.value = null
}

function validate(): boolean {
  let isValid = true
  errors.username = ''
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''
  formError.value = null

  if (!username.value.trim()) {
    errors.username = t('register.errorUsernameEmpty')
    isValid = false
  } else if (username.value.trim().length < 3) {
    errors.username = t('register.errorUsername')
    isValid = false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value.trim()) {
    errors.email = t('register.errorEmailEmpty')
    isValid = false
  } else if (!emailRegex.test(email.value.trim())) {
    errors.email = t('register.errorEmail')
    isValid = false
  }

  if (!password.value) {
    errors.password = t('register.errorPasswordEmpty')
    isValid = false
  } else if (password.value.length < 6) {
    errors.password = t('register.errorPassword')
    isValid = false
  }

  if (!confirmPassword.value) {
    errors.confirmPassword = t('register.errorConfirmPasswordEmpty')
    isValid = false
  } else if (confirmPassword.value !== password.value) {
    errors.confirmPassword = t('register.errorConfirmPasswordMismatch')
    isValid = false
  }

  if (!isValid) {
    formError.value = t('register.errorEmpty')
  }

  return isValid
}

async function handleRegister() {
  if (!validate()) return

  isLoading.value = true
  formError.value = null

  try {
    await nativeBridge.requestRegisterOtp({
      email: email.value.trim(),
      username: username.value.trim(),
      password: password.value,
    })

    formSuccess.value = t('register.successMsg')

    setTimeout(() => {
      emit('registered', {
        email: email.value.trim(),
        username: username.value.trim(),
        password: password.value,
      })
      emit('navigate', 'otp')
    }, 1000)
  } catch (err: any) {
    formError.value = err?.message || String(err)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="w-full flex items-center justify-center py-6 px-4">
    <!-- Zero-Jank Container (Static gradient, no infinite keyframes) -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -right-12 w-48 h-48 bg-emerald-500/10 dark:bg-emerald-500/15 rounded-full blur-2xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -left-12 w-48 h-48 bg-teal-500/10 dark:bg-teal-500/15 rounded-full blur-2xl pointer-events-none"></div>

      <div class="relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-300/30 dark:shadow-black/40">
        <!-- Header -->
        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-white shadow-lg shadow-emerald-500/25 mb-3.5">
            <i class="pi pi-user-plus text-2xl font-bold"></i>
          </div>
          <h1 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-1">
            {{ t('register.title') }}
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            {{ t('register.subtitle') }}
          </p>
        </div>

        <!-- FORM-LEVEL ALERTS -->
        <div
          v-if="formError"
          class="mb-4 p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-2.5 animate-slide-down"
        >
          <i class="pi pi-exclamation-circle text-rose-500 text-sm mt-0.5 flex-shrink-0"></i>
          <span class="leading-relaxed font-medium">{{ formError }}</span>
        </div>

        <div
          v-if="formSuccess"
          class="mb-4 p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 text-xs text-emerald-800 dark:text-emerald-200 flex items-start gap-2.5 animate-slide-down"
        >
          <i class="pi pi-check-circle text-emerald-500 text-sm mt-0.5 flex-shrink-0"></i>
          <div>
            <div class="font-bold mb-0.5">{{ t('common.success') }}</div>
            <div class="text-[11px] leading-relaxed text-emerald-700 dark:text-emerald-300">{{ formSuccess }}</div>
          </div>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <!-- 1. Username -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              {{ t('register.usernameLabel') }}
            </label>
            <div class="relative">
              <i class="pi pi-user absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs z-10"></i>
              <InputText
                v-model="username"
                :invalid="!!errors.username"
                :placeholder="t('register.usernamePlaceholder')"
                class="w-full !pl-9 !py-2.5 !text-sm !rounded-xl transition-all"
                @input="clearError('username')"
              />
            </div>
            <p v-if="errors.username" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-500 dark:text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.username }}</span>
            </p>
          </div>

          <!-- 2. Email -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              {{ t('register.emailLabel') }}
            </label>
            <div class="relative">
              <i class="pi pi-envelope absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs z-10"></i>
              <InputText
                v-model="email"
                type="email"
                :invalid="!!errors.email"
                :placeholder="t('register.emailPlaceholder')"
                class="w-full !pl-9 !py-2.5 !text-sm !rounded-xl transition-all"
                @input="clearError('email')"
              />
            </div>
            <p v-if="errors.email" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-500 dark:text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.email }}</span>
            </p>
          </div>

          <!-- 3. Password with PrimeVue Strength Meter -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              {{ t('register.passwordLabel') }}
            </label>
            <Password
              v-model="password"
              :invalid="!!errors.password"
              :placeholder="t('register.passwordPlaceholder')"
              :promptLabel="t('register.pwdPrompt')"
              :weakLabel="t('register.pwdWeak')"
              :mediumLabel="t('register.pwdMedium')"
              :strongLabel="t('register.pwdStrong')"
              toggleMask
              class="w-full"
              inputClass="w-full !py-2.5 !text-sm !rounded-xl"
              @input="clearError('password')"
            >
              <template #footer>
                <div class="p-2 text-[11px] text-slate-600 dark:text-slate-400">
                  <p class="font-semibold mb-1 text-slate-800 dark:text-slate-200">{{ t('register.pwdTipsTitle') }}</p>
                  <ul class="list-disc pl-4 space-y-0.5">
                    <li>{{ t('register.pwdTip1') }}</li>
                    <li>{{ t('register.pwdTip2') }}</li>
                  </ul>
                </div>
              </template>
            </Password>
            <p v-if="errors.password" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-500 dark:text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.password }}</span>
            </p>
          </div>

          <!-- 4. Confirm Password -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              {{ t('register.confirmPasswordLabel') }}
            </label>
            <Password
              v-model="confirmPassword"
              :invalid="!!errors.confirmPassword"
              :placeholder="t('register.confirmPasswordPlaceholder')"
              :feedback="false"
              toggleMask
              class="w-full"
              inputClass="w-full !py-2.5 !text-sm !rounded-xl"
              @input="clearError('confirmPassword')"
            />
            <p v-if="errors.confirmPassword" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-500 dark:text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.confirmPassword }}</span>
            </p>
          </div>

          <!-- Submit Button -->
          <Button
            type="submit"
            :label="t('register.submitBtn')"
            icon="pi pi-arrow-right"
            iconPos="right"
            :loading="isLoading"
            class="w-full !py-3 !rounded-xl !text-sm !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-lg shadow-emerald-500/25 transition-transform active:scale-[0.99] cursor-pointer mt-2"
          />
        </form>

        <div class="text-center mt-6 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
          <p class="text-xs text-slate-500 dark:text-slate-400">
            {{ t('register.hasAccount') }}
            <button
              type="button"
              class="font-bold text-emerald-600 dark:text-emerald-400 hover:underline cursor-pointer ml-1"
              @click="emit('navigate', 'login')"
            >
              {{ t('register.loginNow') }}
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-slide-down {
  animation: slideDown 0.25s ease-out forwards;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
