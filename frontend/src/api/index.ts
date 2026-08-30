import axios from 'axios'

const getApiBaseUrl = () => {
  if (typeof window !== 'undefined' && window.location?.hostname && window.location.protocol !== 'file:') {
    return `http://${window.location.hostname}:8000`
  }
  return 'http://127.0.0.1:8000'
}

export const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})
