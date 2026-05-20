<template>
  <div class="page-container">
    <div class="top-bar">
      <button class="back-btn" @click="router.push('/profile')">&#8592; 返回</button>
    </div>
    <h1 class="page-title">完整解读</h1>
    <p class="page-subtitle">你的塔罗占卜详细报告</p>

    <div class="loading-spinner" v-if="loading">正在生成详细解读，请稍候...</div>

    <div class="detail-sections fade-in" v-else-if="detail">
      <div v-for="(sec, idx) in sections" :key="idx" class="detail-section">
        <h3 class="section-heading" v-if="sec.title">✦ {{ sec.title }} ✦</h3>
        <div class="section-body" v-html="sec.body"></div>
      </div>
    </div>

    <div class="actions fade-in" v-if="detail">
      <button class="btn-primary" @click="handleShare">生成分享图片</button>
    </div>

    <div class="loading-spinner" v-if="sharing">正在生成分享图片...</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { marked } from 'marked'
import { useRouter, useRoute } from 'vue-router'
import { getReading, generateDetail } from '../api/reading'
import { generateShareImage } from '../api/reading'

const router = useRouter()
const route = useRoute()
const readingId = route.params.readingId

const loading = ref(true)
const sharing = ref(false)
const detail = ref('')

const sections = computed(() => {
  if (!detail.value) return []
  const result = []
  const parts = detail.value.split(/(【[^】]+】)/g)
  let currentTitle = ''

  for (const part of parts) {
    const match = part.match(/【([^】]+)】/)
    if (match) {
      if (currentTitle || result.length === 0) {
        // Push previous section
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

onMounted(async () => {
  try {
    const { data } = await getReading(readingId)
    if (data.detailed_reading) {
      detail.value = data.detailed_reading
    } else {
      const { data: detailData } = await generateDetail(readingId)
      detail.value = detailData.detailed_reading
    }
  } catch (e) {
    alert('获取解读失败')
  } finally {
    loading.value = false
  }
})

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
</style>
