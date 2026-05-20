import api from './index'

export const guestLogin = (profile) => api.post('/api/auth/guest', profile)
export const refreshToken = () => api.post('/api/auth/refresh')
