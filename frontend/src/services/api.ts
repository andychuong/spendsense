import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import type { AuthTokens } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token to requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokens = getStoredTokens()
    if (tokens?.access_token) {
      config.headers.Authorization = `Bearer ${tokens.access_token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle token refresh and errors
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Handle 401 Unauthorized - Try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const tokens = getStoredTokens()
        if (tokens?.refresh_token) {
          const response = await axios.post<AuthTokens>(
            `${API_BASE_URL}/api/v1/auth/refresh`,
            {
              refresh_token: tokens.refresh_token,
            }
          )

          const newTokens = response.data
          storeTokens(newTokens)
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`
          }

          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed - clear tokens and redirect to login
        clearStoredTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Token storage helpers
function getStoredTokens(): AuthTokens | null {
  try {
    const tokens = localStorage.getItem('auth_tokens')
    return tokens ? JSON.parse(tokens) : null
  } catch {
    return null
  }
}

function storeTokens(tokens: AuthTokens): void {
  localStorage.setItem('auth_tokens', JSON.stringify(tokens))
}

function clearStoredTokens(): void {
  localStorage.removeItem('auth_tokens')
}

// Export token helpers for use in auth store
export { storeTokens, getStoredTokens, clearStoredTokens }

export default apiClient

