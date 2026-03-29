<template>
  <div class="lobby-page">
    <header class="lobby-header">
      <h1>🐍 贪吃蛇Online</h1>
      <div class="user-info">
        <span>👤 {{ auth.username }}</span>
        <button class="logout-btn" @click="handleLogout">退出</button>
      </div>
    </header>

    <div class="lobby-content">
      <div class="actions">
        <button class="create-btn" @click="showCreateModal = true">
          ➕ 创建房间
        </button>
        <button class="refresh-btn" @click="fetchRooms">
          🔄 刷新
        </button>
      </div>

      <div class="room-list">
        <div v-if="rooms.length === 0" class="empty">
          暂无房间，快来创建一个吧！
        </div>
        <div
          v-for="room in rooms"
          :key="room.room_id"
          class="room-card"
        >
          <div class="room-info">
            <h3>{{ room.room_name }}</h3>
            <p>🆔 {{ room.room_id }} · 👥 {{ room.player_count }}人 · {{ room.status === 'waiting' ? '等待中' : '游戏中' }}</p>
          </div>
          <button
            v-if="room.status === 'waiting'"
            class="join-btn"
            @click="joinRoom(room.room_id)"
            :disabled="joining"
          >
            加入
          </button>
          <span v-else class="playing-badge">游戏中</span>
        </div>
      </div>
    </div>

    <!-- Create Room Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h2>创建房间</h2>
        <div class="field">
          <label>房间名称</label>
          <input v-model="newRoomName" placeholder="请输入房间名称" maxlength="30" />
        </div>
        <p v-if="createError" class="error">{{ createError }}</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showCreateModal = false">取消</button>
          <button class="confirm-btn" @click="createRoom" :disabled="creating">
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import http from '../api/http.js'

const router = useRouter()
const auth = useAuthStore()

const rooms = ref([])
const showCreateModal = ref(false)
const newRoomName = ref('新房间')
const createError = ref('')
const creating = ref(false)
const joining = ref(false)

onMounted(() => {
  fetchRooms()
})

async function fetchRooms() {
  try {
    const res = await http.get('/api/rooms')
    rooms.value = res.data.rooms
  } catch (e) {
    console.error('Failed to fetch rooms:', e)
  }
}

async function createRoom() {
  createError.value = ''
  creating.value = true
  try {
    const res = await http.post('/api/rooms', { room_name: newRoomName.value })
    showCreateModal.value = false
    router.push(`/room/${res.data.room_id}`)
  } catch (e) {
    createError.value = e.response?.data?.detail || '创建失败'
  } finally {
    creating.value = false
  }
}

async function joinRoom(roomId) {
  joining.value = true
  try {
    await http.post(`/api/rooms/${roomId}/join`)
    router.push(`/room/${roomId}`)
  } catch (e) {
    alert(e.response?.data?.detail || '加入失败')
  } finally {
    joining.value = false
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.lobby-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.lobby-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  margin-bottom: 24px;
}

.lobby-header h1 {
  font-size: 24px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logout-btn {
  background: rgba(255,255,255,0.1);
  color: #aaa;
  padding: 6px 14px;
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.create-btn {
  background: linear-gradient(135deg, #16c9f2, #0ea5e9);
  color: #fff;
  padding: 12px 28px;
}

.refresh-btn {
  background: rgba(255,255,255,0.1);
  color: #ccc;
  padding: 12px 20px;
}

.room-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty {
  text-align: center;
  color: #666;
  padding: 60px 0;
  font-size: 16px;
}

.room-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 16px 20px;
}

.room-info h3 {
  font-size: 17px;
  margin-bottom: 4px;
}

.room-info p {
  font-size: 13px;
  color: #888;
}

.join-btn {
  background: #4CAF50;
  color: #fff;
  padding: 8px 24px;
}

.playing-badge {
  color: #ff9800;
  font-size: 13px;
  font-weight: 600;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: #1a1a2e;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 32px;
  width: 380px;
}

.modal h2 {
  margin-bottom: 20px;
}

.field {
  margin-bottom: 16px;
}

.field label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  color: #aaa;
}

.field input {
  width: 100%;
}

.error {
  color: #ff6b6b;
  font-size: 13px;
  margin-bottom: 12px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.cancel-btn {
  background: rgba(255,255,255,0.1);
  color: #aaa;
}

.confirm-btn {
  background: linear-gradient(135deg, #16c9f2, #0ea5e9);
  color: #fff;
}
</style>
