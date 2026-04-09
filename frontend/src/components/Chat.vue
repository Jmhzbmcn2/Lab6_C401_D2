<template>
  <div class="chat-layout">
    <!-- Main Chat Window -->
    <div class="chat-window">
      <div class="message-feed" ref="feedRef">
        <div v-for="(msg, index) in messages" :key="index" :class="['message-bubble', msg.role]">
          <div class="avatar">
            <svg v-if="msg.role === 'user'" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <svg v-else viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
          </div>
          <div class="message-content">
            <div v-if="msg.role === 'assistant'" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
            <div v-else class="text-body">{{ msg.content }}</div>
            
            <!-- Action Buttons (after bot response) -->
            <div v-if="msg.role === 'assistant' && index > 0" class="action-buttons">
              <!-- Feedback Buttons -->
              <div class="feedback-group">
                <button 
                  class="feedback-btn" 
                  :class="{ active: msg.feedback === 'like' }"
                  @click="setFeedback(index, 'like')"
                  title="Phản hồi chính xác"
                >
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
                </button>
                <button 
                  class="feedback-btn" 
                  :class="{ active: msg.feedback === 'dislike' }"
                  @click="setFeedback(index, 'dislike')"
                  title="Phản hồi chưa chính xác"
                >
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zM17 2h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"/></svg>
                </button>
                <button 
                  class="feedback-btn text-btn"
                  :class="{ active: msg.feedback === 'wrong_dept' }"
                  @click="setFeedback(index, 'wrong_dept')"
                >
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
                  Sai khoa
                </button>
                <button 
                  class="feedback-btn text-btn"
                  :class="{ active: msg.feedback === 'wrong_price' }"
                  @click="setFeedback(index, 'wrong_price')"
                >
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
                  Sai giá
                </button>
              </div>

              <!-- Call Staff Button -->
              <button class="call-staff-btn" @click="showCallModal = true">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg> 
                Gọi nhân viên tư vấn
              </button>
            </div>
            
            <div v-if="msg.role === 'assistant' && msg.debug_trace && msg.debug_trace.length > 0" class="debug-toggle" @click="toggleDebug(index)">
              {{ msg.showDebug ? 'Ẩn Debug Trace' : 'Hiện thuật toán phân tích (Dev)' }}
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
          <div class="avatar">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
          </div>
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
      
      <!-- Quick Suggestion Buttons -->
      <div class="quick-buttons-area">
        <button 
          v-for="suggestion in suggestions" 
          :key="suggestion.label"
          class="quick-btn"
          @click="sendSuggestion(suggestion.query)"
          :disabled="isLoading"
        >
          <span class="quick-icon" v-html="suggestion.icon"></span>
          {{ suggestion.label }}
        </button>
      </div>
      
      <div class="chat-input-area">
        <form @submit.prevent="sendMessage" class="input-form">
          <input 
            type="text" 
            v-model="query" 
            placeholder="Tra cứu giá dịch vụ (vd: Sinh mổ tại Times City)..." 
            :disabled="isLoading"
            class="glow-input"
          />
          <button type="submit" :disabled="isLoading || !query.trim()" class="send-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2"/></svg>
          </button>
        </form>
      </div>
    </div>

    <!-- Call Staff Modal -->
    <transition name="modal-fade">
      <div v-if="showCallModal" class="modal-overlay" @click.self="showCallModal = false">
        <div class="modal-content">
          <h3>
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; vertical-align: bottom;"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg> 
            Liên hệ tổng đài viên Vinmec
          </h3>
          <div class="hotline-list">
            <a href="tel:02439743556" class="hotline-item">
              <span class="hotline-icon"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></span>
              <div>
                <div class="hotline-name">Vinmec Times City</div>
                <div class="hotline-number">024 3974 3556</div>
              </div>
            </a>
            <a href="tel:02473000115" class="hotline-item">
              <span class="hotline-icon"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></span>
              <div>
                <div class="hotline-name">Vinmec Smart City</div>
                <div class="hotline-number">024 7300 0115</div>
              </div>
            </a>
          </div>
          <p class="modal-note">Nhân viên tư vấn sẽ hỗ trợ bạn về bảng giá, bảo hiểm và đặt lịch khám trong thời gian sớm nhất.</p>
          <button class="modal-close-btn" @click="showCallModal = false">Đóng</button>
        </div>
      </div>
    </transition>
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
  content: '**Xin chào!** Tôi là trợ lý AI của Hệ thống Y tế Vinmec.\n\nTôi có thể hỗ trợ bạn:\n- Tra cứu cập nhật bảng giá dịch vụ y tế chính xác\n- So sánh giá dịch vụ giữa chi nhánh Times City & Smart City\n- Gợi ý chuyên khoa phù hợp với nhu cầu cơ bản\n\nHãy nhập câu hỏi hoặc chọn các nút gợi ý dịch vụ phổ biến bên dưới.',
  showDebug: false,
  feedback: null
}])
const isLoading = ref(false)
const feedRef = ref(null)
const showCallModal = ref(false)

