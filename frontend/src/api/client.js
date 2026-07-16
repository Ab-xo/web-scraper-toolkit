import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

// on every error, extract the message from FastAPI's response
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail ?? err.message ?? 'Unknown error'
    const enhanced = new Error(detail)
    enhanced.status = err.response?.status ?? 0
    return Promise.reject(enhanced)
  }
)

export const scrapeUrl = (url, usePlaywright = false) =>
  api.post('/scrape', { url, use_playwright: usePlaywright })

export const queryContent = (html, intent, baseUrl = null) =>
  api.post('/query', { html, intent, base_url: baseUrl })

export const checkHealth = () =>
  api.get('/health')

export default api