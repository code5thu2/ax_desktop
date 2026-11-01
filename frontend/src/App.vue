<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { useSettingsStore } from '@/features/settings/stores/settingsStore'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { nativeBridge } from '@/services/nativeBridge'
import AuthScreens from '@/features/auth/AuthScreens.vue'
import SplashScreen from '@/components/common/SplashScreen.vue'

const settingsStore = useSettingsStore()
const authStore = useAuthStore()

const isTest = typeof process !== 'undefined' && (process.env?.NODE_ENV === 'test' || Boolean(process.env?.VITEST))
const showSplash = ref(!isTest)

function syncTheme(isDark: boolean) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  if (isDark) {
    root.classList.add('dark', 'app-dark')
  } else {
    root.classList.remove('dark', 'app-dark')
  }

  // Synchronize Windows 11 title bar via NativeBridge (Tauri IPC or fallback)
  nativeBridge.setTheme(isDark)
}

watch(
  () => settingsStore.darkMode,
  (isDark) => {
    syncTheme(isDark)
  },
  { immediate: true }
)

onMounted(async () => {
  syncTheme(settingsStore.darkMode)
  await authStore.checkAuthStatus()
})

function handleSplashComplete() {
  showSplash.value = false
}
</script>

<template>
  <div class="h-screen w-screen flex flex-col bg-white dark:bg-[#18181b] text-slate-900 dark:text-[#ececec] overflow-hidden font-sans transition-colors duration-200 relative">
    <Toast position="bottom-right" />
    <ConfirmDialog />

    <!-- Unified Global Splash Screen (Hiển thị ít nhất 1.5s) -->
    <SplashScreen
      v-if="showSplash || (!isTest && !authStore.isInitialized)"
      :duration="1500"
      @complete="handleSplashComplete"
    />

    <!-- Auth Gate -->
    <AuthScreens
      v-if="!showSplash && authStore.isInitialized && !authStore.isLoggedIn"
      :user="authStore.currentUser"
      @login-success="authStore.setAuthenticated"
      @guest-mode="authStore.setGuestMode"
      @logged-out="authStore.logout"
    />

    <!-- Main Application View -->
    <div v-else-if="!showSplash && authStore.isInitialized && authStore.isLoggedIn" class="relative z-10 flex-1 flex flex-col min-h-0">
      <router-view v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </div>
  </div>
</template>

<style>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.15s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}
</style>
