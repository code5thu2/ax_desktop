import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import AppHeader from '../AppHeader.vue'
import { useSettingsStore } from '@/features/settings/stores/settingsStore'

describe('AppHeader', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders branding and theme toggle button', () => {
    const wrapper = mount(AppHeader)
    expect(wrapper.text()).toContain('MCP PROTOCOL STUDIO')
    expect(wrapper.text()).toContain('PRIVATE REGISTRY')
    const themeBtn = wrapper.find('[data-testid="theme-toggle-btn"]')
    expect(themeBtn.exists()).toBe(true)
  })

  it('toggles dark mode when theme button is clicked', async () => {
    const settingsStore = useSettingsStore()
    settingsStore.darkMode = true

    const wrapper = mount(AppHeader)
    const themeBtn = wrapper.find('[data-testid="theme-toggle-btn"]')

    await themeBtn.trigger('click')
    expect(settingsStore.darkMode).toBe(false)

    await themeBtn.trigger('click')
    expect(settingsStore.darkMode).toBe(true)
  })

  it('emits openSettings when settings button is clicked', async () => {
    const wrapper = mount(AppHeader)
    const settingsBtn = wrapper.find('[data-testid="header-settings-btn"]')
    await settingsBtn.trigger('click')
    expect(wrapper.emitted('openSettings')).toBeTruthy()
  })
})
