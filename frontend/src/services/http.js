import axios from 'axios'
import { getAccessToken, getRefreshToken, setAccessToken, clearTokens } from './auth'

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_BASE}/api/v1`,
})

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let isRefreshing = false
let pending = []

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config
    if (error.response && error.response.status === 401 && !original._retry) {
      original._retry = true
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pending.push({ resolve, reject })
        }).then((token) => {
          original.headers.Authorization = `Bearer ${token}`
          return api(original)
        })
      }
      isRefreshing = true
      try {
        const rt = getRefreshToken()
        if (!rt) throw new Error('No refresh token')
        const resp = await axios.post(`${import.meta.env.VITE_API_BASE}/api/v1/auth/refresh`, { refresh_token: rt })
        const newAccess = resp.data.access_token
        setAccessToken(newAccess)
        pending.forEach((p) => p.resolve(newAccess))
        pending = []
        original.headers.Authorization = `Bearer ${newAccess}`
        return api(original)
      } catch (e) {
        pending.forEach((p) => p.reject(e))
        pending = []
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(e)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default api
