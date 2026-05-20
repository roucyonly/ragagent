import api from './index'

const MOCK = import.meta.env.VITE_MOCK === 'true'

export const createReading = (data) => api.post('/api/readings', { ...data, mock: MOCK })
export const getReading = (id) => api.get(`/api/readings/${id}`)
export const generateDetail = (id) => api.post(`/api/readings/${id}/detail${MOCK ? '?mock=true' : ''}`)
export const generateShareImage = (id) => api.post(`/api/share/generate-image/${id}`)
export const getShareImage = (id) => api.get(`/api/share/image/${id}`)
export const getHistory = (limit = 20, offset = 0) => api.get(`/api/user/readings?limit=${limit}&offset=${offset}`)
