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
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&subset=vietnamese&display=swap');

:root {
  --primary: #004F9E;
  --primary-hover: #0062c3;
  --secondary: #00A3E0;
  --bg-color: #f4f7f6;
  --panel-bg: #ffffff;
  --text-main: #2d3748;
  --text-muted: #718096;
  --border: #e2e8f0;
  --accent: #E31837;
  --radius: 12px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
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
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
}

.logo-area h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary);
  display: inline-block;
  margin-right: 1rem;
}

.badge {
  background: rgba(0, 163, 224, 0.1);
  color: var(--secondary);
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(0, 163, 224, 0.3);
}

.main-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}
</style>
