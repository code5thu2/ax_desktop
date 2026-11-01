import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PageMascot from '../PageMascot.vue'

describe('PageMascot.vue (Koboyo Page Mascot Component)', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    if (typeof (globalThis as any).PointerEvent === 'undefined') {
      ;(globalThis as any).PointerEvent = class extends MouseEvent {
        constructor(type: string, params: MouseEventInit = {}) {
          super(type, params)
        }
      }
    }
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('renders correctly with default props', () => {
    const wrapper = mount(PageMascot)
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.attributes('aria-label')).toBe('Page Mascot')
    expect(wrapper.attributes('role')).toBe('button')

    // Default size is 80px
    const style = wrapper.attributes('style')
    expect(style).toContain('width: 80px')
    expect(style).toContain('height: 80px')
  })

  it('supports custom size and pixelated rendering', () => {
    const wrapper = mount(PageMascot, {
      props: {
        size: 120,
        pixelated: true,
        label: 'Cyber Cat',
      },
    })

    expect(wrapper.attributes('aria-label')).toBe('Cyber Cat')
    expect(wrapper.attributes('style')).toContain('width: 120px')
    expect(wrapper.classes()).toContain('rendering-pixelated')
  })

  it('triggers poke reaction on click with event emit and squash', async () => {
    const wrapper = mount(PageMascot, {
      props: {
        reactDuration: 300,
      },
    })

    // Click mascot
    await wrapper.trigger('click')

    // Emits 'poke' with reaction index
    expect(wrapper.emitted('poke')).toBeTruthy()
    expect(wrapper.emitted('poke')![0][0]).toBeGreaterThanOrEqual(0)

    // Mascot is in squash state initially
    expect(wrapper.classes()).toContain('scale-y-[0.88]')

    // Advance 150ms -> squash ends
    vi.advanceTimersByTime(150)
    await wrapper.vm.$nextTick()
    expect(wrapper.classes()).not.toContain('scale-y-[0.88]')

    // Advance beyond reactDuration (300ms) -> returns to tracking
    vi.advanceTimersByTime(200)
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).isReacting).toBe(false)
  })

  it('allows programmatic poke via exposed method', async () => {
    const wrapper = mount(PageMascot)

    ;(wrapper.vm as any).poke(5)
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('poke')![0][0]).toBe(5)
    expect((wrapper.vm as any).isReacting).toBe(true)
  })

  it('tracks pointer coordinates with dead zone honoring', async () => {
    const wrapper = mount(PageMascot, {
      props: {
        deadZone: 40,
      },
    })

    // Mock getBoundingClientRect
    const container = wrapper.element as HTMLElement
    vi.spyOn(container, 'getBoundingClientRect').mockReturnValue({
      left: 100,
      top: 100,
      width: 80,
      height: 80,
      right: 180,
      bottom: 180,
      x: 100,
      y: 100,
      toJSON: () => {},
    })

    // Pointer inside dead zone (center is 140, 140)
    window.dispatchEvent(new (globalThis as any).PointerEvent('pointermove', { clientX: 145, clientY: 145 }))
    // Execute requestAnimationFrame
    await vi.runAllTimersAsync()

    expect((wrapper.vm as any).currentCol).toBe(1)
    expect((wrapper.vm as any).currentRow).toBe(1)

    // Pointer far to the right (clientX: 300, clientY: 140 -> dx = +160, dy = 0)
    window.dispatchEvent(new (globalThis as any).PointerEvent('pointermove', { clientX: 300, clientY: 140 }))
    await vi.runAllTimersAsync()

    expect((wrapper.vm as any).currentCol).toBe(2)
    expect((wrapper.vm as any).currentRow).toBe(1)
  })
})
