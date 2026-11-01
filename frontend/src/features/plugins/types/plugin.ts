export interface PluginEnvRequirement {
  key: string
  label: string
  required?: boolean
  default?: string
  type?: string
}

export interface PluginTool {
  name: string
  description: string
  parameters?: Record<string, string> | any
}

export interface PluginItem {
  id: string
  name: string
  type: 'mcp'
  vendor: string
  version: string
  icon: string
  rating: number
  downloads: string
  summary: string
  description: string
  features: string[]
  installed: boolean
  enabled: boolean
  installPath?: string
  tools?: PluginTool[]
  changeNotes?: string
  category?: string
  runtime?: string
  downloadUrl?: string
  envRequirements?: PluginEnvRequirement[]
  configuredEnv?: Record<string, string>
}
