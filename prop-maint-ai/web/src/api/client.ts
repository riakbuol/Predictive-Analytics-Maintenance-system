import axios from 'axios'

const API_BASE = (import.meta.env.VITE_API_BASE as string) || `${window.location.protocol}//${window.location.hostname}:8000`

export const api = axios.create({ baseURL: API_BASE })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})