<template>
  <div class="scoreboard">
    <h3>🏆 排行榜</h3>
    <div class="player-rows">
      <div
        v-for="snake in sortedSnakes"
        :key="snake.player_id"
        class="player-row"
        :class="{ dead: !snake.alive, me: snake.player_id === myPlayerId }"
      >
        <span class="rank-emoji">{{ snake.emoji }}</span>
        <span class="rank-name" :style="{ color: snake.color }">{{ snake.username }}</span>
        <span class="rank-stats">
          <span class="stat">🔢 {{ snake.length }}</span>
          <span class="stat">💀 {{ snake.kills }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  gameState: Object,
  myPlayerId: String,
})

const sortedSnakes = computed(() => {
  if (!props.gameState?.snakes) return []
  return [...props.gameState.snakes].sort((a, b) => {
    // Sort by kills desc, then by length desc
    if (b.kills !== a.kills) return b.kills - a.kills
    return b.length - a.length
  })
})
</script>

<style scoped>
.scoreboard {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 16px;
  min-width: 200px;
  z-index: 80;
}

h3 {
  font-size: 14px;
  margin-bottom: 8px;
  color: #FFD700;
}

.player-rows {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.player-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 6px;
  border-radius: 6px;
  font-size: 13px;
  transition: background 0.15s;
}

.player-row.me {
  background: rgba(255, 255, 255, 0.08);
}

.player-row.dead {
  opacity: 0.4;
}

.rank-emoji {
  font-size: 18px;
}

.rank-name {
  flex: 1;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 80px;
}

.rank-stats {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #aaa;
}

.stat {
  white-space: nowrap;
}
</style>
