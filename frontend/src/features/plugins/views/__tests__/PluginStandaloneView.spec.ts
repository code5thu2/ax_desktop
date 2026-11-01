import { describe, it, expect, beforeEach, vi, beforeAll } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'
import PluginStandaloneView from '../PluginStandaloneView.vue'

beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver
})

const mockPush = vi.fn()
let currentPath = '/'

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useRoute: () => ({
    path: currentPath,
  }),
}))

describe('PluginStandaloneView.vue', () => {
  beforeEach(() => {
    mockPush.mockClear()
    currentPath = '/'
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders dedicated MCP AppHeader and IntelliJPluginsView', () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    const wrapper = mount(PluginStandaloneView, {
      global: {
        plugins: [PrimeVue, ConfirmationService, ToastService, pinia],
      },
    })

    // Header branding
    expect(wrapper.text()).toContain('MCP PROTOCOL STUDIO')
    expect(wrapper.text()).toContain('PRIVATE REGISTRY')

    // Plugin list content should be rendered
    expect(wrapper.text()).toContain('Marketplace')
    expect(wrapper.text()).toContain('Installed')
    expect(wrapper.text()).toContain('PostgreSQL Database Explorer')

    // Search input and category filter buttons should be present
    expect(wrapper.find('[data-testid="plugin-search-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="filter-all"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="filter-inhouse"]').exists()).toBe(true)
  })

  it('allows opening settings from header', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    const wrapper = mount(PluginStandaloneView, {
      global: {
        plugins: [PrimeVue, ConfirmationService, ToastService, pinia],
      },
    })

    const settingsBtn = wrapper.find('[data-testid="header-settings-btn"]')
    expect(settingsBtn.exists()).toBe(true)
    await settingsBtn.trigger('click')

    const settingsDialog = wrapper.findComponent({ name: 'SettingsDialog' })
    expect(settingsDialog.exists()).toBe(true)
    expect(settingsDialog.props('visible')).toBe(true)
  })
})
