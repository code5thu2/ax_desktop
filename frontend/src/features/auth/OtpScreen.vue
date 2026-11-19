<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from '@/i18n'
import InputOtp from 'primevue/inputotp'
import type { AuthScreen } from './types'
import { nativeBridge } from '@/services/nativeBridge'
import {
  Shield,
  AlertCircle,
  CheckCircle2,
  Info,
  Zap,
  Loader2,
  Check,
  ArrowLeft,
} from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    email?: string
    username?: string
    password?: string
  }>(),
  {
    email: 'test@aipro.studio',
    username: 'testuser',
    password: 'Password123!',
  }
)

const emit = defineEmits<{
  (e: 'navigate', screen: AuthScreen): void
  (e: 'login-success', user: any): void
}>()

const { t } = useI18n()

// 6-digit OTP value
const otpValue = ref('')
const isVerifying = ref(false)
const countdown = ref(59)
let timer: ReturnType<typeof setInterval> | null = null

const formError = ref<string | null>(null)
const formSuccess = ref<string | null>(null)
const infoNotice = ref<string | null>(null)

function startCountdown() {
  countdown.value = 59
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      if (timer) clearInterval(timer)
    }
  }, 1000)
}

onMounted(() => {
  startCountdown()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function onOtpInput() {
  formError.value = null
  if (otpValue.value.length === 6) {
    handleVerifyOtp()
  }
}

async function handleVerifyOtp() {
  if (otpValue.value.length < 6) {
    formError.value = t('otp.errorLength')
    return
  }

  isVerifying.value = true
  formError.value = null
  formSuccess.value = null

  try {
    const res = await nativeBridge.verifyRegisterOtp(props.email, otpValue.value)

    if (!res.ok) {
      formError.value = res.error || t('otp.errorInvalid')
      return
    }

    formSuccess.value = t('otp.successMsg')

    setTimeout(() => {
      emit('login-success', {
        id: BigInt(Date.now()) as unknown as bigint,
        name: props.username,
        email: props.email,
      })
    }, 1000)
  } catch (err: any) {
    formError.value = err?.message || String(err)
  } finally {
    isVerifying.value = false
  }
}

async function handleResendOtp() {
  if (countdown.value > 0) return

  formError.value = null
  infoNotice.value = null

  try {
    await nativeBridge.requestRegisterOtp(props.email)
    infoNotice.value = t('otp.infoResent')
    startCountdown()
  } catch (err: any) {
    formError.value = err?.message || String(err)
  }
}

function handlePasteDemoCode() {
  otpValue.value = '123456'
  onOtpInput()
}
</script>

<template>
  <div class="w-full flex items-center justify-center py-6 px-4">
    <!-- Ambient radial glow background -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -left-12 w-56 h-56 bg-emerald-500/10 dark:bg-emerald-500/15 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -right-12 w-56 h-56 bg-teal-500/10 dark:bg-teal-500/15 rounded-full blur-3xl pointer-events-none"></div>

      <div class="relative bg-white dark:bg-[#2B2D30] border border-slate-200 dark:border-[#393B40] rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-200/60 dark:shadow-2xl dark:shadow-black/60 text-center transition-colors">
        <!-- Shield Icon with Static Status Dot -->
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 text-white shadow-xl shadow-emerald-500/25 ring-4 ring-emerald-500/10 mb-4 relative">
          <Shield :size="30" :stroke-width="2.2" class="text-white" />
          <span class="absolute -top-1 -right-1 flex h-4 w-4">
            <span class="relative inline-flex rounded-full h-4 w-4 bg-emerald-400 border-2 border-white dark:border-[#2B2D30]"></span>
          </span>
        </div>

        <h1 class="text-2xl font-black text-slate-900 dark:text-[#DFE1E5] tracking-tight mb-1">
          {{ t('otp.title') }}
        </h1>
        <p class="text-xs text-slate-500 dark:text-[#868A91] max-w-xs mx-auto leading-relaxed mb-5 font-medium">
          {{ t('otp.subtitle', { email: props.email }) }}
        </p>

        <!-- ALERTS -->
        <div
          v-if="formError"
          class="mb-4 p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-xs text-rose-700 dark:text-rose-300 flex items-center justify-center gap-2 animate-slide-down text-left"
        >
          <AlertCircle :size="16" class="text-rose-500 dark:text-rose-400 flex-shrink-0" />
          <span>{{ formError }}</span>
        </div>

        <div
          v-if="formSuccess"
          class="mb-4 p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 text-xs text-emerald-800 dark:text-emerald-200 flex items-center justify-center gap-2 animate-slide-down text-left"
        >
          <CheckCircle2 :size="16" class="text-emerald-500 dark:text-emerald-400 flex-shrink-0" />
          <span class="font-medium">{{ formSuccess }}</span>
        </div>

        <div
          v-if="infoNotice"
          class="mb-4 p-3 rounded-2xl bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800/60 text-xs text-sky-700 dark:text-sky-300 flex items-center justify-center gap-2 animate-slide-down text-left"
        >
          <Info :size="15" class="text-sky-500 dark:text-sky-400 flex-shrink-0" />
          <span>{{ infoNotice }}</span>
        </div>

        <!-- InputOtp Control -->
        <div class="my-6 flex justify-center">
          <InputOtp
            v-model="otpValue"
            :length="6"
            integerOnly
            @input="onOtpInput"
            class="gap-2 sm:gap-2.5"
            inputClass="!w-10 !h-12 sm:!w-12 sm:!h-14 !text-xl !font-mono !font-extrabold !rounded-xl !border-slate-300 dark:!border-[#393B40] !bg-slate-50 dark:!bg-[#1E1F22] !text-slate-900 dark:!text-[#DFE1E5] focus:!border-emerald-500 focus:!ring-2 focus:!ring-emerald-500/25 text-center shadow-xs"
          />
        </div>

        <!-- Fast Demo OTP button -->
        <div class="mb-5">
          <button
            type="button"
            class="text-[11px] font-mono text-emerald-700 dark:text-emerald-400 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-950/50 dark:hover:bg-emerald-900/60 border border-emerald-200 dark:border-emerald-800/60 px-3 py-1.5 rounded-lg inline-flex items-center gap-1.5 transition-colors cursor-pointer"
            @click="handlePasteDemoCode"
          >
            <Zap :size="12" class="text-emerald-500" />
            <span>{{ t('otp.quickDemoBtn') }}</span>
          </button>
        </div>

        <!-- Submit Button -->
        <button
          type="button"
          :disabled="isVerifying || otpValue.length < 6"
          class="w-full py-3.5 px-4 rounded-xl text-sm font-bold bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/25 dark:shadow-emerald-500/30 transition-all active:scale-[0.98] cursor-pointer mb-5 disabled:opacity-50 flex items-center justify-center gap-2"
          @click="handleVerifyOtp"
        >
          <Loader2 v-if="isVerifying" :size="16" class="animate-spin" />
          <span>{{ t('otp.submitBtn') }}</span>
          <Check v-if="!isVerifying" :size="15" />
        </button>

        <!-- Resend OTP and Timer -->
        <div class="text-xs text-slate-500 dark:text-[#868A91] flex items-center justify-center gap-1.5">
          <span>{{ t('otp.notReceived') }}</span>
          <button
            v-if="countdown === 0"
            type="button"
            class="font-bold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 hover:underline cursor-pointer"
            @click="handleResendOtp"
          >
            {{ t('otp.resendNow') }}
          </button>
          <span v-else class="font-mono text-slate-400 dark:text-slate-500 font-semibold">
            {{ t('otp.resendIn', { countdown }) }}
          </span>
        </div>

        <!-- Back to Register -->
        <div class="text-center mt-6 pt-4 border-t border-slate-100 dark:border-[#393B40]">
          <button
            type="button"
            class="text-xs font-bold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 hover:underline flex items-center justify-center gap-1.5 mx-auto cursor-pointer"
            @click="emit('navigate', 'register')"
          >
            <ArrowLeft :size="13" />
            <span>{{ t('common.backToRegister') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
