<template>
  <div class="page-container">
    <div class="top-bar">
      <button class="back-btn" @click="router.push('/fortune')">&#8592; 返回</button>
      <span class="page-title-small">个人中心</span>
      <button class="logout-btn" @click="handleLogout">退出</button>
    </div>

    <div class="profile-card fade-in">
      <div class="avatar">{{ (userStore.nickname || '?')[0] }}</div>
      <div class="profile-name">{{ userStore.nickname || '神秘旅人' }}</div>
    </div>

    <h3 class="section-title">占卜历史</h3>

    <div class="loading-spinner" v-if="loading">加载中...</div>

    <div v-else-if="readings.length === 0" class="empty-state">
      <p>还没有占卜记录</p>
      <button class="btn-primary" @click="router.push('/fortune')">开始占卜</button>
    </div>

    <div v-else class="history-list fade-in">
      <div v-for="r in readings" :key="r.id" class="history-item" @click="goToReading(r)">
        <div class="history-cards">
          <span v-for="card in (r.cards_drawn || [])" :key="card.card_id" class="mini-card">{{ card.name_cn }}</span>
        </div>
        <div class="history-meta">
          <span class="history-question">{{ r.question_text || '综合占卜' }}</span>
          <span class="history-date">{{ formatDate(r.created_at) }}</span>
        </div>
        <span class="history-status" :class="r.status">{{ statusLabel(r.status) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useReadingStore } from '../stores/reading'
import { getHistory } from '../api/reading'

const router = useRouter()
const userStore = useUserStore()
const readingStore = useReadingStore()

const readings = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await getHistory()
    readings.value = data
  } catch {} finally {
    loading.value = false
  }
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

function statusLabel(s) {
  return { brief: '待解锁', paid: '已付费', completed: '已完成' }[s] || s
}

function goToReading(r) {
  if (r.status === 'completed') {
    router.push(`/detail/${r.id}`)
  } else if (r.status === 'paid') {
    router.push(`/detail/${r.id}`)
  } else {
    readingStore.currentReadingId = r.id
    readingStore.cardsDrawn = r.cards_drawn || []
    readingStore.briefReading = r.brief_reading || ''
    router.push(`/cards`)
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/auth')
}
</script>

<style scoped>
.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.back-btn, .logout-btn {
  background: none; border: none; color: var(--color-text-muted); font-size: var(--font-size-sm);
}
.logout-btn { color: var(--color-danger); }
.page-title-small { font-size: var(--font-size-lg); color: var(--color-text); font-weight: 600; }
.profile-card { text-align: center; padding: 20px; background: var(--color-bg-card); border-radius: var(--radius); border: 1px solid var(--color-border); margin-bottom: 24px; }
.avatar {
  width: 56px; height: 56px; border-radius: 50%; background: var(--color-primary);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 24px; color: white; margin-bottom: 8px;
}
.profile-name { font-size: var(--font-size-lg); color: var(--color-text); }
.section-title { font-size: var(--font-size-base); color: var(--color-text-muted); margin-bottom: 12px; }
.empty-state { text-align: center; padding: 40px 0; color: var(--color-text-muted); }
.history-list { display: flex; flex-direction: column; gap: 10px; }
.history-item {
  display: flex; align-items: center; gap: 10px; padding: 12px;
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); cursor: pointer; transition: all 0.2s;
}
.history-item:hover { border-color: var(--color-primary-light); }
.history-cards { display: flex; gap: 4px; }
.mini-card {
  font-size: 10px; padding: 2px 6px; background: rgba(246,211,101,0.1);
  border-radius: 4px; color: var(--color-accent);
}
.history-meta { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.history-question { font-size: var(--font-size-sm); color: var(--color-text); }
.history-date { font-size: 11px; color: var(--color-text-muted); }
.history-status { font-size: 11px; color: var(--color-text-muted); }
.history-status.completed { color: var(--color-success); }
.history-status.paid { color: var(--color-accent); }
</style>
