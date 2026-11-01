import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePluginStore } from '../stores/pluginStore'

describe('pluginStore (MCP Protocol Studio)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('initializes with seed MCP servers and all items are type "mcp"', () => {
    const store = usePluginStore()
    expect(store.plugins.length).toBeGreaterThanOrEqual(7)
    expect(store.plugins.every((p) => p.type === 'mcp')).toBe(true)
    expect(store.installedCount).toBeGreaterThan(0)
  })

  it('switches between marketplace and installed tabs', () => {
    const store = usePluginStore()
    expect(store.activeTab).toBe('marketplace')

    store.setActiveTab('installed')
    expect(store.activeTab).toBe('installed')
    expect(store.filteredPlugins.every((p) => p.installed)).toBe(true)

    store.setActiveTab('marketplace')
    expect(store.activeTab).toBe('marketplace')
  })

  it('filters plugins by category and search query', () => {
    const store = usePluginStore()

    store.setFilterCategory('In-House Tools')
    expect(store.filterCategory).toBe('In-House Tools')
    expect(store.filteredPlugins.every((p) => p.category === 'In-House Tools')).toBe(true)

    store.setFilterCategory('all')
    expect(store.filterCategory).toBe('all')

    store.searchQuery = 'postgres'
    expect(store.filteredPlugins.some((p) => p.id === 'postgres-mcp')).toBe(true)
    expect(store.filteredPlugins.every((p) =>
      p.name.toLowerCase().includes('postgres') ||
      p.summary.toLowerCase().includes('postgres') ||
      p.id.includes('postgres')
    )).toBe(true)

    store.searchQuery = 'non_existent_search_query_xyz'
    expect(store.filteredPlugins.length).toBe(0)
  })

  it('installs, uninstalls and toggles MCP plugin state', () => {
    const store = usePluginStore()
    const target = store.plugins.find((p) => !p.installed)!
    expect(target).toBeDefined()

    const initialInstalledCount = store.installedCount
    store.installPlugin(target.id)

    expect(target.installed).toBe(true)
    expect(target.enabled).toBe(true)
    expect(store.installedCount).toBe(initialInstalledCount + 1)

    // Toggle enabled
    store.togglePlugin(target.id)
    expect(target.enabled).toBe(false)

    store.togglePlugin(target.id)
    expect(target.enabled).toBe(true)

    // Uninstall
    store.uninstallPlugin(target.id)
    expect(target.installed).toBe(false)
    expect(target.enabled).toBe(false)
    expect(store.installedCount).toBe(initialInstalledCount)
  })

  it('selects plugin and computes selectedPlugin details', () => {
    const store = usePluginStore()

    store.selectPlugin('docker-mcp')
    expect(store.selectedPluginId).toBe('docker-mcp')
    expect(store.selectedPlugin?.name).toBe('Docker & Container Runtime')
    expect(store.selectedPlugin?.type).toBe('mcp')
    expect(store.selectedPlugin?.tools?.length).toBeGreaterThan(0)
  })

  it('updates MCP configured environment variables', async () => {
    const store = usePluginStore()
    const target = store.plugins.find((p) => p.id === 'postgres-mcp')!
    expect(target).toBeDefined()

    // Mock fetch for client install endpoint
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'installed' })
    } as any)

    await store.updateMcpConfig('postgres-mcp', {
      DATABASE_URL: 'postgresql://admin:secret@localhost:5432/mydb'
    })

    expect(target.configuredEnv?.DATABASE_URL).toBe('postgresql://admin:secret@localhost:5432/mydb')
  })
})
