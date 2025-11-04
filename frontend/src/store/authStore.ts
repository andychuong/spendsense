import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { User, AuthTokens } from '@/types'
import { storeTokens, clearStoredTokens } from '@/services/api'

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  setAuth: (user: User, tokens: AuthTokens) => void
  setUser: (user: User) => void
  logout: () => void
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
      logout: () => {
        clearStoredTokens()
        set({ user: null, tokens: null, isAuthenticated: false })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
)

