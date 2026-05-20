<template>
  <div class="page-container" style="justify-content: center; align-items: center;">
    <h1 class="page-title">分享你的解读</h1>
    <p class="page-subtitle">长按图片保存到手机相册</p>

    <div class="share-preview fade-in" v-if="reading">
      <div class="share-card">
        <div class="share-header">
          <div class="share-brand">✦ TAROT READING ✦</div>
          <div class="share-topic">{{ topicName }}</div>
        </div>
        <div class="share-cards">
          <div class="share-card-slot" v-for="card in reading.cards_drawn" :key="card.position">
            <div class="share-card-box">{{ card.name_cn }}</div>
            <span>{{ { past: '过去', present: '现在', future: '未来' }[card.position] }}</span>
          </div>
        </div>
        <div class="share-text">{{ reading.brief_reading?.slice(0, 150) }}...</div>
        <div class="share-footer">塔罗占卜 · 探索命运的低语</div>
      </div>
    </div>

    <div class="share-actions fade-in">
      <button class="btn-primary" @click="startNew">再来一次</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useReadingStore } from '../stores/reading'
import { getReading } from '../api/reading'

const router = useRouter()
const route = useRoute()
const readingStore = useReadingStore()
const readingId = route.params.readingId
const reading = ref(null)
const topicName = ref('')

const topicNames = { love: '桃花/爱情', career: '事业', destiny: '正缘', family: '家庭', general: '综合运势' }

onMounted(async () => {
  const { data } = await getReading(readingId)
  reading.value = data
  topicName.value = topicNames[data.topic] || data.topic
})

function startNew() {
  readingStore.reset()
  router.push('/topic')
}
</script>

<style scoped>
.share-preview { width: 100%; margin: 20px 0; }
.share-card {
  background: linear-gradient(160deg, #1a0533, #2d1b69, #4a1a8a);
  border-radius: var(--radius); padding: 24px 20px; text-align: center;
}
.share-header { margin-bottom: 16px; }
.share-brand { font-size: 12px; color: #b794d6; letter-spacing: 3px; }
.share-topic {
  font-size: var(--font-size-xl); margin-top: 8px;
  background: linear-gradient(135deg, #f6d365, #fda085);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.share-cards { display: flex; justify-content: center; gap: 16px; margin: 16px 0; }
.share-card-slot { text-align: center; }
.share-card-box {
  width: 70px; height: 100px; background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.2); border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; color: #f6d365; font-weight: bold; margin-bottom: 4px;
}
.share-card-slot span { font-size: 11px; color: #b794d6; }
.share-text { font-size: 13px; color: #e0d0f0; line-height: 1.6; text-align: left; margin: 16px 0; }
.share-footer { font-size: 12px; color: #7c4dba; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1); }
.share-actions { width: 100%; }
</style>
