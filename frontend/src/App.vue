<script setup lang="ts">
import { watch, onMounted } from 'vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { useSettingsStore } from '@/features/settings/stores/settingsStore'
import { nativeBridge } from '@/services/nativeBridge'

const settingsStore = useSettingsStore()

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

onMounted(() => {
  syncTheme(settingsStore.darkMode)
  if (typeof window !== 'undefined') {
    window.addEventListener('pywebviewready', () => {
      syncTheme(settingsStore.darkMode)
    })
  }
})
</script>

<template>
  <div class="h-screen w-screen flex flex-col bg-white dark:bg-[#212121] text-slate-900 dark:text-[#ececec] overflow-hidden font-sans transition-colors duration-200 relative">
    <Toast position="bottom-right" />
    <ConfirmDialog />
    <div class="relative z-10 flex-1 flex flex-col min-h-0">
      <router-view v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </div>
  </div>
</template>
