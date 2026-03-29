<template>
  <div v-if="mySnake && !mySnake.alive" class="respawn-overlay">
    <div class="respawn-content">
      <div class="respawn-icon">💀</div>
      <div class="respawn-timer">{{ displayTimer }}</div>
      <div class="respawn-text">复活倒计时</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  gameState: Object,
  myPlayerId: String,
})

const mySnake = computed(() => {
  if (!props.gameState?.snakes) return null
  return props.gameState.snakes.find(s => s.player_id === props.myPlayerId)
})

const displayTimer = computed(() => {
  if (!mySnake.value) return ''
  const t = mySnake.value.respawn_timer
  if (t <= 0) return '复活中...'
  return Math.ceil(t)
})
</script>

<style scoped>
.respawn-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 50;
  pointer-events: none;
}

.respawn-content {
  text-align: center;
}

.respawn-icon {
  font-size: 64px;
  margin-bottom: 16px;
  animation: pulse 1s ease-in-out infinite;
}

.respawn-timer {
  font-size: 96px;
  font-weight: 900;
  color: #ff4444;
  text-shadow: 0 0 30px rgba(255, 68, 68, 0.5);
  line-height: 1;
}

.respawn-text {
  font-size: 20px;
  color: #aaa;
  margin-top: 12px;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
</style>
