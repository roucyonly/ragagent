import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userId = ref(localStorage.getItem('userId') || '')
  const nickname = ref(localStorage.getItem('nickname') || '')

  function setUser(data) {
    token.value = data.access_token
    userId.value = data.user.id
    nickname.value = data.user.nickname || ''
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('userId', data.user.id)
    localStorage.setItem('nickname', data.user.nickname || '')
  }

  function logout() {
    token.value = ''
    userId.value = ''
    nickname.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('nickname')
  }

  const isLoggedIn = () => !!token.value

  return { token, userId, nickname, setUser, logout, isLoggedIn }
})
