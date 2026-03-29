<template>
  <div id="app-root">
    <router-view />
  </div>
</template>

<script setup>
</script>

<style>
#app-root {
  width: 100vw;
  min-height: 100vh;
  background: #1a1a2e;
  color: #eee;
}

a {
  color: #16c9f2;
  text-decoration: none;
}

button {
  cursor: pointer;
  border: none;
  border-radius: 8px;
  padding: 10px 24px;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
}

button:hover {
  filter: brightness(1.15);
}

input {
  border: 2px solid #333;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 15px;
  background: #16213e;
  color: #eee;
  outline: none;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #16c9f2;
}
</style>
