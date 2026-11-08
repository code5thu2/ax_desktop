<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from '@/i18n'
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
const showPassword = ref(false)
const showConfirmPassword = ref(false)

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
    const res = await nativeBridge.requestRegisterOtp(email.value.trim())
    if (!res.ok) {
      formError.value = res.error || 'Gửi OTP thất bại'
      return
    }

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
    <!-- Ambient radial glow background -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -right-12 w-56 h-56 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -left-12 w-56 h-56 bg-teal-500/15 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Obsidian Card -->
      <div class="relative bg-slate-900/95 backdrop-blur-xl border border-slate-800/90 rounded-3xl p-8 sm:p-10 shadow-2xl shadow-black/60">
        <!-- Header -->
        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 text-white shadow-xl shadow-emerald-500/25 ring-4 ring-emerald-500/10 mb-3.5">
            <i class="pi pi-user-plus text-2xl font-bold"></i>
          </div>
          <h1 class="text-2xl font-black text-white tracking-tight mb-1">
            {{ t('register.title') }}
          </h1>
          <p class="text-xs text-slate-400 font-medium">
            {{ t('register.subtitle') }}
          </p>
        </div>

        <!-- FORM-LEVEL ALERTS -->
        <div
          v-if="formError"
          class="mb-4 p-3.5 rounded-2xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-start gap-2.5 animate-slide-down"
        >
          <i class="pi pi-exclamation-circle text-rose-400 text-sm mt-0.5 flex-shrink-0"></i>
          <span class="leading-relaxed font-medium">{{ formError }}</span>
        </div>

        <div
          v-if="formSuccess"
          class="mb-4 p-3.5 rounded-2xl bg-emerald-950/40 border border-emerald-800/60 text-xs text-emerald-200 flex items-start gap-2.5 animate-slide-down"
        >
          <i class="pi pi-check-circle text-emerald-400 text-sm mt-0.5 flex-shrink-0"></i>
          <div>
            <div class="font-bold mb-0.5">{{ t('common.success') }}</div>
            <div class="text-[11px] leading-relaxed text-emerald-300">{{ formSuccess }}</div>
          </div>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <!-- 1. Username -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">
              {{ t('register.usernameLabel') }}
            </label>
            <div class="relative">
              <i class="pi pi-user absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs z-10 pointer-events-none"></i>
              <input
                v-model="username"
                type="text"
                :placeholder="t('register.usernamePlaceholder')"
                class="w-full pl-9 pr-3 py-2.5 text-sm rounded-xl bg-slate-950/90 border border-slate-700/80 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/25 focus:border-emerald-500 transition-all shadow-inner"
                :class="{ '!border-rose-500 !ring-rose-500/20': !!errors.username }"
                @input="clearError('username')"
              />
            </div>
            <p v-if="errors.username" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.username }}</span>
            </p>
          </div>

          <!-- 2. Email -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">
              {{ t('register.emailLabel') }}
            </label>
            <div class="relative">
              <i class="pi pi-envelope absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs z-10 pointer-events-none"></i>
              <input
                v-model="email"
                type="email"
                :placeholder="t('register.emailPlaceholder')"
                class="w-full pl-9 pr-3 py-2.5 text-sm rounded-xl bg-slate-950/90 border border-slate-700/80 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/25 focus:border-emerald-500 transition-all shadow-inner"
                :class="{ '!border-rose-500 !ring-rose-500/20': !!errors.email }"
                @input="clearError('email')"
              />
            </div>
            <p v-if="errors.email" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.email }}</span>
            </p>
          </div>

          <!-- 3. Password -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">
              {{ t('register.passwordLabel') }}
            </label>
            <div class="relative">
              <i class="pi pi-lock absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs z-10 pointer-events-none"></i>
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="t('register.passwordPlaceholder')"
                class="w-full pl-9 pr-10 py-2.5 text-sm rounded-xl bg-slate-950/90 border border-slate-700/80 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/25 focus:border-emerald-500 transition-all font-mono shadow-inner"
                :class="{ '!border-rose-500 !ring-rose-500/20': !!errors.password }"
                @input="clearError('password')"
              />
              <button
                type="button"
                class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white cursor-pointer p-1.5 transition-colors rounded-lg hover:bg-slate-800"
                :title="showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'pi pi-eye-slash' : 'pi pi-eye'" class="text-xs"></i>
              </button>
            </div>
            <p v-if="errors.password" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.password }}</span>
            </p>
          </div>

          <!-- 4. Confirm Password -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">
              {{ t('register.confirmPasswordLabel') }}
            </label>
            <div class="relative">
              <i class="pi pi-lock absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs z-10 pointer-events-none"></i>
              <input
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                :placeholder="t('register.confirmPasswordPlaceholder')"
                class="w-full pl-9 pr-10 py-2.5 text-sm rounded-xl bg-slate-950/90 border border-slate-700/80 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/25 focus:border-emerald-500 transition-all font-mono shadow-inner"
                :class="{ '!border-rose-500 !ring-rose-500/20': !!errors.confirmPassword }"
                @input="clearError('confirmPassword')"
              />
              <button
                type="button"
                class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white cursor-pointer p-1.5 transition-colors rounded-lg hover:bg-slate-800"
                :title="showConfirmPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <i :class="showConfirmPassword ? 'pi pi-eye-slash' : 'pi pi-eye'" class="text-xs"></i>
              </button>
            </div>
            <p v-if="errors.confirmPassword" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.confirmPassword }}</span>
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-3.5 px-4 rounded-xl text-sm font-bold bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/30 transition-all active:scale-[0.98] cursor-pointer flex items-center justify-center gap-2 mt-2 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <i v-if="isLoading" class="pi pi-spinner animate-spin text-sm"></i>
            <span>{{ t('register.submitBtn') }}</span>
            <i v-if="!isLoading" class="pi pi-arrow-right text-xs"></i>
          </button>
        </form>

        <!-- Footer link -->
        <div class="text-center mt-6 pt-4 border-t border-slate-800/80">
          <p class="text-xs text-slate-400">
            {{ t('register.hasAccount') }}
            <button
              type="button"
              class="font-bold text-emerald-400 hover:text-emerald-300 hover:underline cursor-pointer ml-1"
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
