<template>
  <div class="page-container">
    <div class="top-bar">
      <button class="back-btn" @click="router.push('/profile')">&#8592; 返回</button>
    </div>
    <h1 class="page-title">完整解读</h1>
    <p class="page-subtitle">你的塔罗占卜详细报告</p>

    <div class="loading-spinner" v-if="loading">正在生成详细解读，请稍候...</div>

    <div class="detail-content fade-in" v-else-if="detail">
      <div class="detail-text" v-html="formattedDetail"></div>
    </div>

    <div class="actions fade-in" v-if="detail">
      <button class="btn-primary" @click="handleShare">生成分享图片</button>
    </div>

    <div class="loading-spinner" v-if="sharing">正在生成分享图片...</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getReading, generateDetail } from '../api/reading'
import { generateShareImage } from '../api/reading'

const router = useRouter()
const route = useRoute()
const readingId = route.params.readingId

const loading = ref(true)
const sharing = ref(false)
const detail = ref('')

const formattedDetail = computed(() => {
  if (!detail.value) return ''
  return detail.value
    .replace(/【([^】]+)】/g, '<h3 class="section-heading">$1</h3>')
    .replace(/\n/g, '<br>')
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
.detail-content {
  background: rgba(255,255,255,0.04); border-radius: var(--radius); padding: 20px;
  margin-bottom: 20px; line-height: 1.8;
}
.detail-text { font-size: var(--font-size-base); color: var(--color-text); }
:deep(.section-heading) {
  font-size: var(--font-size-lg); color: var(--color-accent);
  margin: 20px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--color-border);
}
:deep(.section-heading:first-child) { margin-top: 0; }
.top-bar { margin-bottom: 12px; }
.back-btn { background: none; border: none; color: var(--color-text-muted); font-size: var(--font-size-sm); }
.actions { display: flex; gap: 12px; }
</style>
