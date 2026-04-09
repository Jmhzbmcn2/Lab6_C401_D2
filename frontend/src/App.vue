<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo-area">
        <h1>Vinmec Healthcare Assistant</h1>
        <span class="badge">AI RAG Agent v2.0</span>
      </div>
    </header>
    <main class="main-content">
      <Chat />
    </main>
  </div>
</template>

<script setup>
import Chat from './components/Chat.vue'
</script>

<style>
/* Global Resets & Fonts */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
  --primary: #2C64E3;
  --primary-hover: #1f4cb3;
  --secondary: #00D2FF;
  --bg-color: #0d1117;
  --panel-bg: #161b22;
  --text-main: #c9d1d9;
  --text-muted: #8b949e;
  --border: #30363d;
  --accent: #238636;
  --radius: 12px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-main);
  height: 100vh;
  overflow: hidden;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-header {
  background: rgba(22, 27, 34, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
}

.logo-area h1 {
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
  margin-right: 1rem;
}

.badge {
  background: rgba(35, 134, 54, 0.2);
  color: #3fb950;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid rgba(63, 185, 80, 0.4);
}

.main-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}
</style>
