<template>
  <div class="game-page" @keydown="handleKeydown" tabindex="0" ref="gamePageRef">
    <GameCanvas
      :gameState="game.gameState"
      :myPlayerId="game.myPlayerId"
    />

    <!-- Respawn Timer Overlay -->
    <RespawnTimer :gameState="game.gameState" :myPlayerId="game.myPlayerId" />

    <!-- Scoreboard -->
    <Scoreboard :gameState="game.gameState" :myPlayerId="game.myPlayerId" />

    <!-- Leave button -->
    <button class="leave-btn" @click="leaveGame">✕ 离开</button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameStore } from '../stores/game.js'
import { connectToRoom, sendMessage, disconnect } from '../api/ws.js'
import GameCanvas from '../components/GameCanvas.vue'
import RespawnTimer from '../components/RespawnTimer.vue'
import Scoreboard from '../components/Scoreboard.vue'

const route = useRoute()
const router = useRouter()
const game = useGameStore()
const gamePageRef = ref(null)

const roomId = route.params.roomId
let lastDirection = ''

onMounted(() => {
  // Focus the game page for keyboard events
  gamePageRef.value?.focus()

  // If not already connected (e.g., direct navigation), connect
  if (!game.isPlaying) {
    connectToRoom(roomId)
  }
})

onUnmounted(() => {
  disconnect()
  game.reset()
})

function handleKeydown(e) {
  const keyMap = {
    'w': 'up', 'W': 'up', 'ArrowUp': 'up',
    's': 'down', 'S': 'down', 'ArrowDown': 'down',
    'a': 'left', 'A': 'left', 'ArrowLeft': 'left',
    'd': 'right', 'D': 'right', 'ArrowRight': 'right',
  }
  const direction = keyMap[e.key]
  if (direction && direction !== lastDirection) {
    lastDirection = direction
    sendMessage({ type: 'input', direction })
  }
}

function leaveGame() {
  disconnect()
  game.reset()
  router.push('/')
}
</script>

<style scoped>
.game-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #0a0a1a;
  outline: none;
}

.leave-btn {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 0, 0, 0.3);
  color: #fff;
  padding: 6px 14px;
  font-size: 13px;
  border-radius: 6px;
  z-index: 100;
}

.leave-btn:hover {
  background: rgba(255, 0, 0, 0.6);
}
</style>
