import apiClient from './api'

interface BehavioralProfile {
  profile_id: string
  user_id: string
  persona_id: number
  persona_name: string
  signals_30d?: {
    subscriptions?: {
      recurring_merchants?: number
      monthly_recurring_spend?: number
      subscription_share?: number
    }
    savings?: {
      net_inflow?: number
      growth_rate?: number
      emergency_fund_coverage?: number
    }
    credit?: {
      utilization?: number
      high_utilization_cards?: number
      interest_charges?: number
      overdue_accounts?: number
    }
    income?: {
      payment_frequency?: number
      cash_flow_buffer?: number
      variable_income?: boolean
    }
  }
  signals_180d?: {
    subscriptions?: {
      recurring_merchants?: number
      monthly_recurring_spend?: number
      subscription_share?: number
    }
    savings?: {
      net_inflow?: number
      growth_rate?: number
      emergency_fund_coverage?: number
    }
    credit?: {
      utilization?: number
      high_utilization_cards?: number
      interest_charges?: number
      overdue_accounts?: number
    }
    income?: {
      payment_frequency?: number
      cash_flow_buffer?: number
      variable_income?: boolean
    }
  }
  updated_at: string
}

interface PersonaHistoryEntry {
  history_id: string
  user_id: string
  persona_id: number
  persona_name: string
  assigned_at: string
  signals?: Record<string, any>
}

export interface ProfileData {
  behavioralProfile?: BehavioralProfile
  personaHistory: PersonaHistoryEntry[]
}

export const profileService = {
  // Get user profile data
  async getProfile(userId?: string): Promise<ProfileData> {
    // If no userId provided, use 'me' to get current user
    const endpoint = userId ? `/api/v1/users/${userId}/profile` : '/api/v1/users/me/profile'
    
    let behavioralProfile: BehavioralProfile | undefined
    try {
      const profileResponse = await apiClient.get<BehavioralProfile>(endpoint)
      behavioralProfile = profileResponse.data
    } catch (error: any) {
      // Profile may not exist yet for new users
      if (error.response?.status !== 404) {
        console.warn('Error fetching behavioral profile:', error.message)
      }
    }

    // Fetch persona history
    // Note: This endpoint may not exist yet - will be added when persona history API is implemented
    let personaHistory: PersonaHistoryEntry[] = []
    try {
      const historyEndpoint = userId 
        ? `/api/v1/users/${userId}/persona-history`
        : '/api/v1/users/me/persona-history'
      const historyResponse = await apiClient.get<{
        items: PersonaHistoryEntry[]
        total: number
      }>(historyEndpoint)
      personaHistory = historyResponse.data.items || []
    } catch (error: any) {
      // Persona history may not exist yet or endpoint not implemented
      if (error.response?.status !== 404) {
        console.warn('Error fetching persona history:', error.message)
      }
    }

    return {
      behavioralProfile,
      personaHistory,
    }
  },

  // Export profile data (placeholder - will be implemented when backend endpoint is ready)
  async exportProfile(_format: 'pdf' | 'csv'): Promise<Blob> {
    // This will be implemented when the export endpoint is ready
    throw new Error('Export functionality not yet implemented')
  },
}

