<script setup lang="ts">
import { computed } from 'vue'

export type LogoVariant =
  | 'network'     // 1. Quỹ đạo nốt giao thức (Orbit Nodes)
  | 'socket'      // 2. Ngàm cắm mô-đun (Dock Socket)
  | 'modular'     // 3. Phân tầng mô-đun (Layered Stack)
  | 'hexacore'    // 4. Lục giác giao thức MCP (Hexagonal Core)
  | 'isocube'     // 5. Khối lập phương công cụ (Isometric Tool Cube)
  | 'synapse'     // 6. Dải ruy-băng vô cực (Infinity Ribbon Loop)
  | 'concentric'  // 7. Sóng mở rộng đa tầng (Concentric Radar Chevrons)

interface Props {
  variant?: LogoVariant
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'hero' | number
  glow?: boolean
  breathing?: boolean
  ambient?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'network',
  size: 'md',
  glow: true,
  breathing: false,
  ambient: false,
})

// Dynamic unique ID for SVG definitions to avoid collisions
const uid = Math.random().toString(36).substring(2, 9)
const gradId = `mcp-grad-${uid}`
const gradUpperId = `mcp-upper-${uid}`
const gradLowerId = `mcp-lower-${uid}`
const isoTopId = `mcp-iso-top-${uid}`
const isoLeftId = `mcp-iso-left-${uid}`
const isoRightId = `mcp-iso-right-${uid}`
const filterId = `mcp-glow-${uid}`

const sizeClasses = computed(() => {
  if (typeof props.size === 'number') return ''
  switch (props.size) {
    case 'xs': return 'w-4 h-4'
    case 'sm': return 'w-6 h-6'
    case 'md': return 'w-8 h-8'
    case 'lg': return 'w-12 h-12'
    case 'xl': return 'w-16 h-16'
    case '2xl': return 'w-20 h-20'
    case 'hero': return 'w-24 h-24'
    default: return 'w-8 h-8'
  }
})

const sizeStyle = computed(() => {
  if (typeof props.size === 'number') {
    return { width: `${props.size}px`, height: `${props.size}px` }
  }
  return {}
})
</script>

