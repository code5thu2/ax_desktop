<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from '@/i18n'
import InputOtp from 'primevue/inputotp'
import Button from 'primevue/button'
import type { AuthScreen } from './types'
import { nativeBridge } from '@/services/nativeBridge'

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
  infoNotice.value = null
  if (otpValue.value.length === 6) {
    handleVerifyOtp()
  }
}

async function handleVerifyOtp() {
  if (otpValue.value.length < 6) {
    formError.value = t('otp.errorIncomplete')
    return
  }

  isVerifying.value = true
  formError.value = null

  try {
    const res = await nativeBridge.verifyRegisterOtp(props.email, otpValue.value)
    if (!res.ok) {
      formError.value = res.error || 'Xác thực OTP thất bại'
      return
    }

    formSuccess.value = t('otp.successMsg', { code: otpValue.value })

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

  otpValue.value = ''
  formError.value = null
  formSuccess.value = null

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
  formError.value = null
  infoNotice.value = t('otp.infoPasted')
  setTimeout(() => {
    handleVerifyOtp()
  }, 300)
}
</script>

<template>
  <div class="w-full flex items-center justify-center py-6 px-4">
    <!-- Zero-Jank Container (Static gradient, no infinite loops) -->
    <div class="relative w-full max-w-md mx-auto">
      <div class="absolute -top-12 -left-12 w-48 h-48 bg-emerald-500/10 dark:bg-emerald-500/15 rounded-full blur-2xl pointer-events-none"></div>
      <div class="absolute -bottom-12 -right-12 w-48 h-48 bg-teal-500/10 dark:bg-teal-500/15 rounded-full blur-2xl pointer-events-none"></div>

      <div class="relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-300/30 dark:shadow-black/40 text-center">
        <!-- Shield Icon with Static Status Dot (Zero Jank) -->
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-white shadow-lg shadow-emerald-500/25 mb-4 relative">
          <i class="pi pi-shield text-3xl font-bold"></i>
          <span class="absolute -top-1 -right-1 flex h-4 w-4">
            <span class="relative inline-flex rounded-full h-4 w-4 bg-emerald-500 border-2 border-white dark:border-slate-900"></span>
          </span>
        </div>

        <h1 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-1">
          {{ t('otp.title') }}
        </h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 max-w-xs mx-auto leading-relaxed mb-5">
          {{ t('otp.subtitle', { email: props.email }) }}
        </p>

        <!-- ALERTS -->
        <div
          v-if="formError"
          class="mb-4 p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-xs text-rose-700 dark:text-rose-300 flex items-center justify-center gap-2 animate-slide-down text-left"
        >
          <i class="pi pi-exclamation-circle text-rose-500 text-sm flex-shrink-0"></i>
          <span>{{ formError }}</span>
        </div>

        <div
          v-if="formSuccess"
          class="mb-4 p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 text-xs text-emerald-800 dark:text-emerald-200 flex items-center justify-center gap-2 animate-slide-down text-left"
        >
          <i class="pi pi-check-circle text-emerald-500 text-sm flex-shrink-0"></i>
          <span class="font-medium">{{ formSuccess }}</span>
        </div>

        <div
          v-if="infoNotice"
          class="mb-4 p-3 rounded-2xl bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800/60 text-xs text-sky-700 dark:text-sky-300 flex items-center justify-center gap-2 animate-slide-down text-left"
        >
          <i class="pi pi-info-circle text-sky-500 text-xs flex-shrink-0"></i>
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
            inputClass="!w-10 !h-12 sm:!w-12 sm:!h-14 !text-xl !font-mono !font-extrabold !rounded-xl !border-slate-300 dark:!border-slate-700 !bg-slate-50 dark:!bg-slate-800/60 focus:!border-emerald-500 focus:!ring-2 focus:!ring-emerald-500/20 text-center"
          />
        </div>

        <!-- Fast Demo OTP button -->
        <div class="mb-5">
          <button
            type="button"
            class="text-[11px] font-mono text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 border border-emerald-200 dark:border-emerald-800/60 px-3 py-1.5 rounded-lg inline-flex items-center gap-1.5 transition-colors cursor-pointer"
            @click="handlePasteDemoCode"
          >
            <i class="pi pi-bolt text-[10px]"></i>
            <span>{{ t('otp.quickDemoCode') }}</span>
          </button>
        </div>

        <!-- Submit Button -->
        <Button
          type="button"
          :label="t('otp.verifyBtn')"
          icon="pi pi-check"
          iconPos="right"
          :loading="isVerifying"
          :disabled="otpValue.length < 6"
          class="w-full !py-3 !rounded-xl !text-sm !font-bold !bg-emerald-500 hover:!bg-emerald-600 !border-0 shadow-lg shadow-emerald-500/25 transition-transform active:scale-[0.99] cursor-pointer mb-5 disabled:opacity-50"
          @click="handleVerifyOtp"
        />

        <!-- Resend OTP and Timer -->
        <div class="text-xs text-slate-500 dark:text-slate-400 flex items-center justify-center gap-1.5">
          <span>{{ t('otp.noCode') }}</span>
          <button
            v-if="countdown === 0"
            type="button"
            class="font-bold text-emerald-600 dark:text-emerald-400 hover:underline cursor-pointer"
            @click="handleResendOtp"
          >
            {{ t('otp.resendNow') }}
          </button>
          <span v-else class="font-mono text-slate-400 font-semibold">
            {{ t('otp.resendIn', { seconds: countdown }) }}
          </span>
        </div>

        <!-- Back to login -->
        <div class="text-center mt-6 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
          <button
            type="button"
            class="text-xs font-bold text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 flex items-center justify-center gap-1.5 mx-auto cursor-pointer transition-colors"
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
