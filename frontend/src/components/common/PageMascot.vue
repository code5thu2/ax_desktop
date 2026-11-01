<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { DEFAULT_DIRECTIONS_SPRITE, DEFAULT_REACTIONS_SPRITE } from './mascotSprites'

export interface PageMascotProps {
  /** Path or URL to the 3x3 directions sprite sheet (WebP/SVG/PNG). */
  directions?: string
  /** Path or URL to the 3x3 reactions sprite sheet (WebP/SVG/PNG). */
  reactions?: string
  /** Mascot size in pixels (width and height square). Default: 80. */
  size?: number | string
  /** Dead zone radius in pixels around mascot center where it looks straight forward. Default: 35. */
  deadZone?: number
  /** Duration in milliseconds that a reaction frame stays visible when poked. Default: 500. */
  reactDuration?: number
  /** Set to true for pixel-art sprites to enable crisp pixelated rendering. Default: false. */
  pixelated?: boolean
  /** Accessible aria-label for screen readers. Default: 'Page Mascot'. */
  label?: string
  /** When true, pointer tracking is disabled and mascot stays centered. Default: false. */
  disabled?: boolean
  /** Controlled external state: 'idle' | 'tracking' | 'thinking' | 'reacting'. */
  state?: 'idle' | 'tracking' | 'thinking' | 'reacting'
}

const props = withDefaults(defineProps<PageMascotProps>(), {
  directions: '/mascots/tv-directions.webp',
  reactions: '/mascots/tv-reactions.webp',
  size: 80,
  deadZone: 35,
  reactDuration: 500,
  pixelated: false,
  label: 'Page Mascot',
  disabled: false,
  state: 'tracking',
})

const emit = defineEmits<{
  (e: 'poke', reactionIndex: number): void
  (e: 'directionChange', col: number, row: number): void
}>()

const mascotEl = ref<HTMLElement | null>(null)
const currentCol = ref(1) // 0: Left, 1: Center, 2: Right
const currentRow = ref(1) // 0: Top, 1: Center, 2: Bottom

const isReacting = ref(false)
const currentReactionIndex = ref(0)
const isSquashing = ref(false)

let reactTimer: ReturnType<typeof setTimeout> | null = null
let squashTimer: ReturnType<typeof setTimeout> | null = null
let rafId: number | null = null
let lastPointerX = 0
let lastPointerY = 0

// Direction mapping for 8 angular sectors (45 degrees each)
// Angle 0 is East (Right: col 2, row 1)
const SECTOR_DIRECTIONS: [number, number][] = [
  [2, 1], // Sector 0: East (Right)
  [2, 2], // Sector 1: South-East (Bottom-Right)
  [1, 2], // Sector 2: South (Bottom)
  [0, 2], // Sector 3: South-West (Bottom-Left)
  [0, 1], // Sector 4: West (Left)
  [0, 0], // Sector 5: North-West (Top-Left)
  [1, 0], // Sector 6: North (Top)
  [2, 0], // Sector 7: North-East (Top-Right)
]

const resolvedDirectionsUrl = computed(() => props.directions || DEFAULT_DIRECTIONS_SPRITE)
const resolvedReactionsUrl = computed(() => props.reactions || DEFAULT_REACTIONS_SPRITE)

const numericSize = computed(() => {
  const val = typeof props.size === 'string' ? parseInt(props.size, 10) : props.size
  return isNaN(val) ? 80 : val
})

/**
 * Calculates background position percentages based on current grid cell (0, 1, 2).
 * Each step in a 3x3 grid is exactly 50% (0%, 50%, 100%).
 */
const backgroundPosStyle = computed(() => {
  if (isReacting.value) {
    const col = currentReactionIndex.value % 3
    const row = Math.floor(currentReactionIndex.value / 3)
    return `${col * 50}% ${row * 50}%`
  }
  return `${currentCol.value * 50}% ${currentRow.value * 50}%`
})

const activeSpriteUrl = computed(() => {
  return isReacting.value ? resolvedReactionsUrl.value : resolvedDirectionsUrl.value
})

/**
 * Updates head look direction based on latest pointer coordinates.
 * Throttled to display refresh rate via requestAnimationFrame.
 */
