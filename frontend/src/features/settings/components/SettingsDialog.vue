<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { useSettingsStore } from '@/features/settings/stores/settingsStore'
import { usePluginStore } from '@/features/plugins/stores/pluginStore'

interface Props {
  visible: boolean
  appendTo?: string | HTMLElement
}

const props = withDefaults(defineProps<Props>(), {
  appendTo: 'body',
})
const emit = defineEmits<{
  'update:visible': [val: boolean]
  'openPlugins': []
}>()

const settingsStore = useSettingsStore()
const pluginStore = usePluginStore()

const activeTab = ref<'general' | 'clients' | 'about'>('general')

const tabs = [
  { id: 'general' as const, label: 'Chung (General)', icon: 'pi pi-cog' },
  { id: 'clients' as const, label: 'AI Clients & IDEs', icon: 'pi pi-desktop' },
  { id: 'about' as const, label: 'Thông tin', icon: 'pi pi-info-circle' },
]

function handleTabClick(tabId: typeof tabs[number]['id']) {
  activeTab.value = tabId
}

// Temporary form states
const tempUrl = ref(settingsStore.apiBaseUrl)
const tempDarkMode = ref(settingsStore.darkMode)
const isAutostartEnabled = ref(false)
const pingStatus = ref<'idle' | 'checking' | 'online' | 'offline'>('idle')
const jsonCopied = ref(false)

async function checkAutostartStatus() {
  try {
    if (typeof window !== 'undefined' && (window as any).pywebview?.api?.is_autostart_enabled) {
      isAutostartEnabled.value = await (window as any).pywebview.api.is_autostart_enabled()
    } else {
      const saved = localStorage.getItem('mcp_studio_autostart')
      isAutostartEnabled.value = saved === 'true'
    }
  } catch (e) {
    console.error('Failed to check autostart:', e)
  }
}

async function toggleAutostart() {
  const next = !isAutostartEnabled.value
  isAutostartEnabled.value = next
  try {
    if (typeof window !== 'undefined' && (window as any).pywebview?.api?.set_autostart) {
      await (window as any).pywebview.api.set_autostart(next)
    }
    localStorage.setItem('mcp_studio_autostart', String(next))
  } catch (e) {
    console.error('Failed to set autostart:', e)
  }
}

