/**
 * Default Built-in 3x3 Sprite Sheet Assets for PageMascot
 * =======================================================
 * Provides zero-dependency, ultra-lightweight SVG Data URIs representing
 * a 3x3 directions grid and a 3x3 reactions grid for a cute AI mascot.
 * 
 * Works out-of-the-box without requiring external image files, while allowing
 * custom external WebP/PNG sprite sheets (e.g. from koboyo.com) via props.
 */

/**
 * Creates an SVG representing a 300x300 canvas divided into a 3x3 grid (each cell 100x100).
 */
function createDirectionsSvg(): string {
  // Eye offsets for 9 directions [row][col] -> [dy, dx]
  // Row 0: Top, Row 1: Center, Row 2: Bottom
  // Col 0: Left, Col 1: Center, Col 2: Right
  const offsets = [
    [[-8, -8], [-8, 0], [-8, 8]],   // Top-Left,    Top,    Top-Right
    [[0, -8],  [0, 0],  [0, 8]],    // Left,        Center, Right
    [[8, -8],  [8, 0],  [8, 8]],    // Bottom-Left, Bottom, Bottom-Right
  ]

  let cells = ''
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      const cx = c * 100
      const cy = r * 100
      const [dy, dx] = offsets[r][c]

      cells += `
        <g transform="translate(${cx}, ${cy})">
          <!-- Mascot Outer Head / Body -->
          <rect x="14" y="16" width="72" height="68" rx="22" fill="#10B981" />
          <rect x="18" y="20" width="64" height="60" rx="18" fill="#059669" opacity="0.25" />
          
          <!-- Cute Ears / Horns -->
          <path d="M 22 18 L 14 6 L 32 14 Z" fill="#10B981" />
          <path d="M 78 18 L 86 6 L 68 14 Z" fill="#10B981" />

          <!-- Face Screen -->
          <rect x="22" y="26" width="56" height="48" rx="14" fill="#0F172A" />

          <!-- Eyes with dynamic look offset [dx, dy] -->
          <circle cx="${38 + dx}" cy="${48 + dy}" r="6.5" fill="#38BDF8" />
          <circle cx="${36 + dx}" cy="${46 + dy}" r="2.2" fill="#FFFFFF" />

          <circle cx="${62 + dx}" cy="${48 + dy}" r="6.5" fill="#38BDF8" />
          <circle cx="${60 + dx}" cy="${46 + dy}" r="2.2" fill="#FFFFFF" />

          <!-- Cute Cheeks -->
          <circle cx="28" cy="56" r="3" fill="#F43F5E" opacity="0.65" />
          <circle cx="72" cy="56" r="3" fill="#F43F5E" opacity="0.65" />

          <!-- Smile -->
          <path d="M ${46 + dx * 0.4} ${58 + dy * 0.4} Q 50 ${62 + dy * 0.4} ${54 + dx * 0.4} ${58 + dy * 0.4}" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" fill="none" />
        </g>
      `
    }
  }

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">${cells}</svg>`
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

/**
 * Creates a 3x3 reactions SVG sheet with 9 distinct expressions for clicks/pokes.
 */
