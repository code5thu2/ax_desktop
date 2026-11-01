<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from '@/i18n'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import type { AuthScreen } from './types'
import { nativeBridge } from '@/services/nativeBridge'

const emit = defineEmits<{
  (e: 'navigate', screen: AuthScreen): void
  (e: 'login-success', user: any): void
  (e: 'guest-mode'): void
}>()

const { t } = useI18n()

const identifier = ref('')
const password = ref('')
const rememberMe = ref(true)
const isLoading = ref(false)

const formError = ref<string | null>(null)
const formSuccess = ref<string | null>(null)
const socialNotice = ref<string | null>(null)

const errors = reactive({
  identifier: '',
  password: '',
})

onMounted(async () => {
  try {
    const status = await nativeBridge.getStatus()
    if (status.rememberedEmail) {
      identifier.value = status.rememberedEmail
    }
  } catch {
    // ignore
  }
})

function clearError(field: keyof typeof errors) {
  errors[field] = ''
  formError.value = null
  socialNotice.value = null
}

function validate(): boolean {
  let isValid = true
  errors.identifier = ''
  errors.password = ''
  formError.value = null
  socialNotice.value = null

  if (!identifier.value.trim()) {
    errors.identifier = t('login.errorIdentifier')
    isValid = false
  }

  if (!password.value) {
    errors.password = t('login.errorPassword')
    isValid = false
  }

  if (!isValid) {
    formError.value = t('login.errorEmpty')
  }

  return isValid
}

async function handleLogin() {
  if (!validate()) return

  isLoading.value = true
  formError.value = null
  formSuccess.value = null

  try {
    const res = await nativeBridge.login({
      email: identifier.value.trim(),
      password: password.value,
    })

    formSuccess.value = t('login.successMsg')

    setTimeout(() => {
      emit('login-success', res.user)
    }, 800)
  } catch (err: any) {
    formError.value = err?.message || String(err)
  } finally {
    isLoading.value = false
  }
}

function handleSocialLogin(provider: string) {
  socialNotice.value = t('login.socialConnecting', { provider })
  setTimeout(() => {
    socialNotice.value = null
  }, 2500)
}

function handleGuestMode() {
  emit('guest-mode')
}
</script>

<template>
  <div class="w-full flex items-center justify-center py-6 px-4">
    <!-- Zero-Jank Container (Static Subtle Radial Backdrops) -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -left-12 w-48 h-48 bg-emerald-500/10 dark:bg-emerald-500/15 rounded-full blur-2xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -right-12 w-48 h-48 bg-teal-500/10 dark:bg-teal-500/15 rounded-full blur-2xl pointer-events-none"></div>

      <div class="relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-300/30 dark:shadow-black/40">
        <!-- Header -->
        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-white shadow-lg shadow-emerald-500/25 mb-3.5">
            <i class="pi pi-shield text-2xl font-bold"></i>
          </div>
          <h1 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-1">
            {{ t('login.title') }}
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            {{ t('login.subtitle') }}
          </p>
        </div>

        <!-- FORM-LEVEL INLINE ALERTS -->
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

        <div
          v-if="socialNotice"
          class="mb-4 p-3 rounded-2xl bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800/60 text-xs text-sky-700 dark:text-sky-300 flex items-center gap-2 animate-slide-down"
        >
          <i class="pi pi-spin pi-spinner text-sky-500 text-xs"></i>
          <span>{{ socialNotice }}</span>
        </div>

        <!-- Social Logins -->
        <div class="grid grid-cols-2 gap-3 mb-5">
          <button
            type="button"
            class="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white hover:bg-slate-50 dark:bg-slate-800/50 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-all cursor-pointer shadow-xs"
            @click="handleSocialLogin('Google')"
          >
            <i class="pi pi-google text-red-500"></i>
            <span>Google</span>
          </button>
          <button
            type="button"
            class="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white hover:bg-slate-50 dark:bg-slate-800/50 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-all cursor-pointer shadow-xs"
            @click="handleSocialLogin('GitHub')"
          >
            <i class="pi pi-github text-slate-900 dark:text-white"></i>
            <span>GitHub</span>
          </button>
        </div>

        <Divider align="center" class="my-5">
          <span class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">{{ t('login.orEmail') }}</span>
        </Divider>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Identifier Input -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              {{ t('login.identifierLabel') }}
            </label>
            <div class="relative">
              <i class="pi pi-user absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs z-10"></i>
              <InputText
                v-model="identifier"
                :invalid="!!errors.identifier"
                :placeholder="t('login.identifierPlaceholder')"
                class="w-full !pl-9 !py-2.5 !text-sm !rounded-xl transition-all"
                @input="clearError('identifier')"
              />
            </div>
            <p v-if="errors.identifier" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-500 dark:text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.identifier }}</span>
            </p>
          </div>

          <!-- Password Input -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300">
                {{ t('login.passwordLabel') }}
              </label>
              <button
                type="button"
                class="text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:underline cursor-pointer"
                @click="emit('navigate', 'forgot')"
              >
                {{ t('login.forgotPassword') }}
              </button>
            </div>
            <Password
              v-model="password"
              :invalid="!!errors.password"
              :placeholder="t('login.passwordPlaceholder')"
              :feedback="false"
              toggleMask
              class="w-full"
              inputClass="w-full !py-2.5 !text-sm !rounded-xl"
              @input="clearError('password')"
            />
            <p v-if="errors.password" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-500 dark:text-rose-400">
              <i class="pi pi-times-circle text-[10px]"></i>
              <span>{{ errors.password }}</span>
            </p>
          </div>

          <!-- Remember me -->
          <div class="flex items-center justify-between pt-1">
            <div class="flex items-center gap-2">
              <Checkbox v-model="rememberMe" :binary="true" inputId="remember-obsidian" />
              <label for="remember-obsidian" class="text-xs text-slate-600 dark:text-slate-400 cursor-pointer select-none">
                {{ t('login.rememberMe') }}
              </label>
            </div>
          </div>

          <!-- Submit Button -->
          <Button
            type="submit"
            :label="t('login.submitBtn')"
            icon="pi pi-arrow-right"
            iconPos="right"
            :loading="isLoading"
            class="w-full !py-3 !rounded-xl !text-sm !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-lg shadow-emerald-500/25 transition-transform active:scale-[0.99] cursor-pointer mt-1"
          />

          <!-- Guest / Offline Mode Button -->
          <button
            type="button"
            class="w-full py-2.5 px-4 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60 text-xs font-semibold text-slate-600 dark:text-slate-300 transition-colors flex items-center justify-center gap-2 cursor-pointer mt-3"
            @click="handleGuestMode"
          >
            <i class="pi pi-desktop text-emerald-500"></i>
            <span>Dùng chế độ Khách / Offline Mode</span>
          </button>
        </form>

        <!-- Footer link -->
        <div class="text-center mt-6 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
          <p class="text-xs text-slate-500 dark:text-slate-400">
            {{ t('login.noAccount') }}
            <button
              type="button"
              class="font-bold text-emerald-600 dark:text-emerald-400 hover:underline cursor-pointer ml-1"
              @click="emit('navigate', 'register')"
            >
              {{ t('login.registerNow') }}
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
