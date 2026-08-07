import axios from 'axios'

// Use Vite dev server proxy: prefix calls with /api so they are forwarded to backend
const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

export const getMetrics = () => api.get('/metrics')
export const postForecast = (payload) => api.post('/predict/forecast', payload)
export const postSegment = (payload) => api.post('/predict/segment', payload)
export const getExplain = (store_nbr) => api.get(`/explain/${store_nbr}`)
export const postABTest = (payload) => api.post('/ab-test', payload)
export const getDrift = () => api.get('/drift')

export default api
