import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userId = ref('')
  const name = ref('')
  const gender = ref('')
  const birthDate = ref('')

  function setUser(data) {
    token.value = data.access_token
    userId.value = data.user.id
    name.value = data.user.name || ''
    gender.value = data.user.gender || ''
    birthDate.value = data.user.birth_date || ''
    localStorage.setItem('token', data.access_token)
  }

  function updateProfile(data) {
    if (data.name) name.value = data.name
    if (data.gender) gender.value = data.gender
    if (data.birth_date) birthDate.value = data.birth_date
  }

  return { token, userId, name, gender, birthDate, setUser, updateProfile }
})
