<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '@/i18n'
import type { AuthScreen, LocaleLang } from './types'
import LoginScreen from './LoginScreen.vue'
import RegisterScreen from './RegisterScreen.vue'
import OtpScreen from './OtpScreen.vue'
import ForgotScreen from './ForgotScreen.vue'
import LogoutScreen from './LogoutScreen.vue'

const props = defineProps<{
  user?: any
  initialScreen?: AuthScreen
}>()

const emit = defineEmits<{
  (e: 'login-success', user: any): void
  (e: 'guest-mode'): void
  (e: 'logged-out'): void
}>()

const { locale, setLocale } = useI18n()

const currentScreen = ref<AuthScreen>(props.initialScreen || 'login')

const pendingRegisterData = ref<{
  email: string
  username: string
  password: string
}>({
  email: '',
  username: '',
  password: '',
})

function handleNavigate(screen: AuthScreen) {
  currentScreen.value = screen
}

function handleRegistered(payload: { email: string; username: string; password: string }) {
  pendingRegisterData.value = payload
}

function handleLoginSuccess(user: any) {
  emit('login-success', user)
}

function handleGuestMode() {
  emit('guest-mode')
}

function handleLoggedOut() {
  emit('logged-out')
}

function switchLang(lang: LocaleLang) {
  setLocale(lang)
}
</script>

<template>
  <div class="min-h-screen w-full bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 flex flex-col justify-between transition-colors duration-300">
    <!-- Top Bar with Brand & Language Switcher -->
    <header class="w-full max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
          <i class="pi pi-bolt text-lg font-bold"></i>
        </div>
        <div>
          <span class="font-extrabold text-base tracking-tight text-slate-900 dark:text-white">AX Desktop</span>
          <span class="ml-2 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            AIPRO Ecosystem
          </span>
        </div>
      </div>

      <!-- Language selector -->
      <div class="flex items-center gap-1.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-1 shadow-xs">
        <button
          type="button"
          class="px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="locale === 'vi' ? 'bg-emerald-500 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="switchLang('vi')"
        >
          VI
        </button>
        <button
          type="button"
          class="px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="locale === 'en' ? 'bg-emerald-500 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="switchLang('en')"
        >
          EN
        </button>
        <button
          type="button"
          class="px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="locale === 'ko' ? 'bg-emerald-500 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
          @click="switchLang('ko')"
        >
          KO
        </button>
      </div>
    </header>

    <!-- Main Auth Screen Content -->
    <main class="flex-1 flex items-center justify-center">
      <LoginScreen
        v-if="currentScreen === 'login'"
        @navigate="handleNavigate"
        @login-success="handleLoginSuccess"
        @guest-mode="handleGuestMode"
      />

      <RegisterScreen
        v-else-if="currentScreen === 'register'"
        @navigate="handleNavigate"
        @registered="handleRegistered"
      />

      <OtpScreen
        v-else-if="currentScreen === 'otp'"
        :email="pendingRegisterData.email || 'thang@aipro.studio'"
        :username="pendingRegisterData.username || 'thanglv'"
        :password="pendingRegisterData.password || 'Password123!'"
        @navigate="handleNavigate"
        @login-success="handleLoginSuccess"
      />

      <ForgotScreen
        v-else-if="currentScreen === 'forgot'"
        @navigate="handleNavigate"
      />

      <LogoutScreen
        v-else-if="currentScreen === 'logout'"
        :user="props.user"
        @navigate="handleNavigate"
        @logged-out="handleLoggedOut"
      />
    </main>

    <!-- Footer -->
    <footer class="w-full text-center py-4 text-xs text-slate-400 dark:text-slate-600">
      AX Desktop &copy; 2026 AIPRO Studio &bull; Zero-Jank Native Experience
    </footer>
  </div>
</template>
