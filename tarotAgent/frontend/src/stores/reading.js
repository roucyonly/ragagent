import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useReadingStore = defineStore('reading', () => {
  const topic = ref('')
  const questionText = ref('')
  const selectedCards = ref([])
  const currentReadingId = ref('')
  const briefReading = ref('')
  const detailedReading = ref('')
  const status = ref('')

  function setTopic(t) {
    topic.value = t
    questionText.value = ''
  }

  function setCards(cards) {
    selectedCards.value = cards
  }

  function setReading(data) {
    currentReadingId.value = data.id
    briefReading.value = data.brief_reading || ''
    status.value = data.status
  }

  function reset() {
    topic.value = ''
    questionText.value = ''
    selectedCards.value = []
    currentReadingId.value = ''
    briefReading.value = ''
    detailedReading.value = ''
    status.value = ''
  }

  return { topic, questionText, selectedCards, currentReadingId, briefReading, detailedReading, status, setTopic, setCards, setReading, reset }
})
