import api from './index'

export const createOrder = (data) => api.post('/api/payments/create-order', data)
export const getOrderStatus = (outTradeNo) => api.get(`/api/payments/order/${outTradeNo}/status`)
export const mockPay = (outTradeNo) => api.post(`/api/payments/mock-pay/${outTradeNo}`)
