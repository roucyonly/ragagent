<template>
  <div class="page-container">
    <div class="top-bar">
      <button class="back-btn" @click="router.push('/profile')">&#8592; 返回</button>
    </div>
    <h1 class="page-title">完整解读</h1>
    <p class="page-subtitle">你的塔罗占卜详细报告</p>

    <div class="loading-spinner" v-show="loading">正在生成详细解读，请稍候...</div>

    <div class="detail-sections fade-in" v-show="!loading && detailText">
      <div v-for="(sec, idx) in sections" :key="idx" class="detail-section">
        <h3 class="section-heading" v-if="sec.title">✦ {{ sec.title }} ✦</h3>
        <div class="section-body" v-html="sec.body"></div>
      </div>
    </div>

    <div class="streaming-view" v-show="!loading && streamingText && !detailText">
      <div class="section-body" v-html="marked(streamingText)"></div>
      <span class="cursor">▌</span>
    </div>

    <div class="actions fade-in" v-show="detailText">
      <button class="btn-primary" @click="handleShare">生成分享图片</button>
    </div>

    <div class="loading-spinner" v-if="sharing">正在生成分享图片...</div>

    <!-- 追问区域 -->
    <div class="follow-up-area fade-in" v-show="detailText && followUpCount < 3">
      <div class="follow-up-header">还有问题？继续追问 ({{ followUpCount }}/3)</div>
      <div class="follow-up-form">
        <textarea
          v-model="followUpQuestion"
          class="follow-up-input"
          placeholder="针对当前解读，你可以继续追问..."
          rows="2"
          @keydown.ctrl.enter="handleFollowUp"
        ></textarea>
        <button class="btn-follow-up" @click="handleFollowUp" :disabled="followUpLoading || !followUpQuestion.trim()">
          <span v-if="followUpLoading">解读中...</span>
          <span v-else>追问</span>
        </button>
      </div>
    </div>

    <div class="follow-up-answer fade-in" v-if="followUpAnswer">
      <h4 class="follow-up-label">✦ 追问 {{ followUpCount }} ✦</h4>
      <div class="section-body" v-html="followUpAnswerHtml"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { marked } from 'marked'
import { useRouter, useRoute } from 'vue-router'
import { getReading, streamDetail, generateShareImage, followUp, MOCK } from '../api/reading'

const router = useRouter()
const route = useRoute()
const readingId = route.params.readingId

const loading = ref(true)
const sharing = ref(false)
const detailText = ref('')
const streamingText = ref('')
const followUpCount = ref(0)
const followUpQuestion = ref('')
const followUpLoading = ref(false)
const followUpAnswer = ref('')

const sections = computed(() => {
  if (!detailText.value) return []
  const result = []
  const parts = detailText.value.split(/(【[^】]+】)/g)
  let currentTitle = ''

  for (const part of parts) {
    const match = part.match(/【([^】]+)】/)
    if (match) {
      if (currentTitle || result.length === 0) {
        if (currentTitle) {
          result.push({ title: currentTitle, body: '' })
        }
      }
      currentTitle = match[1]
    } else {
      const text = part.trim()
      if (text) {
        result.push({ title: currentTitle, body: marked(text) })
        currentTitle = ''
      }
    }
  }
  if (currentTitle) {
    result.push({ title: currentTitle, body: '' })
  }
  return result
})

const followUpAnswerHtml = computed(() => followUpAnswer.value ? marked(followUpAnswer.value) : '')

onMounted(async () => {
  try {
    if (MOCK) {
      loading.value = true
      await fetchStreamDetail()
    } else {
      const { data } = await getReading(readingId)
      if (data.detailed_reading) {
        detailText.value = data.detailed_reading
        followUpCount.value = data.follow_up_count || 0
      } else {
        loading.value = true
        await fetchStreamDetail()
      }
    }
  } catch (e) {
    alert('获取解读失败')
  } finally {
    loading.value = false
  }
})

