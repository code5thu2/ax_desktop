import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSkillStore } from '../stores/skillStore'

describe('SkillStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with default marketplace state', () => {
    const store = useSkillStore()
    expect(store.currentMode).toBe('skills')
    expect(store.activeTab).toBe('marketplace')
    expect(store.searchQuery).toBe('')
    expect(store.skills).toEqual([])
    expect(store.installedSkills).toEqual([])
  })

  it('switches mode between skills and mcp', () => {
    const store = useSkillStore()
    store.setMode('mcp')
    expect(store.currentMode).toBe('mcp')
    store.setMode('skills')
    expect(store.currentMode).toBe('skills')
  })

  it('fetches marketplace skills from nativeBridge', async () => {
    const store = useSkillStore()
    await store.fetchMarketplaceSkills()
    expect(store.skills.length).toBeGreaterThan(0)
    expect(store.skills[0].name).toBeDefined()
  })

  it('handles skill installation with scope', async () => {
    const store = useSkillStore()
    const result = await store.installSkill('vietnam-business-law-skills', 1, 'global')
    expect(result.name).toBe('vietnam-business-law-skills')
    expect(result.scope).toBe('global')
    expect(store.installedSkills.some((s) => s.name === 'vietnam-business-law-skills')).toBe(true)
  })

  it('toggles installed skill state', async () => {
    const store = useSkillStore()
    await store.installSkill('vietnam-business-law-skills', 1, 'global')
    const success = await store.toggleSkill('vietnam-business-law-skills', false)
    expect(success).toBe(true)
    const skill = store.installedSkills.find((s) => s.name === 'vietnam-business-law-skills')
    expect(skill?.enabled).toBe(false)
  })

  it('manages current and recent projects', () => {
    const store = useSkillStore()
    store.setCurrentProject('D:/AI_Projects/MyProject')
    expect(store.currentProject).toBe('D:/AI_Projects/MyProject')
    expect(store.recentProjects).toContain('D:/AI_Projects/MyProject')
  })

  it('updates scope and selectedInstalledKey when changing scope from project to global', async () => {
    const store = useSkillStore()
    // Install in project scope
    await store.installSkill('vietnam-business-law-skills', 1, 'project', 'D:/MyProject')
    store.setActiveTab('installed')
    expect(store.selectedSkill?.installScope).toBe('project')

    // Change scope to global
    await store.uninstallSkill('vietnam-business-law-skills', 'D:/MyProject')
    await store.installSkill('vietnam-business-law-skills', 1, 'global')
    expect(store.selectedInstalledKey).toBe('vietnam-business-law-skills-global-global')
    expect(store.selectedSkill?.installScope).toBe('global')
  })
})
