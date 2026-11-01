<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '@/components/common/AppHeader.vue'
import IntelliJPluginsView from '../components/IntelliJPluginsView.vue'
import SettingsDialog from '@/features/settings/components/SettingsDialog.vue'

const showSettings = ref(false)
</script>

<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-[#fbfbfb] dark:bg-[#1e1e1e] text-slate-800 dark:text-[#ececec] font-sans select-none transition-colors duration-200">
    <!-- Unified Top Navigation Header for MCP Protocol Studio -->
    <AppHeader
      @openSettings="showSettings = true"
    />

    <!-- Main Content Area: IntelliJ Plugins View taking full available space -->
    <main class="flex-1 min-h-0 flex flex-col overflow-hidden bg-white dark:bg-[#1a1a1a]">
      <IntelliJPluginsView />
    </main>

    <!-- Preferences Dialog -->
    <SettingsDialog
      v-model:visible="showSettings"
    />
  </div>
</template>
