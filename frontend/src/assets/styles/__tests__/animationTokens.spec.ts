import { describe, it, expect } from 'vitest'
import { createApp } from 'vue'
import { autoAnimatePlugin } from '@formkit/auto-animate/vue'
// @ts-ignore - JavaScript config file without declaration
import tailwindConfig from '../../../../tailwind.config.js'
import fs from 'fs'
import path from 'path'

describe('Animation System Foundation', () => {
  it('registers autoAnimatePlugin cleanly without throwing', () => {
    const app = createApp({ template: '<div></div>' })
    expect(() => app.use(autoAnimatePlugin)).not.toThrow()
  })

  it('defines custom spring-smooth timing function in tailwind config', () => {
    const theme = tailwindConfig.theme?.extend as any
    expect(theme?.transitionTimingFunction?.['spring-smooth']).toBe('cubic-bezier(0.16, 1, 0.3, 1)')
  })

  it('defines custom keyframes in tailwind config', () => {
    const keyframes = (tailwindConfig.theme?.extend as any)?.keyframes
    expect(keyframes).toBeDefined()
    expect(keyframes).toHaveProperty('fade-in')
    expect(keyframes).toHaveProperty('slide-up')
    expect(keyframes).toHaveProperty('pop-in')
    expect(keyframes).toHaveProperty('message-enter')
  })

  it('defines animation utility classes in tailwind config', () => {
    const animation = (tailwindConfig.theme?.extend as any)?.animation
    expect(animation).toBeDefined()
    expect(animation).toHaveProperty('fade-in')
    expect(animation).toHaveProperty('slide-up')
    expect(animation).toHaveProperty('pop-in')
    expect(animation).toHaveProperty('pop')
    expect(animation).toHaveProperty('message-enter')
  })

  it('includes transitions and prefers-reduced-motion in main.css', () => {
    const cssPath = path.resolve(__dirname, '../main.css')
    const cssContent = fs.readFileSync(cssPath, 'utf-8')

    expect(cssContent).toContain('@media (prefers-reduced-motion: reduce)')
    expect(cssContent).toContain('.page-fade-enter-active')
    expect(cssContent).toContain('.page-fade-leave-active')
    expect(cssContent).toContain('.dropdown-pop-enter-active')
    expect(cssContent).toContain('.dropdown-pop-leave-active')
    expect(cssContent).toContain('.animate-fade-in')
    expect(cssContent).toContain('.animate-slide-up')
    expect(cssContent).toContain('.animate-pop')
    expect(cssContent).toContain('.animate-message-enter')
  })
})
