import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export const useGameStore = defineStore('game', () => {
  const roomInfo = ref(null)
  const gameState = ref(null)
  const isPlaying = ref(false)
  const myPlayerId = ref('')

  function setRoomInfo(info) {
    roomInfo.value = info
  }

  function setGameState(state) {
    gameState.value = state
  }

  function setPlaying(val) {
    isPlaying.value = val
  }

  function setMyPlayerId(id) {
    myPlayerId.value = id
  }

  function reset() {
    roomInfo.value = null
    gameState.value = null
    isPlaying.value = false
    myPlayerId.value = ''
  }

  return {
    roomInfo, gameState, isPlaying, myPlayerId,
    setRoomInfo, setGameState, setPlaying, setMyPlayerId, reset,
  }
})
