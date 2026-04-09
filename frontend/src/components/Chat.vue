<template>
  <div class="chat-layout">
    <!-- Main Chat Window -->
    <div class="chat-window">
      <div class="message-feed" ref="feedRef">
        <div v-for="(msg, index) in messages" :key="index" :class="['message-bubble', msg.role]">
          <div class="avatar">
            <span v-if="msg.role === 'user'">👤</span>
            <span v-else>🤖</span>
          </div>
          <div class="message-content">
            <div v-if="msg.role === 'assistant'" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
            <div v-else class="text-body">{{ msg.content }}</div>
            
            <div v-if="msg.role === 'assistant' && msg.debug_trace && msg.debug_trace.length > 0" class="debug-toggle" @click="toggleDebug(index)">
              {{ msg.showDebug ? 'Hide Debug Trace' : 'View Debug Trace' }}
            </div>
            
            <transition name="slide-fade">
              <div v-if="msg.role === 'assistant' && msg.showDebug" class="debug-panel">
                <h4>LangGraph Execution Trace</h4>
                <div v-for="(step, i) in msg.debug_trace" :key="i" class="debug-step">
                  <div class="step-title">Node: {{ step.step }}</div>
                  <div class="step-data">
                    <pre>{{ JSON.stringify(step.output, null, 2) }}</pre>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>
        
        <div v-if="isLoading" class="message-bubble assistant loading">
          <div class="avatar">🤖</div>
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
      
      <div class="chat-input-area">
        <form @submit.prevent="sendMessage" class="input-form">
          <input 
            type="text" 
            v-model="query" 
            placeholder="Tra cứu giá dịch vụ (vd: Sinh mổ tại Times City)" 
            :disabled="isLoading"
            class="glow-input"
          />
          <button type="submit" :disabled="isLoading || !query.trim()" class="send-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2"/></svg>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUpdated } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

const API_URL = 'http://localhost:8000/chat'

const query = ref('')
const messages = ref([{
  role: 'assistant',
  content: 'Xin chào! Tôi là trợ lý RAG LangGraph của Vinmec. Tôi có thể giúp bạn tra cứu trực tiếp bảng giá dịch vụ từ cơ sở dữ liệu dựa trên từ khóa hoặc khu vực (Times City, Smart City).'
}])
const isLoading = ref(false)
const feedRef = ref(null)

const renderMarkdown = (text) => {
  return marked(text || '')
}

const toggleDebug = (index) => {
  messages.value[index].showDebug = !messages.value[index].showDebug
}

const scrollToBottom = () => {
  if (feedRef.value) {
    feedRef.value.scrollTop = feedRef.value.scrollHeight
  }
}

onUpdated(scrollToBottom)

const sendMessage = async () => {
  const text = query.value.trim()
  if (!text) return
  
  messages.value.push({ role: 'user', content: text })
  query.value = ''
  isLoading.value = true
  
  try {
    const res = await axios.post(API_URL, { query: text })
    
    messages.value.push({
      role: 'assistant',
      content: res.data.answer,
      debug_trace: res.data.debug_trace || [],
      showDebug: false
    })
  } catch (error) {
    console.error(error)
    messages.value.push({
      role: 'assistant',
      content: `**Lỗi:** Không thể kết nối đến backend. Vui lòng kiểm tra lại LangGraph API server.\n\n\`${error.message}\``
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.chat-layout {
  height: 100%;
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  padding: 1rem;
}

.chat-window {
  flex: 1;
  background: var(--panel-bg);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  overflow: hidden;
}

.message-feed {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-bubble {
  display: flex;
  gap: 1rem;
  max-width: 85%;
}

.message-bubble.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.message-bubble.assistant .avatar {
  background: linear-gradient(135deg, rgba(44,100,227,0.2), rgba(0,210,255,0.2));
  border-color: rgba(0,210,255,0.3);
}

.message-content {
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border);
  padding: 1rem 1.2rem;
  border-radius: 0 12px 12px 12px;
  line-height: 1.6;
}

.message-bubble.user .message-content {
  background: linear-gradient(145deg, var(--primary), var(--primary-hover));
  border-color: var(--primary);
  color: white;
  border-radius: 12px 0 12px 12px;
}

.debug-toggle {
  margin-top: 10px;
  font-size: 0.8rem;
  color: var(--secondary);
  cursor: pointer;
  display: inline-block;
  padding: 4px 8px;
  border: 1px solid rgba(0,210,255,0.3);
  border-radius: 4px;
  transition: all 0.2s;
}
.debug-toggle:hover {
  background: rgba(0,210,255,0.1);
}

.debug-panel {
  margin-top: 1rem;
  background: #0d1117;
  border: 1px solid #444c56;
  border-radius: 8px;
  padding: 1rem;
}
.debug-panel h4 {
  font-size: 0.85rem;
  color: #8b949e;
  margin-bottom: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.debug-step {
  margin-bottom: 1rem;
  border-left: 2px solid var(--accent);
  padding-left: 0.8rem;
}
.step-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e6edf3;
  margin-bottom: 0.4rem;
}
.step-data pre {
  font-family: inherit;
  font-size: 0.8rem;
  color: #79c0ff;
  white-space: pre-wrap;
}

.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

.chat-input-area {
  padding: 1.5rem;
  border-top: 1px solid var(--border);
  background: rgba(0,0,0,0.2);
}

.input-form {
  display: flex;
  gap: 1rem;
  position: relative;
}

.glow-input {
  flex: 1;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 1rem 1.5rem;
  color: white;
  font-family: inherit;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
}

.glow-input:focus {
  border-color: var(--secondary);
  box-shadow: 0 0 15px rgba(0,210,255,0.2);
  background: rgba(255,255,255,0.05);
}

.send-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.send-btn svg {
  width: 20px;
  height: 20px;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(0,210,255,0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #30363d;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}
.typing-indicator span {
  width: 6px;
  height: 6px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  45% { transform: scale(1); }
}

/* Markdown Standard Overrides */
:deep(.markdown-body) {
  color: var(--text-main);
  font-size: 0.95rem;
}
:deep(.markdown-body p) { margin-bottom: 0.8em; }
:deep(.markdown-body p:last-child) { margin-bottom: 0; }
:deep(.markdown-body h1), :deep(.markdown-body h2), :deep(.markdown-body h3) { color: white; margin: 1em 0 0.5em; }
:deep(.markdown-body ul), :deep(.markdown-body ol) { margin-left: 1.5em; margin-bottom: 0.8em; }
:deep(.markdown-body li) { margin-bottom: 0.3em; }
</style>