async function fetchStreamDetail() {
  const response = await streamDetail(readingId)
  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  loading.value = false
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const text = decoder.decode(value, { stream: true })
      const lines = text.split('\n').filter(line => line.startsWith('data: '))
      for (const line of lines) {
        try {
          const json = JSON.parse(line.slice(6))
          if (json.chunk) {
            streamingText.value += json.chunk
          } else if (json.done) {
            detailText.value = streamingText.value
            streamingText.value = ''
            followUpCount.value = (await getReading(readingId)).data.follow_up_count || 0
          }
        } catch {}
      }
    }
  } catch (e) {
    alert('获取解读失败')
  }
}

async function handleShare() {
  sharing.value = true
  try {
    const { data } = await generateShareImage(readingId)
    router.push(`/share/${readingId}`)
  } catch (e) {
    alert('生成分享图片失败')
  } finally {
    sharing.value = false
  }
}

async function handleFollowUp() {
  if (!followUpQuestion.value.trim() || followUpLoading.value) return
  followUpLoading.value = true
  try {
    const { data } = await followUp(readingId, followUpQuestion.value.trim())
    followUpAnswer.value = data.answer
    followUpCount.value = data.follow_up_count
    followUpQuestion.value = ''
  } catch (e) {
    alert('追问失败')
  } finally {
    followUpLoading.value = false
  }
}
</script>

<style scoped>
.detail-sections { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.detail-section {
  background: rgba(255,255,255,0.04); border-radius: var(--radius); padding: 20px;
  line-height: 1.8;
}
.section-heading {
  font-size: var(--font-size-lg); color: var(--color-accent);
  margin: 0 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--color-border);
}
.section-body { font-size: var(--font-size-base); color: var(--color-text); }
.section-body :deep(p) { margin: 8px 0; line-height: 1.8; }
.section-body :deep(ul), .section-body :deep(ol) { padding-left: 20px; margin: 8px 0; }
.section-body :deep(li) { margin: 4px 0; }
.section-body :deep(strong) { color: var(--color-accent); }
.section-body :deep(blockquote) {
  border-left: 3px solid var(--color-primary-light); padding-left: 12px;
  margin: 12px 0; color: var(--color-text-muted);
}
.top-bar { margin-bottom: 12px; }
.back-btn { background: none; border: none; color: var(--color-text-muted); font-size: var(--font-size-sm); }
.actions { display: flex; gap: 12px; }
.follow-up-area {
  margin-top: 20px;
  background: rgba(255,255,255,0.04);
  border-radius: var(--radius);
  padding: 16px;
}
.follow-up-header {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-bottom: 10px;
}
.follow-up-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.follow-up-input {
  width: 100%;
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--color-text);
  font-size: var(--font-size-base);
  resize: none;
  font-family: inherit;
}
.follow-up-input:focus {
  outline: none;
  border-color: var(--color-primary);
}
.btn-follow-up {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #4a1a8a, #2d1b69);
  border: 1px solid rgba(246,211,101,0.4);
  border-radius: 8px;
  color: #f6d365;
  font-size: var(--font-size-base);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}
.btn-follow-up:not(:disabled):hover {
  background: linear-gradient(135deg, #5b2d99, #3d2080);
  border-color: rgba(246,211,101,0.6);
}
.btn-follow-up:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.follow-up-answer {
  margin-top: 16px;
  background: rgba(255,255,255,0.04);
  border-radius: var(--radius);
  padding: 16px;
}
.follow-up-label {
  font-size: var(--font-size-sm);
  color: var(--color-accent);
  margin-bottom: 10px;
}
.streaming-view {
  background: rgba(255,255,255,0.04);
  border-radius: var(--radius);
  padding: 20px;
  line-height: 1.8;
  min-height: 200px;
}
.streaming-view .section-body { font-size: var(--font-size-base); color: var(--color-text); }
.streaming-view .section-body p { margin: 6px 0; }
.streaming-view .section-body strong { color: var(--color-accent); }
.streaming-view .section-body em { color: #fda085; }
.streaming-view .section-body ul, .streaming-view .section-body ol { padding-left: 18px; margin: 6px 0; }
.streaming-view .section-body li { margin: 3px 0; }
.streaming-view .section-body blockquote {
  border-left: 2px solid rgba(246,211,101,0.3);
  padding-left: 10px;
  color: var(--color-text-muted);
  margin: 8px 0;
}
.cursor {
  animation: blink 1s step-end infinite;
  color: var(--color-accent);
}
@keyframes blink {
  50% { opacity: 0; }
}
</style>