<template>
  <div class="fortune-page" :style="{ backgroundImage: `url(${bgImg})` }">
    <div class="fortune-overlay">
      <!-- Header -->
      <div class="top-bar">
        <span class="app-title">&#10022; 塔罗占卜</span>
        <button class="profile-btn" @click="router.push('/profile')">{{ userStore.nickname || '我' }}</button>
      </div>

      <!-- Spacer -->
      <div class="spacer"></div>

      <!-- Fortune teller speech -->
      <div class="speech-bubble fade-in">
        <p class="speech-text">"来吧，告诉我你心中的疑惑。<br />命运的丝线已经缠绕，让我为你揭晓答案。"</p>
      </div>

      <!-- Quick suggestions: 2 rows marquee -->
      <div class="suggestions-wrapper fade-in">
        <div class="marquee-row">
          <div class="marquee-track">
            <button v-for="(s, i) in suggestions" :key="'a'+i" class="suggestion-chip" @click="question = s">{{ s }}</button>
            <button v-for="(s, i) in suggestions" :key="'b'+i" class="suggestion-chip" @click="question = s">{{ s }}</button>
          </div>
        </div>
        <div class="marquee-row marquee-row-reverse">
          <div class="marquee-track">
            <button v-for="(s, i) in suggestions2" :key="'c'+i" class="suggestion-chip" @click="question = s">{{ s }}</button>
            <button v-for="(s, i) in suggestions2" :key="'d'+i" class="suggestion-chip" @click="question = s">{{ s }}</button>
          </div>
        </div>
      </div>

      <!-- Question input -->
      <div class="input-section fade-in">
        <textarea v-model="question" placeholder="在这里写下你的问题..." rows="2"></textarea>
        <button class="btn-primary" @click="startReading" :disabled="!question.trim() || submitting">
          {{ submitting ? '占卜中...' : '开始占卜' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useReadingStore } from '../stores/reading'
import { createReading } from '../api/reading'
import bgImg from '../assets/taroter.jpg'

const router = useRouter()
const userStore = useUserStore()
const readingStore = useReadingStore()

const question = ref('')
const submitting = ref(false)

const suggestions = [
  '我的正缘什么时候出现？',
  '这段感情值得继续吗？',
  '未来三个月会有什么转机？',
  '我的财运最近会好转吗？',
]
const suggestions2 = [
  '最近的感情会有什么变化？',
  '我近期的事业运势如何？',
  '我和他的缘分有多深？',
  '家人之间的关系会改善吗？',
]

async function startReading() {
  submitting.value = true
  readingStore.reset()
  readingStore.question = question.value.trim()

  // Fire API async — don't block, navigate immediately
  readingStore.readingPromise = createReading({ question_text: question.value.trim() })
    .then(({ data }) => {
      readingStore.currentReadingId = data.id
      readingStore.briefReading = data.brief_reading
      readingStore.cardsDrawn = data.cards_drawn
      readingStore.status = data.status
      readingStore.readingResolved = true
    })
    .catch(() => {
      readingStore.readingError = true
    })

  router.push('/cards')
  submitting.value = false
}
</script>

<style scoped>
.fortune-page {
  min-height: 100vh;
  background-size: auto 75vh;
  background-position: center top;
  background-repeat: no-repeat;
  background-color: #0a051e;
}
.fortune-overlay {
  min-height: 100vh;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, rgba(10, 5, 30, 0) 0%, rgba(10, 5, 30, 0) 55%, rgba(10, 5, 30, 0.85) 68%, rgba(10, 5, 30, 1) 78%);
}
.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.app-title { font-size: var(--font-size-lg); color: var(--color-accent); }
.profile-btn {
  padding: 6px 14px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px; color: var(--color-text); font-size: var(--font-size-sm);
}
.spacer { flex: 1; min-height: 40px; }
.speech-bubble {
  background: rgba(255,255,255,0.08); border-radius: 16px;
  padding: 14px 18px; margin-bottom: 12px; text-align: center;
  border: 1px solid rgba(255,255,255,0.1);
  backdrop-filter: blur(8px);
}
.speech-text { font-size: var(--font-size-base); color: var(--color-text); line-height: 1.6; font-style: italic; }
.suggestions-wrapper {
  display: flex; flex-direction: column; gap: 6px;
  margin: 4px -16px 8px; padding: 0 16px;
  overflow: hidden;
}
.marquee-row {
  overflow: hidden;
  mask-image: linear-gradient(to right, transparent, black 8%, black 92%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 8%, black 92%, transparent);
}
.marquee-track {
  display: flex; gap: 6px; width: max-content;
  animation: marquee 20s linear infinite;
}
.marquee-row-reverse .marquee-track {
  animation: marquee-reverse 24s linear infinite;
}
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
@keyframes marquee-reverse {
  0% { transform: translateX(-50%); }
  100% { transform: translateX(0); }
}
.suggestion-chip {
  white-space: nowrap; padding: 5px 10px;
  background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15);
  border-radius: 14px; color: var(--color-primary-light); font-size: 11px;
  transition: all 0.3s; flex-shrink: 0;
}
.suggestion-chip:hover { border-color: var(--color-accent); color: var(--color-accent); }
.input-section { margin-top: 8px; }
textarea {
  width: 100%; padding: 12px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
  border-radius: var(--radius-sm); color: var(--color-text); font-size: var(--font-size-base);
  resize: none; margin-bottom: 12px; font-family: inherit;
  backdrop-filter: blur(6px);
}
</style>
