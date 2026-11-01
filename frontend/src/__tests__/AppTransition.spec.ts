import { describe, it, expect, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import { defineComponent, h, Transition } from 'vue'
import PrimeVue from 'primevue/config'
import App from '../App.vue'
import { useAuthStore } from '@/features/auth/stores/authStore'

describe('App Route Transitions', () => {
  beforeEach(() => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const auth = useAuthStore()
    auth.setGuestMode()
  })

  it('wraps router-view in a page-fade transition with out-in mode', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          name: 'home',
          component: defineComponent({
            name: 'HomeView',
            render() {
              return h('div', { class: 'home-page' }, 'Home Page')
            },
          }),
        },
        {
          path: '/settings',
          name: 'settings',
          component: defineComponent({
            name: 'SettingsView',
            render() {
              return h('div', { class: 'settings-page' }, 'Settings Page')
            },
          }),
        },
      ],
    })

    router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, PrimeVue],
        stubs: {
          Toast: true,
          ConfirmDialog: true,
        },
      },
    })

    await router.isReady()
    await flushPromises()

    // Verify Transition exists with name "page-fade" and mode "out-in"
    const transition = wrapper.findComponent(Transition)
    expect(transition.exists()).toBe(true)
    expect((transition as any).props('name')).toBe('page-fade')
    expect((transition as any).props('mode')).toBe('out-in')

    // Verify routed component renders inside the transition
    expect(wrapper.find('.home-page').exists()).toBe(true)

    // Verify navigating to another route renders properly
    await router.push('/settings')
    expect(wrapper.find('.settings-page').exists()).toBe(true)
  })

  it('defines page-fade transition rules with hardware-accelerated properties in main.css', async () => {
    const fs = await import('fs')
    const path = await import('path')
    const cssPath = path.resolve(__dirname, '../assets/styles/main.css')
    const cssContent = fs.readFileSync(cssPath, 'utf-8')

    expect(cssContent).toContain('.page-fade-enter-active')
    expect(cssContent).toContain('.page-fade-leave-active')
    expect(cssContent).toContain('will-change: opacity, transform;')
    expect(cssContent).toContain('translateY(4px)')
    expect(cssContent).toContain('.page-fade-leave-to')
  })
})
