import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useDebounce } from '@vueuse/core'
import type { PluginItem } from '../types/plugin'
import { nativeBridge } from '@/services/nativeBridge'

export const INITIAL_PLUGINS: PluginItem[] = [
  {
    id: 'postgres-mcp',
    name: 'PostgreSQL Database Explorer',
    type: 'mcp',
    vendor: 'Unified Tools Lab',
    version: '2.4.1',
    icon: 'pi pi-database',
    rating: 4.9,
    downloads: '48.2k',
    summary: 'Direct database introspection, SQL query runner, and schema health analyzer.',
    description: 'Enables AI tools to connect to PostgreSQL instances via Model Context Protocol (MCP). Perform live schema inspections, view table definitions, analyze query plans (EXPLAIN ANALYZE), and check missing indexes.',
    features: [
      'Zero-latency SQL query execution with transaction safeguards',
      'Introspective schema exploration and foreign key graphing',
      'Explain query cost analysis with visual bottlenecks breakdown',
      'PostgreSQL health & dead tuples inspector'
    ],
    installed: true,
    enabled: true,
    category: 'In-House Tools',
    tools: [
      { name: 'postgres_execute_query', description: 'Executes a parameterized SELECT or analytical query on target database' },
      { name: 'postgres_describe_table', description: 'Returns columns, data types, constraints, and index details for a table' },
      { name: 'postgres_list_indexes', description: 'Lists all indexes and usage stats across current database schemas' },
      { name: 'postgres_explain_query', description: 'Generates cost and timing breakdown of an execution plan' }
    ],
    changeNotes: 'v2.4.1: Added support for partitioned tables and SSL connection pools.'
  },
  {
    id: 'docker-mcp',
    name: 'Docker & Container Runtime',
    type: 'mcp',
    vendor: 'Cloud Native Ecosystem',
    version: '1.8.0',
    icon: 'pi pi-server',
    rating: 4.8,
    downloads: '92.5k',
    summary: 'Manage local and remote Docker containers, inspect logs, and control Compose services.',
    description: 'Provides official Model Context Protocol integration with Docker Daemon. Inspect container resource consumption, stream live standard output logs, restart crashed containers, and spin up docker-compose clusters.',
    features: [
      'List running, paused, and stopped containers with status badges',
      'Stream container stdout and stderr logs directly into context',
      'Execute diagnostic shell commands in ephemeral containers',
      'Manage multi-container Docker Compose stacks'
    ],
    installed: true,
    enabled: true,
    category: 'In-House Tools',
    tools: [
      { name: 'docker_list_containers', description: 'Lists all containers with ports, image names, and running states' },
      { name: 'docker_inspect_container', description: 'Inspects low-level config, environment variables, and mount bindings' },
      { name: 'docker_container_logs', description: 'Fetches stdout and stderr tail logs for a specific container' },
      { name: 'docker_compose_up', description: 'Starts or rebuilds services defined in docker-compose.yml' }
    ],
    changeNotes: 'v1.8.0: Docker Desktop 4.30+ socket integration and compose v2 support.'
  },
  {
    id: 'puppeteer-mcp',
    name: 'Puppeteer Web Automator',
    type: 'mcp',
    vendor: 'Browser Tools Lab',
    version: '2.0.4',
    icon: 'pi pi-globe',
    rating: 4.9,
    downloads: '64.1k',
    summary: 'Headless Chrome browser automation, full-page screenshots, and dynamic web extraction.',
    description: 'Gives the AI model eyes on the live web. Puppeteer MCP spawns headless Chrome instances to navigate web applications, click buttons, take full-page screenshots, and extract real-time DOM elements.',
    features: [
      'Interactive webpage navigation and single-page app (SPA) rendering',
      'Full-page viewport screenshot captures saved directly to disk',
      'Automated form submission and input field filling',
      'Dynamic HTML content scraping and visual diff checks'
    ],
    installed: true,
    enabled: false,
    category: 'In-House Tools',
    tools: [
      { name: 'browser_navigate', description: 'Navigates headless browser to target URL and waits for network idle' },
      { name: 'take_screenshot', description: 'Captures PNG image of current page viewport or specific selector' },
      { name: 'click_element', description: 'Simulates mouse click on specified DOM element selector' },
      { name: 'evaluate_script', description: 'Executes custom JavaScript expression inside page context' }
    ],
    changeNotes: 'v2.0.4: Upgraded Chromium build and enhanced shadow-DOM traversal.'
  },
  {
    id: 'gitlab-mcp',
    name: 'GitLab DevOps & Pipelines',
    type: 'mcp',
    vendor: 'GitLab Community',
    version: '3.1.2',
    icon: 'pi pi-share-alt',
    rating: 4.7,
    downloads: '35.7k',
    summary: 'Monitor CI/CD pipelines, search repository commits, and review merge requests.',
    description: 'Integrates enterprise GitLab instances with MCP. Query pipeline execution statuses, view failing job trace logs, create issues, and automate merge request descriptions.',
    features: [
      'Pipeline status monitoring with failing job diagnosis',
      'Search code snippets across self-hosted and cloud repositories',
      'Merge Request creation and automated review summaries',
      'Trigger custom CI/CD pipeline schedules'
    ],
    installed: false,
    enabled: false,
    category: 'In-House Tools',
    tools: [
      { name: 'gitlab_list_pipelines', description: 'Queries recent CI/CD pipeline runs for a project' },
      { name: 'gitlab_get_job_trace', description: 'Fetches raw console log of a failed pipeline job' },
      { name: 'gitlab_create_mr', description: 'Creates a new Merge Request between two branches' }
    ],
    changeNotes: 'v3.1.2: Added support for GitLab 17.x GraphQL API.'
  },
  {
    id: 'filesystem-mcp',
    name: 'Local Workspace Filesystem',
    type: 'mcp',
    vendor: 'Antigravity Systems',
    version: '1.2.0',
    icon: 'pi pi-folder',
    rating: 5.0,
    downloads: '110.4k',
    summary: 'Safe, sandboxed workspace filesystem reading, editing, and directory indexing.',
    description: 'Standard MCP filesystem server allowing listing directories, reading file contents, patching source code, and creating workspace assets with strict boundary protection.',
    features: [
      'Sandboxed project directory reading and file search',
      'Precise hunk patching and file replacement',
      'Directory tree listing and glob matching',
      'Permission boundaries preventing access to system sensitive paths'
    ],
    installed: true,
    enabled: true,
    category: 'In-House Tools',
    tools: [
      { name: 'read_file', description: 'Reads contents of target source file within permitted workspace' },
      { name: 'write_file', description: 'Creates or updates a file with provided string content' },
      { name: 'list_directory', description: 'Recursively lists directory structure and file sizes' }
    ],
    changeNotes: 'v1.2.0: Windows path normalization and atomic write locks.'
  },
  {
    id: 'excel-mcp',
    name: 'Excel Spreadsheet Engine',
    type: 'mcp',
    vendor: 'Enterprise Office Tools',
    version: '1.0.0',
    icon: 'pi pi-file-excel',
    rating: 4.8,
    downloads: '22.1k',
    summary: 'Excel workbook creation, reading ranges, formula injection, and cell formatting.',
    description: 'Full spreadsheet manipulation via openpyxl and MCP JSON-RPC protocol.',
    features: [
      'Read and write cell ranges and formula evaluation',
      'Styling, colors, and column width formatting',
      'Multi-sheet workbook operations'
    ],
    installed: false,
    enabled: false,
    category: 'In-House Tools',
    tools: [
      { name: 'create_workbook', description: 'Creates a new Excel spreadsheet' },
      { name: 'read_range', description: 'Reads data from specific sheet cell range' },
      { name: 'write_range', description: 'Writes rows/columns to spreadsheet' }
    ]
  },
  {
    id: 'archive-mcp',
    name: 'Archive & Compression Studio',
    type: 'mcp',
    vendor: 'System Tools Team',
    version: '1.0.0',
    icon: 'pi pi-box',
    rating: 4.9,
    downloads: '18.4k',
    summary: 'Inspect, compress, extract zip and tar archives safely.',
    description: 'High performance zip archive extraction and inspection tool for MCP clients.',
    features: [
      'Zip member listing and checksum validation',
      'Streaming member extraction with directory traversal protection'
    ],
    installed: true,
    enabled: true,
    category: 'In-House Tools',
    tools: [
      { name: 'list_archive', description: 'Lists file members in zip or tar archive' },
      { name: 'extract_archive', description: 'Extracts archive contents into destination directory' }
    ]
  }
]

