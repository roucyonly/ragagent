import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useReadingStore = defineStore('reading', () => {
  const question = ref('')
  const currentReadingId = ref('')
  const briefReading = ref('')
  const detailedReading = ref('')
  const cardsDrawn = ref([])
  const status = ref('')
  const readingPromise = ref(null)
  const readingResolved = ref(false)
  const readingError = ref(false)

  function reset() {
    question.value = ''
    currentReadingId.value = ''
    briefReading.value = ''
    detailedReading.value = ''
    cardsDrawn.value = []
    status.value = ''
    readingPromise.value = null
    readingResolved.value = false
    readingError.value = false
  }

  return {
    question, currentReadingId, briefReading, detailedReading,
    cardsDrawn, status, readingPromise, readingResolved, readingError,
    reset,
  }
})
