import apiClient from './api'

interface UserProfile {
  user_id: string
  email?: string
  phone_number?: string
  oauth_providers?: Record<string, string>
  role: string
  consent_status: boolean
  consent_version: string
  created_at: string
  updated_at?: string
}

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

interface Recommendation {
  recommendation_id: string
  user_id: string
  type: 'education' | 'partner_offer'
  title: string
  content: string
  rationale: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  approved_at?: string
  decision_trace?: Record<string, any>
}

interface Transaction {
  id: string
  user_id: string
  account_id: string
  date: string
  merchant_name?: string
  amount: number
  category_primary: string
  category_detailed?: string
  payment_channel?: string
  pending?: boolean
}

interface TransactionsListResponse {
  items: Transaction[]
  total: number
  skip: number
  limit: number
}

export interface DashboardData {
  profile: UserProfile
  behavioralProfile?: BehavioralProfile
  recommendations: Recommendation[]
  consentStatus: boolean
}

export interface SpendingCategory {
  category: string
  amount: number
  percentage: number
  transaction_count: number
  top_merchants?: Array<{ merchant: string; amount: number }>
  average_transaction: number
}

export interface SpendingSignals {
  window_days: number
  window_start: string
  window_end: string
  categories: SpendingCategory[]
  total_spending: number
  transaction_count: number
  top_category?: string
  top_category_amount?: number
}

export interface SpendingData {
  user_id: string
  generated_at: string
  signals_30d: SpendingSignals
  signals_180d: SpendingSignals
}

export const dashboardService = {
  // Get dashboard data
  async getDashboardData(): Promise<DashboardData> {
    // Fetch user profile
    const profileResponse = await apiClient.get<UserProfile>('/api/v1/users/me')
    const profile = profileResponse.data

    // Fetch behavioral profile (if available)
    // Note: This endpoint may not exist yet - will be added when behavioral profiling is implemented
    let behavioralProfile: BehavioralProfile | undefined
    try {
      const behavioralResponse = await apiClient.get<BehavioralProfile>(
        `/api/v1/users/${profile.user_id}/profile`
      )
      behavioralProfile = behavioralResponse.data
    } catch (error: any) {
      // Behavioral profile may not exist yet for new users or endpoint not implemented
      if (error.response?.status !== 404) {
        console.warn('Error fetching behavioral profile:', error.message)
      }
    }

    // Fetch recommendations (approved ones for dashboard)
    // Note: This endpoint may not exist yet - will be added when recommendations are implemented
    let recommendations: Recommendation[] = []
    try {
      const recommendationsResponse = await apiClient.get<{
        items: Recommendation[]
        total: number
      }>(`/api/v1/recommendations?status=approved&limit=10`)
      recommendations = recommendationsResponse.data.items || []
    } catch (error: any) {
      // Recommendations may not exist yet or endpoint not implemented
      // Suppress CORS and network errors silently - they're expected if backend isn't fully configured
      if (error.response?.status !== 404 && error.response?.status !== 0) {
        console.warn('Error fetching recommendations:', error.message)
      }
    }

    return {
      profile,
      behavioralProfile,
      recommendations,
      consentStatus: profile.consent_status,
    }
  },

  // Get user transactions (for regular users)
  async getUserTransactions(
    userId: string,
    skip: number = 0,
    limit: number = 50
  ): Promise<TransactionsListResponse> {
    // Try user endpoint first, fallback to operator endpoint if needed
    try {
      const response = await apiClient.get<TransactionsListResponse>(
        `/api/v1/users/${userId}/transactions`,
        {
          params: { skip, limit },
        }
      )
      return response.data
    } catch (error: any) {
      // Fallback to operator endpoint if user endpoint doesn't exist
      if (error.response?.status === 404) {
        const response = await apiClient.get<TransactionsListResponse>(
          `/api/v1/operator/users/${userId}/transactions`,
          {
            params: { skip, limit },
          }
        )
        return response.data
      }
      throw error
    }
  },

  // Get spending categories
  async getSpendingCategories(userId: string): Promise<SpendingData> {
    const response = await apiClient.get<SpendingData>(
      `/api/v1/users/${userId}/spending-categories`
    )
    return response.data
  },
}