async function testGatewayPing() {
  pingStatus.value = 'checking'
  try {
    const res = await fetch(`${tempUrl.value}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/list', params: {} })
    })
    if (res.ok) {
      pingStatus.value = 'online'
    } else {
      pingStatus.value = 'offline'
    }
  } catch {
    pingStatus.value = 'offline'
  }
  setTimeout(() => {
    pingStatus.value = 'idle'
  }, 3500)
}

function copyClaudeConfig() {
  const cfg = {
    mcpServers: {
      "mcp-protocol-studio": {
        url: `${settingsStore.apiBaseUrl}/mcp`
      }
    }
  }
  if (navigator.clipboard) {
    navigator.clipboard.writeText(JSON.stringify(cfg, null, 2))
    jsonCopied.value = true
    setTimeout(() => {
      jsonCopied.value = false
    }, 2000)
  }
}

watch(
  () => props.visible,
  (isOpened) => {
    if (isOpened) {
      tempUrl.value = settingsStore.apiBaseUrl
      tempDarkMode.value = settingsStore.darkMode
      checkAutostartStatus()
    }
  }
)

onMounted(() => {
  checkAutostartStatus()
})

function saveSettings() {
  settingsStore.updateApiBaseUrl(tempUrl.value)
  pluginStore.registryServerUrl = tempUrl.value
  settingsStore.darkMode = tempDarkMode.value
  emit('update:visible', false)
}

function resetDefaults() {
  tempUrl.value = 'http://127.0.0.1:8000'
  tempDarkMode.value = true
}
</script>

<template>
  <Dialog
    :visible="props.visible"
    :appendTo="props.appendTo"
    modal
    header="Cài đặt (Settings)"
    :style="{ width: '680px', maxWidth: '95vw' }"
    :breakpoints="{ '1024px': '95vw', '768px': '98vw' }"
    class="!bg-white dark:!bg-[#171717] !border !border-[#e5e5e5] dark:!border-[#2e2e2e] !text-[#0d0d0d] dark:!text-[#ececec] !rounded-2xl shadow-2xl overflow-hidden transition-all duration-200"
    :pt="{
      root: { class: '!bg-white dark:!bg-[#171717] !border !border-[#e5e5e5] dark:!border-[#2e2e2e] !rounded-2xl shadow-2xl overflow-hidden' },
      header: { class: '!bg-transparent !border-b !border-[#e5e5e5] dark:!border-[#2e2e2e] !py-3.5 !px-5 !text-slate-900 dark:!text-[#ececec]' },
      content: { class: '!bg-transparent !p-0 overflow-hidden' },
      footer: { class: '!bg-transparent !border-t !border-[#e5e5e5] dark:!border-[#2e2e2e] !px-5 !py-3' },
      pcCloseButton: {
        root: {
          tabindex: -1,
          class: '!w-8 !h-8 !p-1.5 !outline-none !ring-0 !shadow-none !border-none focus:!outline-none active:!outline-none hover:!bg-[#f0f0f0] dark:hover:!bg-[#262626] text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 !rounded-lg flex items-center justify-center transition cursor-pointer'
        }
      }
    }"
    @update:visible="emit('update:visible', $event)"
  >
    <!-- 2-Column Dialog Layout -->
    <div class="flex flex-col md:flex-row transition-all duration-200 h-[460px]">
      <!-- Left Navigation Column -->
      <nav class="w-full md:w-52 shrink-0 border-b md:border-b-0 md:border-r border-[#e5e5e5] dark:border-[#2e2e2e] p-2.5 space-y-1 bg-[#f9f9f9] dark:bg-[#171717]">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :data-testid="`settings-tab-${tab.id}`"
          type="button"
          class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition cursor-pointer text-left"
          :class="[
            activeTab === tab.id
              ? 'bg-[#e5e5e5] dark:bg-[#262626] text-slate-900 dark:text-white font-semibold'
              : 'text-neutral-500 dark:text-neutral-400 hover:text-slate-900 dark:hover:text-white hover:bg-[#ececec] dark:hover:bg-[#212121]'
          ]"
          @click="handleTabClick(tab.id)"
        >
          <i :class="tab.icon" class="text-xs"></i>
          <span>{{ tab.label }}</span>
        </button>
      </nav>

      <!-- Right Content Panel -->
      <div class="flex-1 min-w-0 bg-white dark:bg-[#171717] p-5 overflow-y-auto space-y-4 text-xs">
        <!-- TAB 1: GENERAL -->
        <div v-if="activeTab === 'general'" class="space-y-4">
          <!-- Theme Selection -->
          <div class="pb-4 border-b border-[#e5e5e5] dark:border-[#2e2e2e]">
            <label class="block text-xs font-semibold text-slate-800 dark:text-[#ececec] mb-1.5">
              Giao diện hiển thị (Theme Mode)
            </label>
            <p class="text-[11px] text-neutral-500 dark:text-neutral-400 mb-2.5">
              Chọn phong cách giao diện sáng hoặc tối cho MCP Protocol Studio.
            </p>
            <div class="grid grid-cols-2 gap-2 p-1 rounded-xl bg-[#f0f0f0] dark:bg-[#212121] border border-[#e5e5e5] dark:border-[#2e2e2e]">
              <button
                type="button"
                data-testid="theme-light-select-btn"
                class="flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-medium transition cursor-pointer"
                :class="[
                  !tempDarkMode
                    ? 'bg-white dark:bg-[#2f2f2f] text-slate-900 dark:text-white shadow-sm border border-[#e5e5e5] dark:border-[#383838]'
                    : 'text-neutral-500 dark:text-neutral-400 hover:text-slate-900 dark:hover:text-white'
                ]"
                @click="tempDarkMode = false"
              >
                <i class="pi pi-sun text-amber-500 text-xs"></i>
                <span>Giao diện Sáng (Light)</span>
              </button>

              <button
                type="button"
                data-testid="theme-dark-select-btn"
                class="flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-medium transition cursor-pointer"
                :class="[
                  tempDarkMode
                    ? 'bg-white dark:bg-[#2f2f2f] text-slate-900 dark:text-white shadow-sm border border-[#e5e5e5] dark:border-[#383838]'
                    : 'text-neutral-500 dark:text-neutral-400 hover:text-slate-900 dark:hover:text-white'
                ]"
                @click="tempDarkMode = true"
              >
                <i class="pi pi-moon text-teal-400 text-xs"></i>
                <span>Giao diện Tối (Dark)</span>
              </button>
            </div>
          </div>

          <!-- Windows Autostart & Run Hidden in Tray -->
          <div class="p-3.5 rounded-xl bg-[#f9f9f9] dark:bg-[#212121] border border-[#e5e5e5] dark:border-[#2e2e2e] flex items-center justify-between gap-3">
            <div class="flex items-center gap-2.5">
              <div class="w-7 h-7 rounded-lg bg-indigo-500/10 text-indigo-500 flex items-center justify-center text-xs shrink-0">
                <i class="pi pi-microsoft"></i>
              </div>
              <div class="flex flex-col min-w-0">
                <span class="text-xs font-semibold text-slate-800 dark:text-[#ececec]">
                  Khởi động cùng Windows (Chạy ẩn Tray)
                </span>
                <span class="text-[11px] text-neutral-500 dark:text-neutral-400 mt-0.5">
                  Tự động khởi động khi bật máy và thu nhỏ chạy ngầm dưới khay hệ thống (System Tray).
                </span>
              </div>
            </div>
            <button
              type="button"
              data-testid="toggle-autostart-btn"
              class="px-3 py-1 rounded-full text-xs font-medium transition cursor-pointer flex-shrink-0"
              :class="isAutostartEnabled ? 'bg-[#10A37F] text-white' : 'bg-[#e5e5e5] dark:bg-[#2f2f2f] text-neutral-600 dark:text-neutral-400'"
              @click="toggleAutostart"
            >
              {{ isAutostartEnabled ? 'Đang bật' : 'Đã tắt' }}
            </button>
          </div>

          <!-- Registry Server URL Config -->
          <div class="p-3.5 rounded-xl bg-[#f9f9f9] dark:bg-[#212121] border border-[#e5e5e5] dark:border-[#2e2e2e] space-y-2.5">
            <div class="flex items-center justify-between">
              <label class="block font-semibold text-slate-800 dark:text-[#ececec]">
                Địa chỉ MCP Gateway & Registry Server
              </label>
              <button
                type="button"
                class="text-[11px] px-2 py-0.5 rounded text-[#10A37F] hover:bg-emerald-500/10 transition cursor-pointer flex items-center gap-1 font-medium"
                @click="testGatewayPing"
              >
                <i class="pi pi-bolt text-[10px]" :class="{ 'animate-spin': pingStatus === 'checking' }"></i>
                <span>{{ pingStatus === 'checking' ? 'Đang kiểm tra...' : (pingStatus === 'online' ? '● Online (Hoạt động)' : (pingStatus === 'offline' ? '✕ Mất kết nối' : 'Kiểm tra Ping')) }}</span>
              </button>
            </div>
            <InputText
              v-model="tempUrl"
              placeholder="http://127.0.0.1:8000"
              class="w-full !text-xs !py-2 !px-3 font-mono !rounded-lg"
            />
            <p class="text-[11px] text-neutral-500 dark:text-neutral-400 leading-relaxed">
              Cổng HTTP nơi FastMCP Gateway và In-House Registry đang lắng nghe các lệnh JSON-RPC.
            </p>
          </div>
        </div>

        <!-- TAB 2: AI CLIENTS & IDES -->
        <div v-if="activeTab === 'clients'" class="space-y-4">
          <div class="pb-3 border-b border-[#e5e5e5] dark:border-[#2e2e2e]">
            <h3 class="text-xs font-bold text-slate-900 dark:text-white">
              Kết nối MCP Server vào AI Clients & IDEs
            </h3>
            <p class="text-[11px] text-neutral-500 dark:text-neutral-400 mt-0.5">
              Sử dụng endpoint HTTP duy nhất để cung cấp toàn bộ công cụ In-House cho các AI Assistant.
            </p>
          </div>

          <!-- Claude Desktop Guide -->
          <div class="p-3.5 rounded-xl bg-[#f9f9f9] dark:bg-[#212121] border border-[#e5e5e5] dark:border-[#2e2e2e] space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-xs text-slate-800 dark:text-[#ececec] flex items-center gap-1.5">
                <i class="pi pi-box text-orange-500"></i>
                Claude Desktop Configuration
              </span>
              <button
                type="button"
                class="text-[11px] px-2.5 py-1 rounded bg-[#10A37F] hover:bg-[#0e8f6f] text-white font-medium transition cursor-pointer flex items-center gap-1"
                @click="copyClaudeConfig"
              >
                <i class="pi pi-copy text-[10px]"></i>
                <span>{{ jsonCopied ? 'Đã sao chép!' : 'Sao chép JSON' }}</span>
              </button>
            </div>
            <p class="text-[11px] text-neutral-500 dark:text-neutral-400">
              Dán đoạn cấu hình này vào file <code class="font-mono bg-neutral-200 dark:bg-[#2a2a2a] px-1 py-0.5 rounded text-[10px]">claude_desktop_config.json</code>:
            </p>
            <pre class="p-2.5 rounded-lg bg-neutral-100 dark:bg-[#151515] text-[11px] font-mono text-slate-800 dark:text-emerald-400 overflow-x-auto border border-neutral-200 dark:border-[#2b2b2b]">{
  "mcpServers": {
    "mcp-protocol-studio": {
      "url": "{{ settingsStore.apiBaseUrl }}/mcp"
    }
  }
}</pre>
          </div>

          <!-- Cursor & Windsurf Guide -->
          <div class="p-3.5 rounded-xl bg-[#f9f9f9] dark:bg-[#212121] border border-[#e5e5e5] dark:border-[#2e2e2e] space-y-2">
            <span class="font-semibold text-xs text-slate-800 dark:text-[#ececec] flex items-center gap-1.5">
              <i class="pi pi-code text-indigo-500"></i>
              Cursor & Windsurf IDE
            </span>
            <p class="text-[11px] text-neutral-500 dark:text-neutral-400 leading-relaxed">
              Mở <b>Cursor Settings → Features → MCP Servers → Add New MCP Server</b>:<br/>
              • Type: <b>sse</b> hoặc <b>http</b><br/>
              • Server URL: <code class="font-mono bg-neutral-200 dark:bg-[#2a2a2a] px-1 py-0.5 rounded text-[10px]">{{ settingsStore.apiBaseUrl }}/mcp</code>
            </p>
          </div>
        </div>

        <!-- TAB 3: ABOUT -->
        <div v-if="activeTab === 'about'" class="space-y-4">
          <div class="flex items-center gap-3 p-4 rounded-xl bg-neutral-50 dark:bg-[#212121] border border-[#e5e5e5] dark:border-[#2e2e2e]">
            <div class="w-12 h-12 rounded-xl bg-emerald-500/10 dark:bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 text-2xl font-bold">
              <i class="pi pi-box"></i>
            </div>
            <div>
              <h2 class="text-sm font-bold text-slate-900 dark:text-white">
                MCP PROTOCOL STUDIO
              </h2>
              <p class="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
                In-House MCP Server Registry & Stateless Pure HTTP Gateway
              </p>
              <div class="flex items-center gap-2 mt-2">
                <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-mono font-bold">
                  v1.0.0 Release
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-neutral-200 dark:bg-[#333333] text-neutral-600 dark:text-neutral-300 font-mono">
                  JSON-RPC 2.0
                </span>
              </div>
            </div>
          </div>

          <div class="space-y-2 text-neutral-600 dark:text-neutral-400 text-[11px] leading-relaxed">
            <p>
              • <b>Registry Server:</b> Quản lý, đóng gói và xuất bản MCP Server nội bộ (PostgreSQL, Docker, Puppeteer, Filesystem, Documents...).
            </p>
            <p>
              • <b>Pure HTTP Gateway:</b> Chuyển đổi linh hoạt giữa giao thức MCP JSON-RPC tiêu chuẩn và REST API trực tiếp.
            </p>
            <p>
              • <b>Interactive Swagger Docs:</b>
              <a
                :href="`${settingsStore.apiBaseUrl}/docs`"
                target="_blank"
                class="text-[#10A37F] hover:underline ml-1 font-mono"
              >
                {{ settingsStore.apiBaseUrl }}/docs
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Controls -->
    <template #footer>
      <div class="flex items-center justify-between w-full">
        <Button
          label="Mặc định"
          text
          size="small"
          class="!text-xs !text-neutral-500 hover:!text-slate-800 dark:hover:!text-white"
          @click="resetDefaults"
        />
        <div class="flex items-center gap-2">
          <Button
            label="Hủy"
            text
            size="small"
            class="!text-xs"
            @click="emit('update:visible', false)"
          />
          <Button
            label="Lưu cài đặt"
            size="small"
            class="!text-xs !bg-[#10A37F] hover:!bg-[#0e8f6f] !text-white !font-semibold !rounded-lg !py-1.5 !px-4"
            @click="saveSettings"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>