function createReactionsSvg(): string {
  // 9 reactions:
  // 0: Happy (^ ^)
  // 1: Surprised (O O)
  // 2: Wink (> ^)
  // 3: Heart eyes (<3 <3)
  // 4: Squint / Poked (> <)
  // 5: Star eyes (* *)
  // 6: Dizzy (@ @)
  // 7: Cat face (:3)
  // 8: Blushing closed eyes (u u)
  const reactions = [
    // 0: Happy (^ ^)
    `
      <path d="M 32 50 Q 38 42 44 50" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" fill="none" />
      <path d="M 56 50 Q 62 42 68 50" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" fill="none" />
      <path d="M 46 58 Q 50 63 54 58" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" fill="none" />
    `,
    // 1: Surprised (O O)
    `
      <circle cx="38" cy="46" r="8" fill="#38BDF8" />
      <circle cx="62" cy="46" r="8" fill="#38BDF8" />
      <ellipse cx="50" cy="60" rx="4" ry="5.5" fill="#38BDF8" />
    `,
    // 2: Wink (> -)
    `
      <path d="M 33 44 L 43 50 L 33 56" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" />
      <circle cx="62" cy="50" r="6.5" fill="#38BDF8" />
      <path d="M 47 58 Q 51 63 55 58" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" fill="none" />
    `,
    // 3: Heart eyes
    `
      <path d="M 38 44 C 34 38 27 42 38 54 C 49 42 42 38 38 44 Z" fill="#F43F5E" />
      <path d="M 62 44 C 58 38 51 42 62 54 C 73 42 66 38 62 44 Z" fill="#F43F5E" />
      <path d="M 46 59 Q 50 64 54 59" stroke="#F43F5E" stroke-width="2" stroke-linecap="round" fill="none" />
    `,
    // 4: Squint / Poked (> <)
    `
      <path d="M 33 44 L 42 49 L 33 54" stroke="#FBBF24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" />
      <path d="M 67 44 L 58 49 L 67 54" stroke="#FBBF24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" />
      <ellipse cx="50" cy="59" rx="3.5" ry="3" fill="#FBBF24" />
    `,
    // 5: Star eyes
    `
      <text x="38" y="55" font-size="18" font-family="sans-serif" text-anchor="middle" fill="#FBBF24">★</text>
      <text x="62" y="55" font-size="18" font-family="sans-serif" text-anchor="middle" fill="#FBBF24">★</text>
      <path d="M 46 58 Q 50 63 54 58" stroke="#FBBF24" stroke-width="2" stroke-linecap="round" fill="none" />
    `,
    // 6: Dizzy (@ @)
    `
      <text x="38" y="54" font-size="17" font-weight="bold" font-family="monospace" text-anchor="middle" fill="#A855F7">@</text>
      <text x="62" y="54" font-size="17" font-weight="bold" font-family="monospace" text-anchor="middle" fill="#A855F7">@</text>
      <path d="M 46 61 Q 50 56 54 61" stroke="#A855F7" stroke-width="2" stroke-linecap="round" fill="none" />
    `,
    // 7: Cat face (:3)
    `
      <circle cx="38" cy="48" r="6" fill="#38BDF8" />
      <circle cx="62" cy="48" r="6" fill="#38BDF8" />
      <path d="M 44 58 Q 47 62 50 58 Q 53 62 56 58" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" fill="none" />
    `,
    // 8: Blushing closed eyes (u u)
    `
      <path d="M 33 46 Q 38 52 43 46" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" fill="none" />
      <path d="M 57 46 Q 62 52 67 46" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" fill="none" />
      <ellipse cx="50" cy="58" rx="2.5" ry="2" fill="#38BDF8" />
    `,
  ]

  let cells = ''
  for (let i = 0; i < 9; i++) {
    const c = i % 3
    const r = Math.floor(i / 3)
    const cx = c * 100
    const cy = r * 100

    cells += `
      <g transform="translate(${cx}, ${cy})">
        <!-- Body -->
        <rect x="14" y="16" width="72" height="68" rx="22" fill="#10B981" />
        <rect x="18" y="20" width="64" height="60" rx="18" fill="#059669" opacity="0.25" />
        
        <!-- Ears -->
        <path d="M 22 18 L 14 6 L 32 14 Z" fill="#10B981" />
        <path d="M 78 18 L 86 6 L 68 14 Z" fill="#10B981" />

        <!-- Face Screen -->
        <rect x="22" y="26" width="56" height="48" rx="14" fill="#0F172A" />

        <!-- Cheeks -->
        <circle cx="28" cy="56" r="3.5" fill="#F43F5E" opacity="0.8" />
        <circle cx="72" cy="56" r="3.5" fill="#F43F5E" opacity="0.8" />

        <!-- Expression Detail -->
        ${reactions[i]}
      </g>
    `
  }

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">${cells}</svg>`
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

export const DEFAULT_DIRECTIONS_SPRITE = createDirectionsSvg()
export const DEFAULT_REACTIONS_SPRITE = createReactionsSvg()
