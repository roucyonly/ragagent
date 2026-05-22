import api from './index'

export const MOCK = import.meta.env.VITE_MOCK === 'true'

export const createReading = (data) => api.post('/api/readings', { ...data, mock: MOCK })
export const getReading = (id) => api.get(`/api/readings/${id}`)
export const generateDetail = (id) => api.post(`/api/readings/${id}/detail${MOCK ? '?mock=true' : ''}`)
export const streamDetail = (id) => {
  const token = localStorage.getItem('token')
  const headers = token ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }
  const mockQuery = MOCK ? '?mock=true' : ''
  return fetch(`/api/readings/${id}/detail/stream${mockQuery}`, {
    method: 'POST',
    headers,
  })
}
export const generateShareImage = (id) => api.post(`/api/share/generate-image/${id}`)
export const getShareImage = (id) => api.get(`/api/share/image/${id}`)
export const getHistory = (limit = 20, offset = 0) => api.get(`/api/user/readings?limit=${limit}&offset=${offset}`)
export const followUp = (id, question) => api.post(`/api/readings/${id}/follow-up`, { question })
