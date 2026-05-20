import api from './index'

export const getCards = () => api.get('/api/tarot/cards')
export const getTopics = () => api.get('/api/tarot/topics')
export const createReading = (data) => api.post('/api/readings', data)
export const getReading = (id) => api.get(`/api/readings/${id}`)
export const generateDetail = (id) => api.post(`/api/readings/${id}/detail`)
export const generateShareImage = (id) => api.post(`/api/share/generate-image/${id}`)
