<template>
  <canvas ref="canvasRef" class="game-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  gameState: Object,
  myPlayerId: String,
})

const canvasRef = ref(null)
let ctx = null
let animFrameId = null
let cellSize = 16

const APPLE_EMOJIS = {
  speed: '⚡',
  growth: '🌟',
  invincible: '🛡️',
  slow: '⏳',
  heart: '❤️',
  spike: '🔺',
}

onMounted(() => {
  const canvas = canvasRef.value
  ctx = canvas.getContext('2d')
  resize()
  window.addEventListener('resize', resize)
  render()
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  if (animFrameId) cancelAnimationFrame(animFrameId)
})

function resize() {
  const canvas = canvasRef.value
  if (!canvas) return
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight

  // Calculate cell size to fit the map
  const state = props.gameState
  const mapW = state?.map_width || 60
  const mapH = state?.map_height || 40
  const margin = 20
  cellSize = Math.min(
    (canvas.width - margin * 2) / mapW,
    (canvas.height - margin * 2) / mapH,
  )
  cellSize = Math.max(8, Math.floor(cellSize))
}

function render() {
  if (!ctx || !canvasRef.value) return
  draw()
  animFrameId = requestAnimationFrame(render)
}

function draw() {
  const canvas = canvasRef.value
  const state = props.gameState
  if (!canvas || !ctx) return

  const w = canvas.width
  const h = canvas.height
  const mapW = state?.map_width || 60
  const mapH = state?.map_height || 40

  // Map offset to center
  const totalW = mapW * cellSize
  const totalH = mapH * cellSize
  const offsetX = Math.floor((w - totalW) / 2)
  const offsetY = Math.floor((h - totalH) / 2)

  // Clear
  ctx.fillStyle = '#0a0a1a'
  ctx.fillRect(0, 0, w, h)

  // Slow motion effect
  if (state?.slow_motion) {
    ctx.fillStyle = 'rgba(100, 100, 200, 0.08)'
    ctx.fillRect(0, 0, w, h)
  }

  // Draw grid background
  ctx.fillStyle = '#0f0f2a'
  ctx.fillRect(offsetX, offsetY, totalW, totalH)

  // Grid lines
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)'
  ctx.lineWidth = 1
  for (let x = 0; x <= mapW; x++) {
    ctx.beginPath()
    ctx.moveTo(offsetX + x * cellSize, offsetY)
    ctx.lineTo(offsetX + x * cellSize, offsetY + totalH)
    ctx.stroke()
  }
  for (let y = 0; y <= mapH; y++) {
    ctx.beginPath()
    ctx.moveTo(offsetX, offsetY + y * cellSize)
    ctx.lineTo(offsetX + totalW, offsetY + y * cellSize)
    ctx.stroke()
  }

  // Border
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
  ctx.lineWidth = 2
  ctx.strokeRect(offsetX, offsetY, totalW, totalH)

  if (!state) return

  // Draw apples
  for (const apple of state.apples || []) {
    const ax = offsetX + apple.position.x * cellSize
    const ay = offsetY + apple.position.y * cellSize
    const emoji = APPLE_EMOJIS[apple.type] || '🍎'
    ctx.font = `${cellSize - 2}px serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(emoji, ax + cellSize / 2, ay + cellSize / 2 + 1)
  }

  // Draw snakes
  for (const snake of state.snakes || []) {
    if (!snake.alive || snake.body.length === 0) continue

    const color = snake.color || '#4CAF50'
    const isInvincible = snake.invincible
    const isDamageImmune = snake.damage_immune
    const hp = snake.hp || 0
    const spikes = snake.spikes || 0

    // Blinking effect for damage immune: alternate alpha
    const blinkAlpha = isDamageImmune && Math.floor(Date.now() / 150) % 2 === 0 ? 0.25 : 1.0

    // Draw body segments (from tail to head)
    for (let i = snake.body.length - 1; i >= 1; i--) {
      const seg = snake.body[i]
      const sx = offsetX + seg.x * cellSize
      const sy = offsetY + seg.y * cellSize

      ctx.globalAlpha = blinkAlpha

      // Determine segment type
      const isSpikeSegment = spikes > 0 && i >= snake.body.length - spikes
      const isHeartSegment = i >= 1 && i <= hp

      if (isInvincible && Math.floor(Date.now() / 150) % 2 === 0) {
        ctx.shadowColor = color
        ctx.shadowBlur = 10
      }

      if (isHeartSegment) {
        // Heart segment: draw red background + heart emoji
        ctx.fillStyle = '#cc0000'
        const padding = 1
        drawRoundRect(ctx, sx + padding, sy + padding, cellSize - padding * 2, cellSize - padding * 2, 4)
        ctx.fill()
        ctx.font = `${cellSize - 4}px serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText('❤️', sx + cellSize / 2, sy + cellSize / 2 + 1)
      } else if (isSpikeSegment) {
        // Spike segment: orange background + spike emoji
        ctx.fillStyle = '#ff6600'
        const padding = 1
        drawRoundRect(ctx, sx + padding, sy + padding, cellSize - padding * 2, cellSize - padding * 2, 4)
        ctx.fill()
        ctx.font = `${cellSize - 4}px serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText('🔺', sx + cellSize / 2, sy + cellSize / 2 + 1)
      } else {
        // Regular body segment
        ctx.fillStyle = color
        const padding = 1
        const radius = 4
        drawRoundRect(ctx, sx + padding, sy + padding, cellSize - padding * 2, cellSize - padding * 2, radius)
        ctx.fill()
      }

      ctx.shadowBlur = 0
    }

    // Draw head with emoji
    const head = snake.body[0]
    const hx = offsetX + head.x * cellSize
    const hy = offsetY + head.y * cellSize

    ctx.globalAlpha = blinkAlpha

    if (isInvincible && Math.floor(Date.now() / 150) % 2 === 0) {
      ctx.shadowColor = '#FFD700'
      ctx.shadowBlur = 15
    }

    // Head background
    ctx.fillStyle = color
    drawRoundRect(ctx, hx + 1, hy + 1, cellSize - 2, cellSize - 2, 4)
    ctx.fill()
    ctx.shadowBlur = 0

    // Emoji on head
    ctx.font = `${cellSize - 4}px serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(snake.emoji || '🐍', hx + cellSize / 2, hy + cellSize / 2 + 1)

    // Speed boost indicator
    if (snake.speed_boost) {
      ctx.font = `${Math.max(10, cellSize / 2)}px serif`
      ctx.fillText('💨', hx + cellSize, hy)
    }

    ctx.globalAlpha = 1.0
  }

  // Slow motion banner
  if (state.slow_motion) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.4)'
    ctx.fillRect(w / 2 - 100, 10, 200, 32)
    ctx.font = 'bold 16px sans-serif'
    ctx.fillStyle = '#FFD700'
    ctx.textAlign = 'center'
    ctx.fillText('⏳ 慢动作', w / 2, 32)
  }
}

function drawRoundRect(ctx, x, y, w, h, r) {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.lineTo(x + w - r, y)
  ctx.quadraticCurveTo(x + w, y, x + w, y + r)
  ctx.lineTo(x + w, y + h - r)
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h)
  ctx.lineTo(x + r, y + h)
  ctx.quadraticCurveTo(x, y + h, x, y + h - r)
  ctx.lineTo(x, y + r)
  ctx.quadraticCurveTo(x, y, x + r, y)
  ctx.closePath()
}
</script>

<style scoped>
.game-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
