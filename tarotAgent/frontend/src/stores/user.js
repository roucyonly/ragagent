import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userId = ref('')
  const nickname = ref('')

  function setUser(data) {
    token.value = data.access_token
    userId.value = data.user.id
    nickname.value = data.user.nickname || ''
    localStorage.setItem('token', data.access_token)
  }

  function logout() {
    token.value = ''
    userId.value = ''
    nickname.value = ''
    localStorage.removeItem('token')
  }

  const isLoggedIn = () => !!token.value

  return { token, userId, nickname, setUser, logout, isLoggedIn }
})
