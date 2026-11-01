import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSettingsStore } from '../settingsStore'

describe('settingsStore', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('initializes with expected default values', () => {
    const store = useSettingsStore()
    expect(store.apiBaseUrl).toBe('http://127.0.0.1:8000')
    expect(store.darkMode).toBe(true)
    expect(store.autostartEnabled).toBe(false)
  })

  it('allows updating settings', () => {
    const store = useSettingsStore()
    store.updateApiBaseUrl('http://192.168.1.100:8000')
    expect(store.apiBaseUrl).toBe('http://192.168.1.100:8000')

    store.toggleDarkMode()
    expect(store.darkMode).toBe(false)
  })
})
