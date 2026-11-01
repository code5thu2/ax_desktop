import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AppSkillMcpLogo, { type LogoVariant } from '../AppSkillMcpLogo.vue'

describe('AppSkillMcpLogo', () => {
  it('renders network variant by default', () => {
    const wrapper = mount(AppSkillMcpLogo)
    expect(wrapper.find('.logo-variant-network').exists()).toBe(true)
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  const allVariants: LogoVariant[] = [
    'network',
    'socket',
    'modular',
    'hexacore',
    'isocube',
    'synapse',
    'concentric',
  ]

  allVariants.forEach((variant) => {
    it(`renders ${variant} variant correctly`, () => {
      const wrapper = mount(AppSkillMcpLogo, {
        props: { variant },
      })
      expect(wrapper.find(`.logo-variant-${variant}`).exists()).toBe(true)
    })
  })

  it('applies custom size class and styles correctly', () => {
    const wrapper = mount(AppSkillMcpLogo, {
      props: { size: 'hero' },
    })
    expect(wrapper.find('svg').classes()).toContain('w-24')
    expect(wrapper.find('svg').classes()).toContain('h-24')
  })
})
