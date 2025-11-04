import apiClient from './api'

interface UserWithPersona {
  user_id: string
  name?: string
  email?: string
  role: string
  consent_status: boolean
  created_at?: string
  persona_id?: number
  persona_name?: string
  profile_updated_at?: string
}

interface UsersListResponse {
  items: UserWithPersona[]
  total: number
  skip: number
  limit: number
}

interface Account {
  id: string
  user_id: string
  account_id: string
  name: string
  type: string
  subtype: string
  holder_category: string
  balance_available?: number
  balance_current: number
  balance_limit?: number
  iso_currency_code: string
  mask?: string
  upload_id?: string
  created_at: string
  updated_at?: string
}

interface Transaction {
  id: string
  account_id: string
  user_id: string
  transaction_id: string
  date: string
  amount: number
  merchant_name?: string
  merchant_entity_id?: string
  payment_channel: string
  category_primary: string
  category_detailed?: string
  pending: boolean
  iso_currency_code: string
  upload_id?: string
  created_at: string
}

interface Liability {
  id: string
  account_id: string
  user_id: string
  apr_percentage?: number
  apr_type?: string
  minimum_payment_amount?: number
  last_payment_amount?: number
  last_payment_date?: string
  last_statement_balance?: number
  is_overdue?: boolean
  next_payment_due_date?: string
  interest_rate?: number
  upload_id?: string
  created_at: string
  updated_at?: string
}

interface AccountsListResponse {
  items: Account[]
  total: number
}

interface TransactionsListResponse {
  items: Transaction[]
  total: number
  skip: number
  limit: number
}

interface LiabilitiesListResponse {
  items: Liability[]
  total: number
}

interface BehavioralProfile {
  profile_id: string
  user_id: string
  persona_id: number
  persona_name: string
  signals_30d?: {
    income?: {
      payroll_deposits?: Array<{
        date: string
        amount: number
        merchant_name?: string
      }>
      payment_frequency?: {
        median_gap_days?: number
        average_gap_days?: number
        frequency_type?: string
        deposit_count?: number
      }
      payment_variability?: {
        mean_amount?: number
        min_amount?: number
        max_amount?: number
        coefficient_of_variation?: number
        variability_level?: string
      }
      cash_flow_buffer?: {
        cash_flow_buffer_months?: number
        current_balance?: number
        average_monthly_expenses?: number
      }
      variable_income_pattern?: {
        is_variable_income?: boolean
        confidence?: string
      }
    }
    subscriptions?: Record<string, any>
    savings?: Record<string, any>
    credit?: Record<string, any>
  }
  signals_180d?: {
    income?: {
      payroll_deposits?: Array<{
        date: string
        amount: number
        merchant_name?: string
      }>
      payment_frequency?: {
        median_gap_days?: number
        average_gap_days?: number
        frequency_type?: string
        deposit_count?: number
      }
      payment_variability?: {
        mean_amount?: number
        min_amount?: number
        max_amount?: number
        coefficient_of_variation?: number
        variability_level?: string
      }
      cash_flow_buffer?: {
        cash_flow_buffer_months?: number
        current_balance?: number
        average_monthly_expenses?: number
      }
      variable_income_pattern?: {
        is_variable_income?: boolean
        confidence?: string
      }
    }
    subscriptions?: Record<string, any>
    savings?: Record<string, any>
    credit?: Record<string, any>
  }
  signals_365d?: {
    income?: {
      payroll_deposits?: Array<{
        date: string
        amount: number
        merchant_name?: string
      }>
      payment_frequency?: {
        median_gap_days?: number
        average_gap_days?: number
        frequency_type?: string
        deposit_count?: number
      }
      payment_variability?: {
        mean_amount?: number
        min_amount?: number
        max_amount?: number
        coefficient_of_variation?: number
        variability_level?: string
      }
      cash_flow_buffer?: {
        cash_flow_buffer_months?: number
        current_balance?: number
        average_monthly_expenses?: number
      }
      variable_income_pattern?: {
        is_variable_income?: boolean
        confidence?: string
      }
    }
    subscriptions?: Record<string, any>
    savings?: Record<string, any>
    credit?: Record<string, any>
  }
  updated_at: string
}

export const adminService = {
  // Get all users with personas (admin only)
  async getAllUsers(skip: number = 0, limit: number = 100): Promise<UsersListResponse> {
    const response = await apiClient.get<UsersListResponse>('/api/v1/operator/admin/users', {
      params: { skip, limit },
    })
    return response.data
  },

  // Get user profile (admin/operator)
  async getUserProfile(userId: string) {
    const response = await apiClient.get(`/api/v1/operator/users/${userId}`)
    return response.data
  },

  // Get user accounts
  async getUserAccounts(userId: string): Promise<AccountsListResponse> {
    const response = await apiClient.get<AccountsListResponse>(`/api/v1/operator/users/${userId}/accounts`)
    return response.data
  },

  // Get user transactions (paginated)
  async getUserTransactions(
    userId: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<TransactionsListResponse> {
    const response = await apiClient.get<TransactionsListResponse>(
      `/api/v1/operator/users/${userId}/transactions`,
      {
        params: { skip, limit },
      }
    )
    return response.data
  },

  // Get user behavioral profile (includes income signals)
  async getUserBehavioralProfile(userId: string): Promise<BehavioralProfile> {
    const response = await apiClient.get<BehavioralProfile>(`/api/v1/users/${userId}/profile`)
    return response.data
  },

  // Get user liabilities
  async getUserLiabilities(userId: string): Promise<LiabilitiesListResponse> {
    const response = await apiClient.get<LiabilitiesListResponse>(
      `/api/v1/operator/users/${userId}/liabilities`
    )
    return response.data
  },

  // Get user recommendations
  async getUserRecommendations(
    userId: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<{
    items: Array<{
      recommendation_id: string
      user_id: string
      type: 'education' | 'partner_offer'
      title: string
      content: string
      rationale: string
      status: 'pending' | 'approved' | 'rejected'
      created_at: string
      approved_at?: string
    }>
    total: number
    skip: number
    limit: number
  }> {
    const response = await apiClient.get(
      `/api/v1/users/${userId}/recommendations`,
      {
        params: { skip, limit },
      }
    )
    return response.data
  },

  // Get user persona history
  async getUserPersonaHistory(userId: string): Promise<{
    items: Array<{
      history_id: string
      user_id: string
      persona_id: number
      persona_name: string
      assigned_at: string
      signals?: Record<string, any>
    }>
    total: number
    skip: number
    limit: number
  }> {
    const response = await apiClient.get(`/api/v1/users/${userId}/persona-history`)
    return response.data
  },
}

export type {
  UserWithPersona,
  UsersListResponse,
  Account,
  Transaction,
  Liability,
  AccountsListResponse,
  TransactionsListResponse,
  LiabilitiesListResponse,
  BehavioralProfile,
}
