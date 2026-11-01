import { describe, it, expect, beforeEach, beforeAll } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import SettingsDialog from '../SettingsDialog.vue'

beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver

  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
  })
})

describe('SettingsDialog.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders correctly when visible with appendTo self', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    const wrapper = mount(SettingsDialog, {
      props: {
        visible: true,
        appendTo: 'self',
      },
      global: {
        plugins: [PrimeVue, pinia],
      },
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Cài đặt (Settings)')
    expect(wrapper.text()).toContain('Chung (General)')
    expect(wrapper.text()).toContain('AI Clients & IDEs')
  })

  it('allows toggling between light and dark theme mode', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    const wrapper = mount(SettingsDialog, {
      props: {
        visible: true,
        appendTo: 'self',
      },
      global: {
        plugins: [PrimeVue, pinia],
      },
    })

    const lightBtn = wrapper.find('[data-testid="theme-light-select-btn"]')
    const darkBtn = wrapper.find('[data-testid="theme-dark-select-btn"]')

    expect(lightBtn.exists()).toBe(true)
    expect(darkBtn.exists()).toBe(true)

    await lightBtn.trigger('click')
    await darkBtn.trigger('click')
  })

  it('switches tabs when clicking on nav items', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    const wrapper = mount(SettingsDialog, {
      props: {
        visible: true,
        appendTo: 'self',
      },
      global: {
        plugins: [PrimeVue, pinia],
      },
    })

    const buttons = wrapper.findAll('nav button')
    expect(buttons.length).toBe(3)

    // Click AI Clients tab
    await buttons[1].trigger('click')
    expect(wrapper.text()).toContain('Claude Desktop Configuration')
    expect(wrapper.text()).toContain('Cursor & Windsurf IDE')

    // Click About tab
    await buttons[2].trigger('click')
    expect(wrapper.text()).toContain('MCP PROTOCOL STUDIO')
  })

  it('saves settings and emits update:visible false when Save is clicked', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    const wrapper = mount(SettingsDialog, {
      props: {
        visible: true,
        appendTo: 'self',
      },
      global: {
        plugins: [PrimeVue, pinia],
      },
    })

    const saveBtn = wrapper.findAll('button').find((b) => b.text().includes('Lưu cài đặt'))
    expect(saveBtn?.exists()).toBe(true)
    await saveBtn?.trigger('click')

    expect(wrapper.emitted('update:visible')).toBeTruthy()
    expect(wrapper.emitted('update:visible')![0]).toEqual([false])
  })
})
