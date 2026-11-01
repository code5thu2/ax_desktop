import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import SplashScreen from '../SplashScreen.vue'

describe('SplashScreen', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders branding title and initial loading status', () => {
    const wrapper = mount(SplashScreen, {
      props: {
        duration: 3000,
      },
    })

    expect(wrapper.text()).toContain('MCP PROTOCOL STUDIO')
    expect(wrapper.text()).toContain('ENTERPRISE')
    expect(wrapper.find('[data-testid="splash-screen"]').exists()).toBe(true)
  })

  it('increments progress and emits complete after duration', async () => {
    const wrapper = mount(SplashScreen, {
      props: {
        duration: 3000,
      },
    })

    // Advance halfway
    vi.advanceTimersByTime(1500)
    await wrapper.vm.$nextTick()

    // Advance to end
    vi.advanceTimersByTime(2000)
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('complete')).toBeTruthy()
  })
})
