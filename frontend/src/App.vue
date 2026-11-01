<script setup lang="ts">
import { watch, onMounted } from 'vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { useSettingsStore } from '@/features/settings/stores/settingsStore'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { nativeBridge } from '@/services/nativeBridge'
import AuthScreens from '@/features/auth/AuthScreens.vue'

const settingsStore = useSettingsStore()
const authStore = useAuthStore()

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
</script>

<template>
  <div class="h-screen w-screen flex flex-col bg-white dark:bg-[#18181b] text-slate-900 dark:text-[#ececec] overflow-hidden font-sans transition-colors duration-200 relative">
    <Toast position="bottom-right" />
    <ConfirmDialog />

    <!-- Loading Gate -->
    <div
      v-if="!authStore.isInitialized"
      class="flex-1 flex flex-col items-center justify-center gap-3 bg-slate-50 dark:bg-slate-950"
    >
      <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white shadow-lg shadow-emerald-500/25">
        <i class="pi pi-bolt text-2xl font-bold animate-pulse"></i>
      </div>
      <div class="text-sm font-semibold text-slate-600 dark:text-slate-300">
        Khởi tạo AX Desktop...
      </div>
    </div>

    <!-- Auth Gate -->
    <AuthScreens
      v-else-if="!authStore.isLoggedIn"
      :user="authStore.currentUser"
      @login-success="authStore.setAuthenticated"
      @guest-mode="authStore.setGuestMode"
      @logged-out="authStore.logout"
    />

    <!-- Main Application View -->
    <div v-else class="relative z-10 flex-1 flex flex-col min-h-0">
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
