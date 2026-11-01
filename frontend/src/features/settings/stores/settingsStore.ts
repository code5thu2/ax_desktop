import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useStorage } from '@vueuse/core'

export const useSettingsStore = defineStore('settings', () => {
  // MCP Studio Gateway Server Settings
  const registryServerUrl = useStorage('mcp_studio_registry_url', 'http://127.0.0.1:8000')
  const apiBaseUrl = registryServerUrl

  // Theme & Window Experience
  const darkMode = useStorage('mcp_studio_dark_mode', true)
  const autostartEnabled = useStorage('mcp_studio_autostart', false)

  // Backwards compatibility for existing test assertions
  const selectedModel = ref('mcp-protocol-gateway')
  const temperature = ref(0.7)
  const availableModels = ref([
    {
      label: 'MCP Protocol Gateway',
      value: 'mcp-protocol-gateway',
      badge: 'FastMCP',
      description: 'Pure HTTP JSON-RPC Gateway & Registry',
      provider: 'mcp'
    }
  ])

  function updateRegistryUrl(url: string) {
    registryServerUrl.value = url.trim()
  }

  function updateApiBaseUrl(url: string) {
    registryServerUrl.value = url.trim()
  }

  function updateTemperature(val: number) {
    temperature.value = val
  }

  function toggleDarkMode() {
    darkMode.value = !darkMode.value
  }

  function setDarkMode(val: boolean) {
    darkMode.value = Boolean(val)
  }

  return {
    registryServerUrl,
    apiBaseUrl,
    darkMode,
    autostartEnabled,
    selectedModel,
    temperature,
    availableModels,
    updateRegistryUrl,
    updateApiBaseUrl,
    updateTemperature,
    toggleDarkMode,
    setDarkMode,
  }
})