export const usePluginStore = defineStore('plugins', () => {
  function loadInitialPlugins(): PluginItem[] {
    try {
      if (typeof localStorage !== 'undefined') {
        const raw = localStorage.getItem('mcp_studio_plugins_v1')
        if (raw) return JSON.parse(raw)
      }
    } catch {}
    return JSON.parse(JSON.stringify(INITIAL_PLUGINS))
  }

  const plugins = ref<PluginItem[]>(loadInitialPlugins())

  function persistPlugins() {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('mcp_studio_plugins_v1', JSON.stringify(plugins.value))
      }
    } catch {}
  }

  const activeTab = ref<'marketplace' | 'installed'>('marketplace')
  const filterCategory = ref<string>('all')
  const searchQuery = ref('')
  const isTest = typeof process !== 'undefined' && (process.env?.NODE_ENV === 'test' || Boolean(process.env?.VITEST))
  const debouncedQuery = isTest ? searchQuery : useDebounce(searchQuery, 150)
  const selectedPluginId = ref<string>('postgres-mcp')
  const showGitImportModal = ref(false)
  const showUploadModal = ref(false)

  // Installed plugins
  const installedPlugins = computed(() => {
    return plugins.value.filter((p) => p.installed)
  })

  // Marketplace plugins (all plugins)
  const marketplacePlugins = computed(() => {
    return plugins.value
  })

  // Badge count for Installed tab
  const installedCount = computed(() => {
    return installedPlugins.value.length
  })

  // Filtered list depending on activeTab, filterCategory, and debouncedQuery
  const filteredPlugins = computed(() => {
    const list = activeTab.value === 'installed' ? installedPlugins.value : marketplacePlugins.value
    const q = debouncedQuery.value.trim().toLowerCase()

    return list.filter((p) => {
      // Category match
      if (filterCategory.value !== 'all' && p.category !== filterCategory.value) {
        return false
      }
      // Search match
      if (!q) return true
      const inName = p.name.toLowerCase().includes(q)
      const inSummary = p.summary.toLowerCase().includes(q)
      const inVendor = p.vendor.toLowerCase().includes(q)
      const inTools = p.tools?.some((t) => t.name.toLowerCase().includes(q) || t.description.toLowerCase().includes(q))
      return inName || inSummary || inVendor || inTools
    })
  })

  // Selected plugin object (falls back to active item in filtered list)
  const selectedPlugin = computed<PluginItem | null>(() => {
    const list = filteredPlugins.value
    if (list.length === 0) return null
    return list.find((p) => p.id === selectedPluginId.value) || list[0]
  })

  // MCP Registry & Gateway Server URL
  const registryServerUrl = ref('http://127.0.0.1:8000')
  const isLoadingCatalog = ref(false)
  const isServerOnline = ref(true)

  async function fetchCatalogFromServer() {
    isLoadingCatalog.value = true
    try {
      const data = await nativeBridge.getCatalog(registryServerUrl.value)
      const remoteServers = data.servers || []
      isServerOnline.value = true

      // Merge remote servers with local state
      remoteServers.forEach((remote: any) => {
        const existing = plugins.value.find((p) => p.id === remote.id)
        if (existing) {
          existing.name = remote.name || existing.name
          existing.summary = remote.summary || existing.summary
          existing.description = remote.description || existing.description
          existing.version = remote.version || existing.version
          existing.category = remote.category || existing.category || 'In-House Tools'
          existing.tools = (remote.tools || []).map((t: any) => ({
            name: t.name,
            description: t.description || `Tool ${t.name}`,
            parameters: t.parameters || t.inputSchema || {}
          }))
          existing.envRequirements = remote.envRequirements || existing.envRequirements || []
        } else {
          plugins.value.unshift({
            id: remote.id,
            name: remote.name || remote.id,
            type: 'mcp',
            vendor: remote.vendor || 'In-House Registry',
            version: remote.version || '1.0.0',
            icon: remote.icon || 'pi pi-server',
            rating: 5.0,
            downloads: '1.2k',
            summary: remote.summary || `MCP Server ${remote.name}`,
            description: remote.description || remote.summary || 'Enterprise MCP protocol server.',
            features: [
              'Stateless pure HTTP request-response protocol',
              'JSON-RPC 2.0 tool execution via Gateway'
            ],
            installed: false,
            enabled: false,
            category: remote.category || 'In-House Tools',
            runtime: remote.runtime || 'python',
            downloadUrl: remote.download_url,
            tools: (remote.tools || []).map((t: any) => ({
              name: t.name,
              description: t.description || `Tool ${t.name}`,
              parameters: t.parameters || t.inputSchema || {}
            })),
            envRequirements: remote.envRequirements || []
          })
        }
      })

      isServerOnline.value = true
      await syncInstalledClients()
      persistPlugins()
    } catch {
      isServerOnline.value = false
    } finally {
      isLoadingCatalog.value = false
    }
  }

  async function installMcpOnClient(id: string) {
    const target = plugins.value.find((p) => p.id === id)
    if (!target) return
    try {
      const res = await fetch(`${registryServerUrl.value}/api/v1/client/install/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ env: target.configuredEnv || {} })
      })
      if (res.ok) {
        const data = await res.json()
        target.installed = true
        target.enabled = true
        target.installPath = data.install_path
        persistPlugins()
        return data
      }
    } catch {
      // Local fallback
    }
  }

  async function updateMcpConfig(id: string, newEnv: Record<string, string>) {
    const target = plugins.value.find((p) => p.id === id)
    if (!target) return
    target.configuredEnv = { ...newEnv }
    persistPlugins()
    if (isServerOnline.value) {
      try {
        const res = await fetch(`${registryServerUrl.value}/api/v1/client/config/${id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ env: newEnv })
        })
        if (res.ok) {
          return await res.json()
        }
      } catch {
        // Fallback to local store
      }
    }
  }

  function installPlugin(id: string) {
    const target = plugins.value.find((p) => p.id === id)
    if (target) {
      target.installed = true
      target.enabled = true
      if (isServerOnline.value) {
        installMcpOnClient(id)
      }
      selectedPluginId.value = id
      persistPlugins()
    }
  }

  function uninstallPlugin(id: string) {
    const target = plugins.value.find((p) => p.id === id)
    if (target) {
      if (isServerOnline.value) {
        fetch(`${registryServerUrl.value}/api/v1/client/uninstall/${id}`, { method: 'POST' }).catch(() => {})
      }
      target.installed = false
      target.enabled = false
      target.installPath = undefined
      persistPlugins()
    }
  }

  function togglePlugin(id: string, state?: boolean) {
    const target = plugins.value.find((p) => p.id === id)
    if (target) {
      target.enabled = state !== undefined ? state : !target.enabled
      persistPlugins()
    }
  }

  function selectPlugin(id: string) {
    selectedPluginId.value = id
  }

  function setActiveTab(tab: 'marketplace' | 'installed') {
    activeTab.value = tab
    const currentList = tab === 'installed' ? installedPlugins.value : marketplacePlugins.value
    if (currentList.length > 0 && !currentList.some((p) => p.id === selectedPluginId.value)) {
      selectedPluginId.value = currentList[0].id
    }
  }

  function setFilterCategory(cat: string) {
    filterCategory.value = cat
  }

  async function syncInstalledClients() {
    if (!isServerOnline.value) return
    try {
      const res = await fetch(`${registryServerUrl.value}/api/v1/client/installed`)
      if (res.ok) {
        const data = await res.json()
        const installedList = data.installed || []
        installedList.forEach((inst: any) => {
          const p = plugins.value.find((x) => x.id === inst.server_id)
          if (p) {
            p.installed = true
            p.installPath = inst.install_path
            if (inst.configured_env && Object.keys(inst.configured_env).length > 0) {
              p.configuredEnv = { ...(p.configuredEnv || {}), ...inst.configured_env }
            }
          }
        })
      }
    } catch {
      // Ignore sync error
    }
  }

  async function importFromGit(
    repoUrl: string,
    branch: string = 'main',
    token?: string,
    name?: string,
    description?: string,
    envRequirements?: Array<{ key: string; label?: string; default?: string; required?: boolean; type?: string }>
  ) {
    const res = await fetch(`${registryServerUrl.value}/api/v1/mcp/import-git`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        repo_url: repoUrl,
        branch,
        token: token || undefined,
        name: name || undefined,
        description: description || undefined,
        env_requirements: envRequirements && envRequirements.length > 0 ? envRequirements : undefined
      })
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: 'Import failed' }))
      throw new Error(errData.detail || `Failed to import from Git (HTTP ${res.status})`)
    }

    const result = await res.json()
    await fetchCatalogFromServer()
    if (result.id) {
      selectPlugin(result.id)
    }
    return result
  }

  async function uploadCustomMCP(
    file: File,
    name?: string,
    description?: string,
    envRequirements?: Array<{ key: string; label?: string; default?: string; required?: boolean; type?: string }>
  ) {
    const formData = new FormData()
    formData.append('file', file)
    if (name) formData.append('name', name)
    if (description) formData.append('description', description)
    if (envRequirements && envRequirements.length > 0) {
      formData.append('env_requirements', JSON.stringify(envRequirements))
    }

    const res = await fetch(`${registryServerUrl.value}/api/v1/mcp/upload`, {
      method: 'POST',
      body: formData
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: 'Upload failed' }))
      throw new Error(errData.detail || `Upload failed (HTTP ${res.status})`)
    }

    const result = await res.json()
    await fetchCatalogFromServer()
    if (result.id) {
      selectPlugin(result.id)
    }
    return result
  }

  async function executeToolDirectly(toolName: string, args: Record<string, any> = {}) {
    const res = await fetch(`${registryServerUrl.value}/mcp/tools/${toolName}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(args)
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: 'Execution error' }))
      throw new Error(errData.detail || `Tool execution failed (HTTP ${res.status})`)
    }

    return await res.json()
  }

  return {
    plugins,
    activeTab,
    filterCategory,
    searchQuery,
    selectedPluginId,
    selectedPlugin,
    installedPlugins,
    marketplacePlugins,
    installedCount,
    filteredPlugins,
    installPlugin,
    uninstallPlugin,
    togglePlugin,
    selectPlugin,
    setActiveTab,
    setFilterCategory,
    registryServerUrl,
    isLoadingCatalog,
    isServerOnline,
    fetchCatalogFromServer,
    importFromGit,
    uploadCustomMCP,
    executeToolDirectly,
    installMcpOnClient,
    syncInstalledClients,
    updateMcpConfig,
    persistPlugins,
    showGitImportModal,
    showUploadModal,
  }
})
