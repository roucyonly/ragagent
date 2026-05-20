<template>
  <div class="page-container" style="justify-content: center; align-items: center;">
    <div class="logo-section">
      <div class="logo-icon">&#10022;</div>
      <h1 class="page-title">塔罗占卜</h1>
      <p class="page-subtitle">探索命运的低语</p>
    </div>

    <div class="tab-row">
      <button :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
      <button :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
    </div>

    <div class="form-section fade-in">
      <div class="form-group">
        <label>昵称</label>
        <input v-model="nickname" placeholder="输入你的昵称" @keyup.enter="submit" />
      </div>
      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" :placeholder="mode === 'register' ? '设置密码' : '输入密码'" @keyup.enter="submit" />
      </div>

      <button class="btn-primary" @click="submit" :disabled="loading || !nickname || !password">
        {{ loading ? '请稍候...' : (mode === 'login' ? '登录' : '注册') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { login, register } from '../api/auth'

const router = useRouter()
const userStore = useUserStore()

const mode = ref('login')
const nickname = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  try {
    const fn = mode.value === 'login' ? login : register
    const { data } = await fn({ nickname: nickname.value, password: password.value })
    userStore.setUser(data)
    router.push('/fortune')
  } catch (e) {
    const msg = e.response?.data?.detail || '操作失败，请重试'
    alert(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.logo-section { text-align: center; margin-bottom: 24px; }
.logo-icon { font-size: 48px; color: var(--color-accent); margin-bottom: 16px; }
.tab-row { display: flex; gap: 0; margin-bottom: 20px; width: 100%; }
.tab-row button {
  flex: 1; padding: 12px; background: var(--color-bg-card); border: 1px solid var(--color-border);
  color: var(--color-text-muted); font-size: var(--font-size-base); transition: all 0.3s;
}
.tab-row button:first-child { border-radius: var(--radius-sm) 0 0 var(--radius-sm); }
.tab-row button:last-child { border-radius: 0 var(--radius-sm) var(--radius-sm) 0; }
.tab-row button.active { background: var(--color-primary); border-color: var(--color-primary); color: white; }
.form-section { width: 100%; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: 6px; }
.form-group input {
  width: 100%; padding: 12px; background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); color: var(--color-text); font-size: var(--font-size-base);
}
</style>
