<template>
  <div class="page-container">
    <h1 class="page-title">选择你的牌</h1>
    <p class="page-subtitle">从 78 张牌中选择 3 张（过去 · 现在 · 未来）</p>

    <div class="selected-bar" v-if="selected.length > 0">
      <div class="selected-slot" v-for="(s, i) in 3" :key="i">
        <div class="slot-box" :class="{ filled: selected[i] }">
          {{ selected[i] ? selected[i].name_cn : '?' }}
        </div>
        <span class="slot-label">{{ ['过去', '现在', '未来'][i] }}</span>
      </div>
    </div>

    <div class="card-grid fade-in" v-if="cards.length">
      <div v-for="card in cards" :key="card.card_id"
        class="card-item" :class="{ picked: isPicked(card.card_id) }"
        @click="toggleCard(card)">
        <div class="card-face">
          <span class="card-num">{{ card.number }}</span>
          <span class="card-name">{{ card.name_cn }}</span>
          <span class="card-suit">{{ card.suit || card.arcana }}</span>
        </div>
      </div>
    </div>

    <div class="loading-spinner" v-else>加载牌面中...</div>

    <div class="actions">
      <button class="btn-random" @click="randomPick">随机抽牌</button>
      <button class="btn-primary" @click="submit" :disabled="selected.length !== 3 || submitting">
        {{ submitting ? '解读中...' : '开始解读' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReadingStore } from '../stores/reading'
import { getCards, createReading } from '../api/reading'

const router = useRouter()
const readingStore = useReadingStore()

const cards = ref([])
const selected = ref([])
const submitting = ref(false)

onMounted(async () => {
  const { data } = await getCards()
  cards.value = data
})

function isPicked(id) {
  return selected.value.some(c => c.card_id === id)
}

function toggleCard(card) {
  const idx = selected.value.findIndex(c => c.card_id === card.card_id)
  if (idx >= 0) {
    selected.value.splice(idx, 1)
  } else if (selected.value.length < 3) {
    selected.value.push(card)
  }
}

function randomPick() {
  const shuffled = [...cards.value].sort(() => Math.random() - 0.5)
  selected.value = shuffled.slice(0, 3)
}

async function submit() {
  submitting.value = true
  try {
    const positions = ['past', 'present', 'future']
    const payload = {
      topic: readingStore.topic,
      question_text: readingStore.questionText || null,
      cards: selected.value.map((c, i) => ({
        card_id: c.card_id,
        name_en: c.name_en,
        name_cn: c.name_cn,
        position: positions[i],
        is_reversed: Math.random() > 0.7,
      })),
    }
    const { data } = await createReading(payload)
    readingStore.setReading(data)
    router.push(`/brief/${data.id}`)
  } catch (e) {
    alert('解读失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.selected-bar { display: flex; justify-content: center; gap: 16px; margin-bottom: 20px; }
.selected-slot { text-align: center; }
.slot-box {
  width: 70px; height: 100px; background: var(--color-bg-card); border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center;
  font-size: var(--font-size-lg); font-weight: bold; color: var(--color-text-muted); transition: all 0.3s;
}
.slot-box.filled { border-style: solid; border-color: var(--color-accent); color: var(--color-accent); background: rgba(246,211,101,0.08); }
.slot-label { font-size: var(--font-size-sm); color: var(--color-text-muted); display: block; margin-top: 4px; }
.card-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
  max-height: 360px; overflow-y: auto; padding: 4px;
}
.card-item { cursor: pointer; transition: all 0.2s; }
.card-face {
  aspect-ratio: 2/3; background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 4px; padding: 4px; transition: all 0.2s;
}
.card-item.picked .card-face { border-color: var(--color-accent); background: rgba(246,211,101,0.12); }
.card-item:hover .card-face { border-color: var(--color-primary-light); }
.card-num { font-size: 10px; color: var(--color-text-muted); }
.card-name { font-size: 12px; color: var(--color-text); font-weight: 600; text-align: center; }
.card-suit { font-size: 10px; color: var(--color-primary-light); }
.actions { display: flex; gap: 12px; margin-top: 20px; }
.btn-random {
  flex: 1; padding: 14px; background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius); color: var(--color-text); transition: all 0.3s;
}
.btn-primary { flex: 2; }
</style>