function updateTracking() {
  rafId = null
  if (props.disabled || props.state === 'idle' || isReacting.value || !mascotEl.value) {
    return
  }

  const rect = mascotEl.value.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2

  const dx = lastPointerX - centerX
  const dy = lastPointerY - centerY
  const distance = Math.hypot(dx, dy)

  let newCol = 1
  let newRow = 1

  // Dead zone check: when pointer is close, look straight forward
  if (distance > props.deadZone) {
    const angleRad = Math.atan2(dy, dx)
    const angleDeg = (angleRad * 180) / Math.PI
    // Normalize to 0..360 with a 22.5 degree offset so sector 0 is centered on East
    const normalizedAngle = (angleDeg + 360 + 22.5) % 360
    const sector = Math.floor(normalizedAngle / 45) % 8
    const [c, r] = SECTOR_DIRECTIONS[sector]
    newCol = c
    newRow = r
  }

  if (newCol !== currentCol.value || newRow !== currentRow.value) {
    currentCol.value = newCol
    currentRow.value = newRow
    emit('directionChange', newCol, newRow)
  }
}

function onPointerMove(e: PointerEvent) {
  if (props.disabled || props.state === 'idle') return

  lastPointerX = e.clientX
  lastPointerY = e.clientY

  if (rafId === null) {
    rafId = window.requestAnimationFrame(updateTracking)
  }
}

/**
 * Triggers a poke reaction with squash animation.
 * Cycles or picks a specific reaction index (0..8).
 */
function poke(reactionIndex?: number) {
  if (reactTimer) clearTimeout(reactTimer)
  if (squashTimer) clearTimeout(squashTimer)

  // Pick index: explicitly passed or rotate through 0..8
  const nextIdx = typeof reactionIndex === 'number'
    ? Math.max(0, Math.min(8, Math.floor(reactionIndex)))
    : (currentReactionIndex.value + 1) % 9

  currentReactionIndex.value = nextIdx
  isReacting.value = true
  isSquashing.value = true

  emit('poke', nextIdx)

  // Squash release after 140ms
  squashTimer = setTimeout(() => {
    isSquashing.value = false
  }, 140)

  // Revert back to tracking direction after reactDuration
  reactTimer = setTimeout(() => {
    isReacting.value = false
    if (rafId === null) {
      rafId = window.requestAnimationFrame(updateTracking)
    }
  }, props.reactDuration)
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('pointermove', onPointerMove, { passive: true })
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('pointermove', onPointerMove)
  }
  if (rafId !== null) cancelAnimationFrame(rafId)
  if (reactTimer) clearTimeout(reactTimer)
  if (squashTimer) clearTimeout(squashTimer)
})

defineExpose({
  poke,
  currentCol,
  currentRow,
  isReacting,
})
</script>

<template>
  <div
    ref="mascotEl"
    role="button"
    tabindex="0"
    :aria-label="props.label"
    class="page-mascot-container relative inline-block cursor-pointer select-none transition-transform duration-150 transform-gpu active:scale-95 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 rounded-full"
    :class="[
      isSquashing ? 'scale-y-[0.88] scale-x-[1.08]' : 'scale-100',
      props.pixelated ? 'rendering-pixelated' : '',
    ]"
    :style="{
      width: `${numericSize}px`,
      height: `${numericSize}px`,
    }"
    @click="poke()"
    @keydown.enter.prevent="poke()"
    @keydown.space.prevent="poke()"
  >
    <!-- Mascot Sprite Canvas: 3x3 Sprite Sheet -->
    <div
      class="w-full h-full rounded-2xl overflow-hidden transition-[background-position] duration-75 ease-out"
      :style="{
        backgroundImage: `url('${activeSpriteUrl}')`,
        backgroundSize: '300% 300%',
        backgroundPosition: backgroundPosStyle,
        backgroundRepeat: 'no-repeat',
      }"
    />
  </div>
</template>

<style scoped>
.rendering-pixelated {
  image-rendering: pixelated;
  image-rendering: crisp-edges;
}

@media (prefers-reduced-motion: reduce) {
  .page-mascot-container {
    transition: none !important;
    transform: none !important;
  }
}
</style>