// Replaced Emojis with SVGs for suggestions
const svgUser = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`
const svgPlus = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>`
const svgBlood = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>`
const svgChart = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`
const svgSmile = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>`

const suggestions = ref([
  { icon: svgUser, label: 'Sinh mổ', query: 'Giá sinh mổ tại Vinmec' },
  { icon: svgBlood, label: 'Xét nghiệm máu', query: 'Giá các gói xét nghiệm máu' },
  { icon: svgPlus, label: 'Khám tổng quát', query: 'Giá khám sức khỏe tổng quát' },
  { icon: svgChart, label: 'So sánh giá', query: 'So sánh giá sinh thiết giữa Times City và Smart City' },
  { icon: svgSmile, label: 'Nha khoa', query: 'Giá khám và điều trị nha khoa' }
])

const renderMarkdown = (text) => {
  return marked(text || '')
}

const toggleDebug = (index) => {
  messages.value[index].showDebug = !messages.value[index].showDebug
}

const setFeedback = (index, type) => {
  const current = messages.value[index].feedback
  messages.value[index].feedback = current === type ? null : type
}

const scrollToBottom = () => {
  if (feedRef.value) {
    feedRef.value.scrollTop = feedRef.value.scrollHeight
  }
}

onUpdated(scrollToBottom)

const sendSuggestion = (text) => {
  query.value = text
  sendMessage()
}

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
      showDebug: false,
      feedback: null
    })
  } catch (error) {
    console.error(error)
    messages.value.push({
      role: 'assistant',
      content: `**Hệ thống gián đoạn:** Lỗi kết nối đến Backend Server.\n\n*(Ghi chú cho lập trình viên: Nếu Python báo lỗi thiếu module như 'genai', hãy chạy \`pip install google-genai\` trong thư mục backend để cài đặt SDK mới nhất)*\n\nChi tiết lỗi: \`${error.message}\``,
      feedback: null
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.chat-layout {
  height: 100%;
  width: 100%;
  margin: 0 auto;
  display: flex;
  background: var(--bg-color);
}

.chat-window {
  flex: 1;
  background: var(--panel-bg);
  display: flex;
  flex-direction: column;
  width: 100%;
  /* Removed border, radius, shadow for a full-viewport app feel */
}

.message-feed {
  flex: 1;
  padding: 2rem 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center; /* Center the bubbles container */
  gap: 1.5rem;
  background-color: #fbfcfd;
}

.message-bubble {
  display: flex;
  gap: 1rem;
  width: 100%;
  max-width: 800px; /* Constrain reading width inside the fluid layout */
}

.message-bubble.user {
  flex-direction: row-reverse;
}

.avatar {
  background: white;
  border: 1px solid var(--border);
  color: var(--primary);
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.message-bubble.user .avatar {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.message-content {
  background: white;
  border: 1px solid var(--border);
  padding: 1.2rem 1.4rem;
  border-radius: 0 16px 16px 16px;
  line-height: 1.6;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.message-bubble.user .message-content {
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  border-color: var(--primary);
  color: white;
  border-radius: 16px 0 16px 16px;
  box-shadow: 0 4px 12px rgba(0, 79, 158, 0.2);
}

/* === ACTION BUTTONS === */
.action-buttons {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.feedback-group {
  display: flex;
  gap: 6px;
}

.feedback-btn {
  background: #f8fafc;
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.feedback-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: var(--text-main);
}

.feedback-btn.active {
  background: rgba(0, 79, 158, 0.1);
  border-color: var(--primary);
  color: var(--primary);
  font-weight: 500;
}

.feedback-btn.text-btn {
  font-size: 0.8rem;
  padding: 6px 12px;
}

.call-staff-btn {
  margin-left: auto;
  background: var(--accent); /* Vinmec Red Accent */
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  box-shadow: 0 4px 10px rgba(227, 24, 55, 0.25);
}

.call-staff-btn:hover {
  transform: translateY(-1px);
  background: #c51530;
  box-shadow: 0 6px 14px rgba(227, 24, 55, 0.35);
}

/* === QUICK BUTTONS === */
.quick-buttons-area {
  padding: 1rem;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  background: #f8fafc;
}

.quick-btn {
  background: white;
  border: 1px solid var(--border);
  color: var(--text-main);
  border-radius: 24px;
  padding: 8px 16px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.quick-btn:hover:not(:disabled) {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(0, 79, 158, 0.04);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 79, 158, 0.1);
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-icon {
  display: flex;
  align-items: center;
  color: var(--secondary);
}

/* === DEBUG SECTION  === */
.debug-toggle {
  margin-top: 12px;
  font-size: 0.8rem;
  color: var(--text-muted);
  cursor: pointer;
  display: inline-block;
  padding: 4px 8px;
  border: 1px dashed var(--border);
  border-radius: 4px;
  transition: all 0.2s;
}
.debug-toggle:hover {
  background: #f1f5f9;
  color: var(--text-main);
}

.debug-panel {
  margin-top: 1rem;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
}
.debug-panel h4 {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.debug-step {
  margin-bottom: 1rem;
  border-left: 3px solid var(--secondary);
  padding-left: 0.8rem;
}
.step-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 0.4rem;
}
.step-data pre {
  font-family: Consolas, monospace;
  font-size: 0.8rem;
  color: var(--text-main);
  background: white;
  padding: 8px;
  border: 1px solid var(--border);
  border-radius: 4px;
  white-space: pre-wrap;
}

.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

/* === INPUT AREA === */
.chat-input-area {
  padding: 1.5rem 1rem 2rem;
  background: white;
  display: flex;
  justify-content: center;
}

.input-form {
  display: flex;
  gap: 1rem;
  width: 100%;
  max-width: 800px;
  position: relative;
}

.glow-input {
  flex: 1;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 30px;
  padding: 1.2rem 1.8rem;
  color: var(--text-main);
  font-family: inherit;
  font-size: 1.05rem;
  outline: none;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.glow-input::placeholder {
  color: #a0aec0;
}

.glow-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 79, 158, 0.1);
  background: white;
}

.send-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 12px rgba(0, 79, 158, 0.3);
}

.send-btn svg {
  width: 22px;
  height: 22px;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 79, 158, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #cbd5e1;
  box-shadow: none;
}

/* === TYPING INDICATOR === */
.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 10px 4px;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--secondary);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  45% { transform: scale(1); opacity: 1; }
}

/* === MODAL === */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(2px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 450px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.modal-content h3 {
  color: var(--primary);
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
  font-weight: 700;
}

.hotline-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 1.5rem;
}

.hotline-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 14px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
}

.hotline-item:hover {
  background: white;
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(0, 79, 158, 0.08);
  transform: translateX(4px);
}

.hotline-icon {
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(227, 24, 55, 0.1);
  padding: 10px;
  border-radius: 10px;
}

.hotline-name {
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.hotline-number {
  color: var(--text-main);
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.modal-note {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
  text-align: center;
}

.modal-close-btn {
  width: 100%;
  background: #f1f5f9;
  border: 1px solid var(--border);
  color: var(--text-main);
  border-radius: 12px;
  padding: 14px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.modal-close-btn:hover {
  background: #e2e8f0;
  color: var(--primary);
}

.modal-fade-enter-active { transition: all 0.3s ease; }
.modal-fade-leave-active { transition: all 0.2s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; transform: scale(0.95); }

/* Markdown Standard Overrides */
:deep(.markdown-body) {
  color: var(--text-main);
  font-size: 1rem;
}
:deep(.markdown-body p) { margin-bottom: 1em; }
:deep(.markdown-body p:last-child) { margin-bottom: 0; }
:deep(.markdown-body h1), :deep(.markdown-body h2), :deep(.markdown-body h3) { color: var(--primary); margin: 1.2em 0 0.6em; font-weight: 600; }
:deep(.markdown-body ul), :deep(.markdown-body ol) { margin-left: 1.5em; margin-bottom: 1em; }
:deep(.markdown-body li) { margin-bottom: 0.4em; }
:deep(.markdown-body table) { width: 100%; border-collapse: collapse; margin: 1.5em 0; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
:deep(.markdown-body th), :deep(.markdown-body td) { border: 1px solid var(--border); padding: 10px 14px; text-align: left; }
:deep(.markdown-body th) { background: #f8fafc; color: var(--text-main); font-weight: 600; text-transform: uppercase; font-size: 0.85em; letter-spacing: 0.5px; }
:deep(.markdown-body td) { background: white; }
:deep(.markdown-body table tr:hover td) { background: #fcfcfc; }
:deep(.markdown-body blockquote) { border-left: 4px solid var(--secondary); padding-left: 1.2em; color: var(--text-muted); margin: 1.2em 0; background: rgba(0, 163, 224, 0.05); padding: 10px 14px; border-radius: 0 8px 8px 0; }
:deep(.markdown-body hr) { border: none; border-top: 1px solid var(--border); margin: 1.5em 0; }
</style>
