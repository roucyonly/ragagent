import api from './index'

export const register = (data) => api.post('/api/auth/register', data)
export const login = (data) => api.post('/api/auth/login', data)
export const refreshToken = () => api.post('/api/auth/refresh')
