<template>
  <div class="page-container">
    <h1 class="page-title">牌面解读</h1>
    <p class="page-subtitle">你的三张牌揭示了一些重要的信息...</p>

    <div class="cards-display fade-in">
      <div class="card-reveal" v-for="(card, i) in reading?.cards_drawn" :key="i">
        <div class="card-box card-flip" :style="{ animationDelay: i * 0.3 + 's' }">
          <span class="card-name">{{ card.name_cn }}</span>
          <span class="card-pos">{{ { past: '过去', present: '现在', future: '未来' }[card.position] }}</span>
          <span class="card-dir" v-if="card.is_reversed">逆位</span>
        </div>
      </div>
    </div>

    <div class="reading-content fade-in" v-if="reading?.brief_reading">
      <div class="section-label">✦ 简要解读 ✦</div>
      <p class="reading-text">{{ reading.brief_reading }}</p>
    </div>
    <div class="loading-spinner" v-else>正在为你解读牌面...</div>

    <div class="teaser fade-in" v-if="reading?.brief_reading">
      <p>想要了解更深入的解读？解锁完整占卜报告，获得逐牌详解、牌间关联分析和专属建议。</p>
      <button class="btn-primary" @click="router.push(`/payment/${readingId}`)">解锁完整解读</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getReading } from '../api/reading'

const router = useRouter()
const route = useRoute()
const readingId = route.params.readingId
const reading = ref(null)

onMounted(async () => {
  const { data } = await getReading(readingId)
  reading.value = data
})
</script>

<style scoped>
.cards-display { display: flex; justify-content: center; gap: 16px; margin: 20px 0; }
.card-reveal { text-align: center; }
.card-box {
  width: 80px; height: 120px; background: linear-gradient(135deg, #3d2080, #5b2d99);
  border: 1px solid var(--color-accent); border-radius: var(--radius-sm);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  margin-bottom: 6px;
}
.card-name { font-size: 14px; color: var(--color-accent); font-weight: bold; }
.card-pos { font-size: 11px; color: var(--color-text-muted); }
.card-dir { font-size: 10px; color: var(--color-accent-pink); }
.reading-content {
  background: rgba(255,255,255,0.04); border-radius: var(--radius); padding: 20px; margin-bottom: 20px;
}
.section-label { font-size: var(--font-size-sm); color: var(--color-primary-light); margin-bottom: 12px; letter-spacing: 2px; }
.reading-text { font-size: var(--font-size-base); line-height: 1.8; color: var(--color-text); }
.teaser {
  text-align: center; padding: 20px; background: rgba(246,211,101,0.06);
  border: 1px solid rgba(246,211,101,0.2); border-radius: var(--radius);
}
.teaser p { font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: 16px; line-height: 1.6; }
</style>
