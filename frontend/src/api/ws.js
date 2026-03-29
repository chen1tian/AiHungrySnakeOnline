import { useAuthStore } from '../stores/auth.js'
import { useGameStore } from '../stores/game.js'

let ws = null
let reconnectTimer = null

export function connectToRoom(roomId, onOpen) {
  disconnect()

  const auth = useAuthStore()
  const game = useGameStore()

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const url = `${protocol}//${host}/ws/game/${roomId}?token=${auth.token}`

  ws = new WebSocket(url)

  ws.onopen = () => {
    console.log('WebSocket connected')
    if (onOpen) onOpen()
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleMessage(data, game)
    } catch (e) {
      console.error('Failed to parse WS message:', e)
    }
  }

  ws.onclose = (event) => {
    console.log('WebSocket closed:', event.code, event.reason)
    ws = null
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
}

function handleMessage(data, game) {
  switch (data.type) {
    case 'room_info':
      game.setRoomInfo(data)
      break
    case 'game_start':
      game.setPlaying(true)
      break
    case 'state':
      game.setGameState(data)
      break
    case 'player_join':
    case 'player_leave':
      // Room info will be sent separately
      break
    default:
      console.log('Unknown WS message type:', data.type)
  }
}

export function sendMessage(data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data))
  }
}

export function disconnect() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (ws) {
    ws.close()
    ws = null
  }
}
