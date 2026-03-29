<template>
  <div class="dpad-container" v-show="visible">
    <div class="dpad">
      <button
        class="dpad-btn up"
        @touchstart.prevent="onPress('up')"
        @touchend.prevent="onRelease"
      >▲</button>
      <div class="dpad-mid-row">
        <button
          class="dpad-btn left"
          @touchstart.prevent="onPress('left')"
          @touchend.prevent="onRelease"
        >◀</button>
        <div class="dpad-center"></div>
        <button
          class="dpad-btn right"
          @touchstart.prevent="onPress('right')"
          @touchend.prevent="onRelease"
        >▶</button>
      </div>
      <button
        class="dpad-btn down"
        @touchstart.prevent="onPress('down')"
        @touchend.prevent="onRelease"
      >▼</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['direction'])

defineProps({
  visible: { type: Boolean, default: true },
})

let repeatTimer = null
let currentDir = null

function onPress(dir) {
  currentDir = dir
  emit('direction', dir)
  clearInterval(repeatTimer)
  repeatTimer = setInterval(() => {
    if (currentDir) emit('direction', currentDir)
  }, 120)
}

function onRelease() {
  currentDir = null
  clearInterval(repeatTimer)
  repeatTimer = null
}
</script>

<style scoped>
.dpad-container {
  position: absolute;
  bottom: 32px;
  left: 32px;
  z-index: 200;
  user-select: none;
  -webkit-user-select: none;
  touch-action: none;
  pointer-events: none;
}

.dpad {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  pointer-events: auto;
}

.dpad-mid-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dpad-btn {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.8);
  font-size: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  touch-action: manipulation;
  pointer-events: auto;
  transition: background 0.1s;
}

.dpad-btn:active {
  background: rgba(255, 255, 255, 0.35);
}

.dpad-center {
  width: 56px;
  height: 56px;
}
</style>
