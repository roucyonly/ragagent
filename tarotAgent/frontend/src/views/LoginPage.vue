<template>
  <div class="page-container" style="justify-content: center; align-items: center;">
    <div class="logo-section">
      <div class="logo-icon">&#10022;</div>
      <h1 class="page-title">塔罗占卜</h1>
      <p class="page-subtitle">探索命运的低语，聆听星辰的指引</p>
    </div>

    <div class="form-section fade-in">
      <div class="form-group">
        <label>你的名字</label>
        <input v-model="name" placeholder="请输入你的名字" />
      </div>
      <div class="form-group">
        <label>性别</label>
        <div class="gender-select">
          <button :class="{ active: gender === 'male' }" @click="gender = 'male'">男</button>
          <button :class="{ active: gender === 'female' }" @click="gender = 'female'">女</button>
        </div>
      </div>
      <div class="form-group">
        <label>出生日期</label>
        <input v-model="birthDate" type="date" />
      </div>

      <button class="btn-primary" @click="handleLogin" :disabled="loading || !name">
        {{ loading ? '正在连接...' : '开始占卜' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { guestLogin } from '../api/auth'

const router = useRouter()
const userStore = useUserStore()

const name = ref('')
const gender = ref('')
const birthDate = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    const { data } = await guestLogin({
      name: name.value,
      gender: gender.value || null,
      birth_date: birthDate.value || null,
    })
    userStore.setUser(data)
    router.push('/topic')
  } catch (e) {
    alert('登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.logo-section { text-align: center; margin-bottom: 40px; }
.logo-icon { font-size: 48px; color: var(--color-accent); margin-bottom: 16px; }
.form-section { width: 100%; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: 8px; }
.form-group input {
  width: 100%; padding: 12px; background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); color: var(--color-text); font-size: var(--font-size-base);
}
.gender-select { display: flex; gap: 12px; }
.gender-select button {
  flex: 1; padding: 12px; background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); color: var(--color-text-muted); transition: all 0.3s;
}
.gender-select button.active {
  background: var(--color-primary); border-color: var(--color-primary-light); color: white;
}
</style>
