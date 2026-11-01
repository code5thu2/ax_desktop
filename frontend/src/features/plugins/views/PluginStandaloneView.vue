<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '@/components/common/AppHeader.vue'
import IntelliJPluginsView from '../components/IntelliJPluginsView.vue'
import SettingsDialog from '@/features/settings/components/SettingsDialog.vue'

const props = withDefaults(
  defineProps<{
    embedded?: boolean
  }>(),
  {
    embedded: false,
  }
)

const showSettings = ref(false)
</script>

<template>
  <div class="h-full w-full flex flex-col overflow-hidden bg-white dark:bg-[#121214] text-slate-900 dark:text-[#ececec] font-sans select-none">
    <!-- Standalone Header only when NOT embedded in AX Portal -->
    <AppHeader
      v-if="!props.embedded"
      @openSettings="showSettings = true"
    />

    <!-- Main Content Area taking full available space -->
    <main class="flex-1 min-h-0 flex flex-col overflow-hidden">
      <IntelliJPluginsView />
    </main>

    <!-- Preferences Dialog for standalone mode -->
    <SettingsDialog
      v-if="!props.embedded"
      v-model:visible="showSettings"
    />
  </div>
</template>
