<script setup lang="ts">
import { computed, type Component } from 'vue'
import {
  Puzzle,
  Play,
  GitBranch,
  Folder,
  Settings,
  Terminal,
  Code2,
  Search,
  Download,
  Trash2,
  Copy,
  X,
  Plus,
  Check,
  User,
  RefreshCw,
  Layers,
  Boxes,
  Package,
  ExternalLink,
  ChevronRight,
  ChevronLeft,
  ChevronDown,
  ChevronUp,
  Upload,
  Info,
  AlertTriangle,
  Database,
  Cpu,
  Sparkles,
  HelpCircle,
  Filter,
  Sliders,
  FolderGit2,
  Eye,
  EyeOff,
} from 'lucide-vue-next'

const iconMap: Record<string, Component> = {
  puzzle: Puzzle,
  plugin: Puzzle,
  run: Play,
  play: Play,
  git: GitBranch,
  branch: GitBranch,
  branches: GitBranch,
  folder: Folder,
  project: FolderGit2,
  settings: Settings,
  terminal: Terminal,
  code: Code2,
  search: Search,
  find: Search,
  download: Download,
  install: Download,
  trash: Trash2,
  delete: Trash2,
  copy: Copy,
  close: X,
  x: X,
  add: Plus,
  plus: Plus,
  check: Check,
  checkmark: Check,
  user: User,
  refresh: RefreshCw,
  sync: RefreshCw,
  services: Layers,
  layers: Layers,
  dependencies: Boxes,
  boxes: Boxes,
  package: Package,
  'external-link': ExternalLink,
  'chevron-right': ChevronRight,
  'chevron-left': ChevronLeft,
  'chevron-down': ChevronDown,
  'chevron-up': ChevronUp,
  upload: Upload,
  info: Info,
  alert: AlertTriangle,
  warning: AlertTriangle,
  database: Database,
  cpu: Cpu,
  sparkles: Sparkles,
  ai: Sparkles,
  help: HelpCircle,
  filter: Filter,
  sliders: Sliders,
  eye: Eye,
  'eye-off': EyeOff,
}

const props = withDefaults(
  defineProps<{
    name: string
    size?: 'xs' | 'sm' | 'md' | 'lg' | number
    class?: string
    strokeWidth?: number
  }>(),
  {
    size: 'md',
    strokeWidth: 2,
  }
)

const sizeInPx = computed(() => {
  if (typeof props.size === 'number') return props.size
  switch (props.size) {
    case 'xs':
      return 12
    case 'sm':
      return 14
    case 'lg':
      return 20
    case 'md':
    default:
      return 16
  }
})

const iconComponent = computed(() => iconMap[props.name] || HelpCircle)
</script>

<template>
  <component
    :is="iconComponent"
    :size="sizeInPx"
    :stroke-width="props.strokeWidth"
    class="inline-block flex-shrink-0 transition-colors"
    :class="props.class"
  />
</template>
