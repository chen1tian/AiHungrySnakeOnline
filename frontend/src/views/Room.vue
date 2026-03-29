<template>
  <div class="room-page">
    <header class="room-header">
      <button class="back-btn" @click="leaveRoom">← 返回大厅</button>
      <h2>{{ roomInfo?.room_name || '房间' }}</h2>
      <span class="room-id">🆔 {{ roomId }}</span>
    </header>

    <div class="room-body">
      <!-- Player List -->
      <div class="player-section">
        <h3>玩家列表 ({{ playerList.length }})</h3>
        <div class="player-list">
          <div
            v-for="[uid, player] in playerList"
            :key="uid"
            class="player-card"
            :style="{ borderLeftColor: player.color }"
          >
            <span class="player-emoji">{{ player.emoji }}</span>
            <span class="player-name">
              {{ player.username }}
              <span v-if="uid === roomInfo?.host_id" class="host-badge">房主</span>
            </span>
            <span class="player-color-dot" :style="{ background: player.color }"></span>
          </div>
        </div>
      </div>

      <!-- Settings -->
      <div class="settings-section">
        <h3>个人设置</h3>

        <div class="setting-group">
          <label>蛇头 Emoji</label>
          <div class="emoji-picker">
            <span
              v-for="e in emojiOptions"
              :key="e"
              class="emoji-option"
              :class="{ selected: myEmoji === e }"
              @click="selectEmoji(e)"
            >{{ e }}</span>
          </div>
        </div>

        <div class="setting-group">
          <label>颜色（同色=同队）</label>
          <div class="color-picker">
            <span
              v-for="c in colorOptions"
              :key="c"
              class="color-option"
              :class="{ selected: myColor === c }"
              :style="{ background: c }"
              @click="selectColor(c)"
            ></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Start Button (host only) -->
    <div class="room-footer">
      <button
        v-if="isHost"
        class="start-btn"
        @click="startGame"
        :disabled="playerList.length < 1"
      >
        🎮 开始游戏
      </button>
      <p v-else class="wait-msg">等待房主开始游戏...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { useGameStore } from '../stores/game.js'
import { connectToRoom, sendMessage, disconnect } from '../api/ws.js'
import http from '../api/http.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const game = useGameStore()

const roomId = route.params.roomId

const emojiOptions = ['🐍', '🐉', '🦎', '🐊', '🐢', '🐲', '🦖', '🐸', '🐛', '🐝', '🦋', '🐌', '🐙', '👻', '🤖', '🎃']
const colorOptions = ['#4CAF50', '#2196F3', '#f44336', '#FF9800', '#9C27B0', '#00BCD4', '#E91E63', '#FFEB3B']

const myEmoji = ref('🐍')
const myColor = ref('#4CAF50')

const roomInfo = computed(() => game.roomInfo)
const playerList = computed(() => {
  if (!roomInfo.value?.players) return []
  return Object.entries(roomInfo.value.players)
})
const isHost = computed(() => {
  // uid is a number but host_id is string
  return roomInfo.value?.host_id === String(getMyUid())
})

function getMyUid() {
  // Parse uid from JWT
  try {
    const payload = JSON.parse(atob(auth.token.split('.')[1]))
    return payload.uid
  } catch {
    return ''
  }
}

onMounted(() => {
  game.setMyPlayerId(String(getMyUid()))
  connectToRoom(roomId)
})

onUnmounted(() => {
  // Don't disconnect if navigating to game
  if (router.currentRoute.value.name !== 'Game') {
    disconnect()
    game.reset()
  }
})

// Watch for game start
watch(() => game.isPlaying, (val) => {
  if (val) {
    router.push(`/game/${roomId}`)
  }
})

function selectEmoji(e) {
  myEmoji.value = e
  sendMessage({ type: 'settings', emoji: e, color: myColor.value })
}

function selectColor(c) {
  myColor.value = c
  sendMessage({ type: 'settings', emoji: myEmoji.value, color: c })
}

function startGame() {
  sendMessage({ type: 'start_game' })
}

async function leaveRoom() {
  try {
    await http.post(`/api/rooms/${roomId}/leave`)
  } catch {}
  disconnect()
  game.reset()
  router.push('/')
}
</script>

<style scoped>
.room-page {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.room-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  margin-bottom: 24px;
}

.back-btn {
  background: rgba(255,255,255,0.1);
  color: #ccc;
  padding: 8px 16px;
  font-size: 14px;
}

.room-id {
  margin-left: auto;
  color: #888;
  font-size: 13px;
}

.room-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.player-section h3,
.settings-section h3 {
  margin-bottom: 12px;
  font-size: 16px;
  color: #ccc;
}

.player-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.player-card {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.05);
  border-left: 4px solid #4CAF50;
  border-radius: 8px;
  padding: 12px 16px;
}

.player-emoji {
  font-size: 24px;
}

.player-name {
  flex: 1;
  font-weight: 500;
}

.host-badge {
  background: #ff9800;
  color: #000;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 6px;
  font-weight: 700;
}

.player-color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.setting-group {
  margin-bottom: 20px;
}

.setting-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #aaa;
}

.emoji-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.emoji-option {
  font-size: 28px;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  border: 2px solid transparent;
  transition: all 0.15s;
}

.emoji-option:hover {
  background: rgba(255,255,255,0.1);
}

.emoji-option.selected {
  border-color: #16c9f2;
  background: rgba(22, 201, 242, 0.15);
}

.color-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.color-option {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid transparent;
  transition: all 0.15s;
}

.color-option:hover {
  transform: scale(1.15);
}

.color-option.selected {
  border-color: #fff;
  box-shadow: 0 0 12px rgba(255,255,255,0.3);
}

.room-footer {
  padding: 20px 0;
  text-align: center;
}

.start-btn {
  background: linear-gradient(135deg, #4CAF50, #2E7D32);
  color: #fff;
  padding: 14px 48px;
  font-size: 18px;
  border-radius: 12px;
}

.start-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.wait-msg {
  color: #888;
  font-size: 16px;
}
</style>