<template>
  <div
    class="relative inline-flex items-center justify-center select-none"
    :class="[breathing ? 'logo-breathing-wrapper' : '']"
  >
    <!-- Ambient glowing aura (100% đồng bộ AppLogo gốc) -->
    <div
      v-if="ambient || breathing"
      class="absolute rounded-full pointer-events-none -z-10"
      :class="[
        breathing ? 'aura-breathing bg-gradient-to-tr from-indigo-500/40 via-violet-500/45 to-sky-400/35 blur-2xl' : 'bg-indigo-500/30 blur-xl',
        typeof size === 'number' ? 'w-full h-full scale-150' :
        (size === 'hero' || size === '2xl' ? 'w-36 h-36' : (size === 'xl' || size === 'lg' ? 'w-24 h-24' : 'w-12 h-12'))
      ]"
    ></div>

    <!-- Emblem SVG (100% Vector Phẳng, MCP Protocol Studio) -->
    <svg
      :class="[
        sizeClasses,
        glow && !breathing ? 'drop-shadow-[0_0_20px_rgba(99,102,241,0.65)]' : '',
        breathing ? 'svg-breathing' : '',
      ]"
      :style="sizeStyle"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <!-- MCP Protocol Studio Primary Gradient: Sky Blue -> Electric Indigo -> Deep Violet -->
        <linearGradient :id="gradId" x1="32" y1="8" x2="32" y2="54" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#38bdf8" />
          <stop offset="35%" stop-color="#6366f1" />
          <stop offset="100%" stop-color="#7c3aed" />
        </linearGradient>

        <!-- Upper Tier Gradient (Sky to Indigo) -->
        <linearGradient :id="gradUpperId" x1="32" y1="8" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#38bdf8" />
          <stop offset="100%" stop-color="#6366f1" />
        </linearGradient>

        <!-- Lower Tier Gradient (Indigo to Violet) -->
        <linearGradient :id="gradLowerId" x1="32" y1="35" x2="32" y2="54" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#6366f1" />
          <stop offset="100%" stop-color="#7c3aed" />
        </linearGradient>

        <!-- Isometric Cube Facet Gradients -->
        <linearGradient :id="isoTopId" x1="13" y1="10" x2="51" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#38bdf8" />
          <stop offset="100%" stop-color="#60a5fa" />
        </linearGradient>
        <linearGradient :id="isoLeftId" x1="13" y1="21" x2="32" y2="54" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#6366f1" />
          <stop offset="100%" stop-color="#4f46e5" />
        </linearGradient>
        <linearGradient :id="isoRightId" x1="51" y1="21" x2="32" y2="54" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#8b5cf6" />
          <stop offset="100%" stop-color="#7c3aed" />
        </linearGradient>

        <!-- Soft Glow Filter (Exact same as AppLogo) -->
        <filter :id="filterId" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="1.2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <!-- ======================================================== -->
      <!-- KIỂU 1: PROTOCOL ORBIT NETWORK                           -->
      <!-- Giữ 100% Chevron & Sao cũ, thêm 3 Node Protocol tinh gọn-->
      <!-- ======================================================== -->
      <g v-if="variant === 'network'" class="logo-variant-network">
        <!-- Subtle Dashed Protocol Orbit Trace -->
        <ellipse
          cx="32"
          cy="34"
          rx="27"
          ry="24"
          stroke="rgba(99, 102, 241, 0.4)"
          stroke-width="1.2"
          stroke-dasharray="3 3"
          fill="none"
        />

        <!-- Connection Traces to Nodes -->
        <line x1="32" y1="5.5" x2="32" y2="8" stroke="rgba(56, 189, 248, 0.8)" stroke-width="1.2" stroke-linecap="round" />
        <line x1="56" y1="48" x2="51" y2="46" stroke="rgba(99, 102, 241, 0.8)" stroke-width="1.2" stroke-linecap="round" />
        <line x1="8" y1="48" x2="13" y2="46" stroke="rgba(124, 58, 237, 0.8)" stroke-width="1.2" stroke-linecap="round" />

        <!-- 3 Satellite Protocol Nodes (Model - Context - Protocol) -->
        <circle cx="32" cy="4" r="2.8" fill="#38bdf8" stroke="rgba(255, 255, 255, 0.8)" stroke-width="1" />
        <circle cx="32" cy="4" r="1.1" fill="#ffffff" />
        <circle cx="56.5" cy="48" r="2.8" fill="#6366f1" stroke="rgba(255, 255, 255, 0.8)" stroke-width="1" />
        <circle cx="56.5" cy="48" r="1.1" fill="#ffffff" />
        <circle cx="7.5" cy="48" r="2.8" fill="#7c3aed" stroke="rgba(255, 255, 255, 0.8)" stroke-width="1" />
        <circle cx="7.5" cy="48" r="1.1" fill="#ffffff" />

        <!-- MCP Delta / Chevron Shape -->
        <path
          d="M 32 8 C 35 8 38 11 40 15 L 53 43 C 55 47.5 53 52 48.5 53.5 C 45 54.5 39 50 32 46 C 25 50 19 54.5 15.5 53.5 C 11 52 9 47.5 11 43 L 24 15 C 26 11 29 8 32 8 Z"
          :fill="`url(#${gradId})`"
          stroke="rgba(255, 255, 255, 0.45)"
          stroke-width="1.2"
        />

        <!-- Exact Original Glowing 4-point AI Star -->
        <path
          d="M 32 19 C 32 25.5 34.5 28 41 28 C 34.5 28 32 30.5 32 37 C 32 30.5 29.5 28 23 28 C 29.5 28 32 25.5 32 19 Z"
          fill="#ffffff"
          :filter="`url(#${filterId})`"
        />
      </g>

      <!-- ======================================================== -->
      <!-- KIỂU 2: MODULAR DOCK SOCKET                              -->
      <!-- Chevron gốc có khe cắm tinh xảo + Module Plugin rời     -->
      <!-- ======================================================== -->
      <g v-else-if="variant === 'socket'" class="logo-variant-socket">
        <!-- Main Delta Chevron with Geometric Dock Notch at Base -->
        <path
          d="M 32 8 C 35 8 38 11 40 15 L 53 43 C 55 47.5 53 52 48.5 53.5 C 45 54.5 39 50 36 47.5 L 36 42.5 C 36 41 35 40 33.5 40 L 30.5 40 C 29 40 28 41 28 42.5 L 28 47.5 C 25 50 19 54.5 15.5 53.5 C 11 52 9 47.5 11 43 L 24 15 C 26 11 29 8 32 8 Z"
          :fill="`url(#${gradId})`"
          stroke="rgba(255, 255, 255, 0.45)"
          stroke-width="1.2"
        />

        <!-- Dock Socket Contact Pins -->
        <line x1="30" y1="40" x2="30" y2="42" stroke="rgba(255, 255, 255, 0.6)" stroke-width="1" />
        <line x1="34" y1="40" x2="34" y2="42" stroke="rgba(255, 255, 255, 0.6)" stroke-width="1" />

        <!-- Plug-in Skill / MCP Module Block -->
        <path
          d="M 29.5 44 L 34.5 44 C 35.5 44 36.2 45 35.8 46 L 34 50.5 C 33.5 51.5 32.5 52 32 52 C 31.5 52 30.5 51.5 30 50.5 L 28.2 46 C 27.8 45 28.5 44 29.5 44 Z"
          :fill="`url(#${gradLowerId})`"
          stroke="rgba(255, 255, 255, 0.65)"
          stroke-width="1.1"
        />
        <circle cx="32" cy="47.5" r="1.2" fill="#ffffff" :filter="`url(#${filterId})`" />

        <!-- Exact Original Glowing 4-point AI Star -->
        <path
          d="M 32 19 C 32 25.5 34.5 28 41 28 C 34.5 28 32 30.5 32 37 C 32 30.5 29.5 28 23 28 C 29.5 28 32 25.5 32 19 Z"
          fill="#ffffff"
          :filter="`url(#${filterId})`"
        />
      </g>

      <!-- ======================================================== -->
      <!-- KIỂU 3: MODULAR LAYERED STACK                            -->
      <!-- Chevron gốc được tách tầng chính xác biểu thị Mô-đun    -->
      <!-- ======================================================== -->
      <g v-else-if="variant === 'modular'" class="logo-variant-modular">
        <!-- Upper Modular Tier: Skill Intelligence Chevron -->
        <path
          d="M 32 8 C 35 8 38 11 40 15 L 46.5 29 C 47.2 30.5 46.2 32 44.5 32 L 19.5 32 C 17.8 32 16.8 30.5 17.5 29 L 24 15 C 26 11 29 8 32 8 Z"
          :fill="`url(#${gradUpperId})`"
          stroke="rgba(255, 255, 255, 0.45)"
          stroke-width="1.2"
        />

        <!-- Lower Modular Tier: MCP Host Foundation Base -->
        <path
          d="M 18.5 35.5 L 45.5 35.5 C 47.2 35.5 48.2 36.8 48.8 38.2 L 53 43 C 55 47.5 53 52 48.5 53.5 C 45 54.5 39 50 32 46 C 25 50 19 54.5 15.5 53.5 C 11 52 9 47.5 11 43 L 15.2 38.2 C 15.8 36.8 16.8 35.5 18.5 35.5 Z"
          :fill="`url(#${gradLowerId})`"
          stroke="rgba(255, 255, 255, 0.45)"
          stroke-width="1.2"
        />

        <!-- Alignment Connector Micro-Nodes in the Seam -->
        <circle cx="27" cy="33.8" r="0.9" fill="rgba(255, 255, 255, 0.85)" />
        <circle cx="32" cy="33.8" r="1.1" fill="#38bdf8" />
        <circle cx="37" cy="33.8" r="0.9" fill="rgba(255, 255, 255, 0.85)" />

        <!-- Glowing 4-point AI Star in Upper Tier -->
        <path
          d="M 32 16.5 C 32 21 33.8 22.8 38 22.8 C 33.8 22.8 32 24.6 32 29 C 32 24.6 30.2 22.8 26 22.8 C 30.2 22.8 32 21 32 16.5 Z"
          fill="#ffffff"
          :filter="`url(#${filterId})`"
        />
      </g>

      <!-- ======================================================== -->
      <!-- KIỂU 4: HEXAGONAL PROTOCOL CORE                          -->
      <!-- Khối Lục giác MCP chứa lõi âm bản Delta 'A' & Sao trung tâm-->
      <!-- ======================================================== -->
      <g v-else-if="variant === 'hexacore'" class="logo-variant-hexacore">
        <!-- Rounded Hexagonal Outer Shell -->
        <path
          d="M 32 6.5 C 34 6.5 35.5 7.4 36.5 8.2 L 51.5 17 C 53 18 54 19.8 54 21.8 L 54 42.2 C 54 44.2 53 46 51.5 47 L 36.5 55.8 C 35.5 56.6 34 57.5 32 57.5 C 30 57.5 28.5 56.6 27.5 55.8 L 12.5 47 C 11 46 10 44.2 10 42.2 L 10 21.8 C 10 19.8 11 18 12.5 17 L 27.5 8.2 C 28.5 7.4 30 6.5 32 6.5 Z"
          :fill="`url(#${gradId})`"
          stroke="rgba(255, 255, 255, 0.5)"
          stroke-width="1.2"
        />

        <!-- Inner Negative-Space Delta 'A' Sanctuary -->
        <path
          d="M 32 16 C 34 16 35.8 17.8 37 20.5 L 44.5 37.5 C 45.5 40 44 42.5 41.5 43 C 39.5 43.5 36 41 32 38.5 C 28 41 24.5 43.5 22.5 43 C 20 42.5 18.5 40 19.5 37.5 L 27 20.5 C 28.2 17.8 30 16 32 16 Z"
          fill="#171717"
          stroke="rgba(255, 255, 255, 0.2)"
          stroke-width="1"
        />

        <!-- 6 Micro-Pins on Hexagon Corners -->
        <circle cx="32" cy="7.5" r="1.3" fill="#ffffff" />
        <circle cx="53.5" cy="22" r="1.3" fill="#ffffff" />
        <circle cx="53.5" cy="42" r="1.3" fill="#ffffff" />
        <circle cx="32" cy="56.5" r="1.3" fill="#ffffff" />
        <circle cx="10.5" cy="42" r="1.3" fill="#ffffff" />
        <circle cx="10.5" cy="22" r="1.3" fill="#ffffff" />

        <!-- Glowing Star nestled in the heart of Hexagon -->
        <path
          d="M 32 22 C 32 26.5 33.8 28.2 38 28.2 C 33.8 28.2 32 29.9 32 34.4 C 32 29.9 30.2 28.2 26 28.2 C 30.2 28.2 32 26.5 32 22 Z"
          fill="#ffffff"
          :filter="`url(#${filterId})`"
        />
      </g>

      <!-- ======================================================== -->
      <!-- KIỂU 5: ISOMETRIC TOOL CUBE                              -->
      <!-- Khối Lập Phương MCP 3D phẳng: 3 mặt Sky - Indigo - Violet-->
      <!-- ======================================================== -->
      <g v-else-if="variant === 'isocube'" class="logo-variant-isocube">
        <!-- Top Facet (Sky Blue Facet) -->
        <path
          d="M 32 9 L 52 20.5 L 32 32 L 12 20.5 Z"
          :fill="`url(#${isoTopId})`"
          stroke="rgba(255, 255, 255, 0.6)"
          stroke-width="1.2"
        />

        <!-- Left Facet (Electric Indigo Facet) -->
        <path
          d="M 12 20.5 L 32 32 L 32 55 L 12 43.5 Z"
          :fill="`url(#${isoLeftId})`"
          stroke="rgba(255, 255, 255, 0.45)"
          stroke-width="1.2"
        />

        <!-- Right Facet (Deep Violet Facet) -->
        <path
          d="M 32 32 L 52 20.5 L 52 43.5 L 32 55 Z"
          :fill="`url(#${isoRightId})`"
          stroke="rgba(255, 255, 255, 0.45)"
          stroke-width="1.2"
        />

        <!-- Center Intersection Seams -->
        <line x1="32" y1="32" x2="32" y2="55" stroke="rgba(255, 255, 255, 0.35)" stroke-width="1.2" />

        <!-- Modular Port Grooves on Front Faces -->
        <line x1="18" y1="30" x2="26" y2="34.5" stroke="rgba(255, 255, 255, 0.4)" stroke-width="1" stroke-linecap="round" />
        <line x1="46" y1="30" x2="38" y2="34.5" stroke="rgba(255, 255, 255, 0.4)" stroke-width="1" stroke-linecap="round" />

        <!-- Glowing Star resting on Top Facet -->
        <path
          d="M 32 14 C 32 18.5 33.6 19.8 37.8 20.5 C 33.6 21.2 32 22.5 32 27 C 32 22.5 30.4 21.2 26.2 20.5 C 30.4 19.8 32 18.5 32 14 Z"
          fill="#ffffff"
          :filter="`url(#${filterId})`"
        />
      </g>

      <!-- ======================================================== -->
      <!-- KIỂU 6: INFINITY RIBBON LOOP                             -->
      <!-- Dải Ruy-Băng Vô Cực uốn thành chữ 'A' & Cầu Nối Tool     -->
      <!-- ======================================================== -->
      <g v-else-if="variant === 'synapse'" class="logo-variant-synapse">
        <!-- Fluid Outer Continuous Ribbon Loop (Forms 'A' + Infinity) -->
        <path
          d="M 15 48 C 10 43 11 35 17 27 L 27 13.5 C 29 10.5 35 10.5 37 13.5 L 47 27 C 53 35 54 43 49 48 C 45 52 38 49 32 43 C 26 49 19 52 15 48 Z"
          fill="none"
          :stroke="`url(#${gradId})`"
          stroke-width="5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- Inner Bridge / Crossbar forming the 'A' cross -->
        <path
          d="M 21.5 33.5 Q 32 30.5 42.5 33.5"
          fill="none"
          :stroke="`url(#${gradId})`"
          stroke-width="3.5"
          stroke-linecap="round"
        />

        <!-- Glowing 4-Point AI Star at Apex Junction -->
        <path
          d="M 32 17 C 32 21.5 33.8 23.2 38 23.2 C 33.8 23.2 32 24.9 32 29.4 C 32 24.9 30.2 23.2 26 23.2 C 30.2 23.2 32 21.5 32 17 Z"
          fill="#ffffff"
          :filter="`url(#${filterId})`"
        />

        <!-- Terminal Connector Points at the Loop Bases -->
        <circle cx="16" cy="46" r="1.5" fill="#38bdf8" />
        <circle cx="48" cy="46" r="1.5" fill="#7c3aed" />
      </g>

      <!-- ======================================================== -->
      <!-- KIỂU 7: CONCENTRIC MULTI-LAYER CHEVRONS                  -->
      <!-- 3 Tầng Sóng Radar Chevrons mở rộng năng lực Agentic     -->
      <!-- ======================================================== -->
      <g v-else-if="variant === 'concentric'" class="logo-variant-concentric">
        <!-- Outer MCP Protocol Wing (Dashed Radar Trace) -->
        <path
          d="M 32 5 C 36 5 40 9 43 14 L 56 42 C 58 46.5 56 51 51 52.5 C 47 53.5 40 49 32 45 C 24 49 17 53.5 13 52.5 C 8 51 6 46.5 8 42 L 21 14 C 24 9 28 5 32 5 Z"
          fill="none"
          stroke="rgba(124, 58, 237, 0.45)"
          stroke-width="1.3"
          stroke-dasharray="4 3"
        />

        <!-- Middle Skill Extension Wing (Translucent Gradient) -->
        <path
          d="M 32 10 C 35 10 38 13 40 17 L 50 39 C 51.5 42.5 50 46 46 47 C 43 48 37.5 44.5 32 41.5 C 26.5 44.5 21 48 18 47 C 14 46 12.5 42.5 14 39 L 24 17 C 26 13 29 10 32 10 Z"
          :fill="`url(#${gradId})`"
          fill-opacity="0.25"
          :stroke="`url(#${gradId})`"
          stroke-width="1.2"
        />

        <!-- Inner Core Agent Chevron (Solid & Vibrant) -->
        <path
          d="M 32 15 C 34 15 36 17 37.5 20 L 44 34 C 45 36.5 44 39 41 39.8 C 38.5 40.5 34.5 38 32 36 C 29.5 38 25.5 40.5 23 39.8 C 20 39 19 36.5 20 34 L 26.5 20 C 28 17 30 15 32 15 Z"
          :fill="`url(#${gradId})`"
          stroke="rgba(255, 255, 255, 0.6)"
          stroke-width="1.2"
        />

        <!-- Radiant Glowing AI Star at the Core -->
        <path
          d="M 32 20 C 32 24 33.5 25.5 37 25.5 C 33.5 25.5 32 27 32 31 C 32 27 30.5 25.5 27 25.5 C 30.5 25.5 32 24 32 20 Z"
          fill="#ffffff"
          :filter="`url(#${filterId})`"
        />
      </g>
    </svg>
  </div>
</template>

<style scoped>
@keyframes logoPulseBreathing {
  0%, 100% {
    transform: scale(1);
    filter: drop-shadow(0 0 18px rgba(99, 102, 241, 0.55)) drop-shadow(0 0 35px rgba(56, 189, 248, 0.3));
  }
  50% {
    transform: scale(1.09);
    filter: drop-shadow(0 0 34px rgba(99, 102, 241, 0.95)) drop-shadow(0 0 70px rgba(168, 85, 247, 0.7)) drop-shadow(0 0 95px rgba(56, 189, 248, 0.5));
  }
}

@keyframes auraBreathing {
  0%, 100% {
    opacity: 0.35;
    transform: scale(0.9);
  }
  50% {
    opacity: 0.9;
    transform: scale(1.35);
  }
}

.svg-breathing {
  animation: logoPulseBreathing 2.6s ease-in-out infinite;
}

.aura-breathing {
  animation: auraBreathing 2.6s ease-in-out infinite;
}
</style>
