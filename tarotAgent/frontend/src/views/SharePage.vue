<template>
  <div class="page-container">
    <div class="top-bar">
      <button class="back-btn" @click="router.push('/fortune')">&#8592; 返回</button>
      <span class="page-title-small">分享解读</span>
      <span></span>
    </div>

    <div class="loading-spinner" v-if="loading">{{ loadingText }}</div>

    <template v-else-if="imageUrl">
      <div class="share-preview fade-in">
        <img :src="imageBlobUrl" alt="塔罗解读" class="share-img" />
      </div>
      <div class="share-actions fade-in">
        <button class="btn-primary" @click="downloadImage">保存图片</button>
        <button class="btn-back" @click="startNew">再来一次</button>
      </div>
    </template>

    <div class="error-state" v-else>
      <p>图片生成失败</p>
      <button class="btn-primary" @click="generate">重试</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useReadingStore } from '../stores/reading'
import { generateShareImage, getShareImage } from '../api/reading'
import api from '../api/index'

const router = useRouter()
const route = useRoute()
const readingStore = useReadingStore()
const readingId = route.params.readingId

const loading = ref(true)
const loadingText = ref('正在生成分享图片...')
const imageUrl = ref('')
const imageBlobUrl = ref('')

onMounted(async () => {
  await generate()
})

async function loadBlob() {
  const resp = await api.get(`/api/share/image/${readingId}`, { responseType: 'blob' })
  if (imageBlobUrl.value) URL.revokeObjectURL(imageBlobUrl.value)
  imageBlobUrl.value = URL.createObjectURL(resp.data)
}

async function generate() {
  loading.value = true
  loadingText.value = '正在生成分享图片...'
  try {
    const { data } = await getShareImage(readingId)
    if (data.image_url) {
      imageUrl.value = data.image_url
      await loadBlob()
      loading.value = false
      return
    }
  } catch {
    // Not generated yet, generate it
  }

  try {
    loadingText.value = '正在生成分享图片，请稍候...'
    const { data } = await generateShareImage(readingId)
    imageUrl.value = data.image_url
    await loadBlob()
  } catch {
    imageUrl.value = ''
  } finally {
    loading.value = false
  }
}

function downloadImage() {
  if (!imageBlobUrl.value) return
  const link = document.createElement('a')
  link.href = imageBlobUrl.value
  link.download = `tarot_${readingId}.jpg`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function startNew() {
  readingStore.reset()
  router.push('/fortune')
}
</script>

<style scoped>
.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.back-btn { background: none; border: none; color: var(--color-text-muted); font-size: var(--font-size-sm); }
.page-title-small { font-size: var(--font-size-lg); color: var(--color-text); font-weight: 600; }
.share-preview { width: 100%; margin-bottom: 20px; }
.share-img {
  width: 100%; border-radius: var(--radius);
  border: 1px solid var(--color-border);
}
.share-actions { display: flex; flex-direction: column; gap: 10px; }
.btn-back {
  background: none; border: 1px solid var(--color-border);
  padding: 12px; border-radius: var(--radius); color: var(--color-text-muted);
  font-size: var(--font-size-base);
}
.error-state { text-align: center; padding: 40px 0; color: var(--color-text-muted); }
</style>
