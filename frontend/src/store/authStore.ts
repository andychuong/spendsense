import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { User, AuthTokens } from '@/types'
import { storeTokens, clearStoredTokens } from '@/services/api'
import { authService } from '@/services/authService'

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  setAuth: (user: User, tokens: AuthTokens) => void
  setUser: (user: User) => void
  logout: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      setAuth: (user: User, tokens: AuthTokens) => {
        storeTokens(tokens)
        set({ user, tokens, isAuthenticated: true })
      },
      setUser: (user: User) => {
        set({ user })
      },
      logout: async () => {
        try {
          // Call backend to revoke refresh token
          await authService.logout()
        } catch (error) {
          // Even if backend logout fails, clear local tokens
          console.error('Logout error:', error)
        } finally {
          // Always clear local tokens and state
          clearStoredTokens()
          set({ user: null, tokens: null, isAuthenticated: false })
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
)

