// API Response Types
export interface ApiError {
  detail: string | { [key: string]: string[] }
}

export interface ApiResponse<T> {
  data?: T
  error?: ApiError
}

// Auth Types
export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface User {
  id: string
  email?: string
  phone?: string
  role: string
  created_at: string
  updated_at: string
}

// Store Types
export interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
}

