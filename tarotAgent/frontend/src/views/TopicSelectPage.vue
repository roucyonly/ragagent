<template>
  <div class="page-container">
    <h1 class="page-title">你想了解什么？</h1>
    <p class="page-subtitle">选择一个你最关心的话题</p>

    <div class="topic-grid fade-in">
      <div v-for="t in topics" :key="t.key" class="topic-card" :class="{ selected: readingStore.topic === t.key }" @click="selectTopic(t.key)">
        <span class="topic-icon">{{ t.icon }}</span>
        <span class="topic-name">{{ t.name }}</span>
        <span class="topic-desc">{{ t.desc }}</span>
      </div>
    </div>

    <div class="question-section" v-if="readingStore.topic">
      <div class="form-group">
        <label>你有什么具体的问题吗？（选填）</label>
        <input v-model="questionText" placeholder="输入你的问题..." />
      </div>
      <button class="btn-primary" @click="next">选牌去</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReadingStore } from '../stores/reading'
import { getTopics } from '../api/reading'

const router = useRouter()
const readingStore = useReadingStore()

const topics = ref([])
const questionText = ref('')

onMounted(async () => {
  const { data } = await getTopics()
  topics.value = data
})

function selectTopic(key) {
  readingStore.setTopic(key)
}

function next() {
  readingStore.questionText = questionText.value
  router.push('/cards')
}
</script>

<style scoped>
.topic-grid { display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }
.topic-card {
  display: flex; align-items: center; gap: 12px; padding: 16px;
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius); cursor: pointer; transition: all 0.3s;
}
.topic-card.selected { border-color: var(--color-accent); background: rgba(246, 211, 101, 0.1); }
.topic-icon { font-size: 24px; }
.topic-name { font-size: var(--font-size-lg); font-weight: 600; min-width: 72px; }
.topic-desc { font-size: var(--font-size-sm); color: var(--color-text-muted); flex: 1; }
.question-section { margin-top: 8px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: 8px; }
.form-group input {
  width: 100%; padding: 12px; background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); color: var(--color-text); font-size: var(--font-size-base);
}
</style>
