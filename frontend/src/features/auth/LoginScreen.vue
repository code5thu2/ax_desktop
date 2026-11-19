<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from '@/i18n'
import type { AuthScreen } from './types'
import { nativeBridge } from '@/services/nativeBridge'
import {
  Shield,
  User,
  Lock,
  Eye,
  EyeOff,
  Check,
  ArrowRight,
  Loader2,
  AlertCircle,
  CheckCircle2,
  XCircle,
} from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'navigate', screen: AuthScreen): void
  (e: 'login-success', user: any): void
}>()

const { t } = useI18n()

const identifier = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(true)
const isLoading = ref(false)

const formError = ref<string | null>(null)
const formSuccess = ref<string | null>(null)

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
}

function validate(): boolean {
  let isValid = true
  errors.identifier = ''
  errors.password = ''
  formError.value = null

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
</script>

<template>
  <div class="w-full flex items-center justify-center py-6 px-4">
    <!-- Ambient radial glow background -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -left-12 w-56 h-56 bg-emerald-500/10 dark:bg-emerald-500/15 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -right-12 w-56 h-56 bg-teal-500/10 dark:bg-teal-500/15 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Auth Card (Adaptive Light/Dark Theme) -->
      <div class="relative bg-white dark:bg-[#2B2D30] border border-slate-200 dark:border-[#393B40] rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-200/60 dark:shadow-2xl dark:shadow-black/60 transition-colors">
        <!-- Brand Shield Header -->
        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 text-white shadow-lg shadow-emerald-500/25 ring-4 ring-emerald-500/10 mb-3.5">
            <Shield :size="28" :stroke-width="2.2" class="text-white" />
          </div>
          <h1 class="text-2xl font-black text-slate-900 dark:text-[#DFE1E5] tracking-tight mb-1">
            {{ t('login.title') }}
          </h1>
          <p class="text-xs text-slate-500 dark:text-[#868A91] font-medium">
            {{ t('login.subtitle') }}
          </p>
        </div>

        <!-- FORM ALERTS -->
        <div
          v-if="formError"
          class="mb-4 p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-2.5 animate-slide-down"
        >
          <AlertCircle :size="16" class="text-rose-500 dark:text-rose-400 mt-0.5 flex-shrink-0" />
          <span class="leading-relaxed font-medium">{{ formError }}</span>
        </div>

        <div
          v-if="formSuccess"
          class="mb-4 p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 text-xs text-emerald-800 dark:text-emerald-200 flex items-start gap-2.5 animate-slide-down"
        >
          <CheckCircle2 :size="16" class="text-emerald-500 dark:text-emerald-400 mt-0.5 flex-shrink-0" />
          <div>
            <div class="font-bold mb-0.5">{{ t('common.success') }}</div>
            <div class="text-[11px] leading-relaxed text-emerald-700 dark:text-emerald-300">{{ formSuccess }}</div>
          </div>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Identifier Input -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-[#CED0D6] mb-1.5">
              {{ t('login.identifierLabel') }}
            </label>
            <div class="relative">
              <User :size="15" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 dark:text-[#868A91] z-10 pointer-events-none" />
              <input
                v-model="identifier"
                type="text"
                :placeholder="t('login.identifierPlaceholder')"
                class="w-full pl-9 pr-3 py-2.5 text-sm rounded-xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-300 dark:border-[#393B40] text-slate-900 dark:text-[#DFE1E5] placeholder:text-slate-400 dark:placeholder:text-[#6C707E] focus:outline-none focus:ring-2 focus:ring-emerald-500/25 focus:border-emerald-500 focus:bg-white dark:focus:bg-[#1E1F22] transition-all shadow-xs"
                :class="{ '!border-rose-500 !ring-rose-500/20': !!errors.identifier }"
                @input="clearError('identifier')"
              />
            </div>
            <p v-if="errors.identifier" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-600 dark:text-rose-400">
              <XCircle :size="12" />
              <span>{{ errors.identifier }}</span>
            </p>
          </div>

          <!-- Password Input -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-xs font-semibold text-slate-700 dark:text-[#CED0D6]">
                {{ t('login.passwordLabel') }}
              </label>
              <button
                type="button"
                class="text-xs font-semibold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 transition-colors cursor-pointer"
                @click="emit('navigate', 'forgot')"
              >
                {{ t('login.forgotPassword') }}
              </button>
            </div>
            <div class="relative">
              <Lock :size="15" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 dark:text-[#868A91] z-10 pointer-events-none" />
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="t('login.passwordPlaceholder')"
                class="w-full pl-9 pr-10 py-2.5 text-sm rounded-xl bg-slate-50 dark:bg-[#1E1F22] border border-slate-300 dark:border-[#393B40] text-slate-900 dark:text-[#DFE1E5] placeholder:text-slate-400 dark:placeholder:text-[#6C707E] focus:outline-none focus:ring-2 focus:ring-emerald-500/25 focus:border-emerald-500 focus:bg-white dark:focus:bg-[#1E1F22] transition-all font-mono shadow-xs"
                :class="{ '!border-rose-500 !ring-rose-500/20': !!errors.password }"
                @input="clearError('password')"
              />
              <button
                type="button"
                class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 dark:text-[#868A91] dark:hover:text-[#DFE1E5] cursor-pointer p-1.5 transition-colors rounded-lg hover:bg-slate-100 dark:hover:bg-[#393B40]"
                :title="showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
                @click="showPassword = !showPassword"
              >
                <EyeOff v-if="showPassword" :size="15" />
                <Eye v-else :size="15" />
              </button>
            </div>
            <p v-if="errors.password" class="mt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-rose-600 dark:text-rose-400">
              <XCircle :size="12" />
              <span>{{ errors.password }}</span>
            </p>
          </div>

          <!-- Remember me (Bulletproof Custom Checkbox) -->
          <div class="flex items-center justify-between pt-1">
            <div
              class="flex items-center gap-2.5 cursor-pointer select-none group"
              @click="rememberMe = !rememberMe"
            >
              <div
                class="w-4 h-4 rounded-md border flex items-center justify-center transition-all"
                :class="rememberMe ? 'bg-emerald-500 border-emerald-500 text-white shadow-xs' : 'border-slate-300 dark:border-[#43454A] bg-white dark:bg-[#1E1F22] group-hover:border-slate-400 dark:group-hover:border-[#6C707E]'"
              >
                <Check v-if="rememberMe" :size="11" :stroke-width="3" />
              </div>
              <span class="text-xs text-slate-600 dark:text-[#CED0D6] font-medium">
                {{ t('login.rememberMe') }}
              </span>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-3.5 px-4 rounded-xl text-sm font-bold bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/25 dark:shadow-emerald-500/30 transition-all active:scale-[0.98] cursor-pointer flex items-center justify-center gap-2 mt-2 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="isLoading" :size="16" class="animate-spin" />
            <span>{{ t('login.submitBtn') }}</span>
            <ArrowRight v-if="!isLoading" :size="15" />
          </button>
        </form>

        <!-- Footer link -->
        <div class="text-center mt-6 pt-4 border-t border-slate-100 dark:border-[#393B40]">
          <p class="text-xs text-slate-500 dark:text-[#868A91]">
            {{ t('login.noAccount') }}
            <button
              type="button"
              class="font-bold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 hover:underline cursor-pointer ml-1"
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
