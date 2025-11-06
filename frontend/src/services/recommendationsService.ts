import apiClient from './api'

export interface RecommendationExplanation {
  data_citations?: string[]
  persona?: string
  similar_scenarios?: string[]
  context_retrieved?: number
  similar_users?: number
  generation_method?: string
  confidence?: number
}

export interface Recommendation {
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
  explanation?: RecommendationExplanation
  // Partner offer specific fields
  eligibility_status?: 'eligible' | 'ineligible' | 'pending'
  eligibility_reason?: string
  partner_name?: string
  partner_logo_url?: string
  offer_details?: Record<string, any>
}

export interface RecommendationsResponse {
  items: Recommendation[]
  total: number
  skip: number
  limit: number
}

export interface RecommendationsFilters {
  status?: 'pending' | 'approved' | 'rejected'
  type?: 'education' | 'partner_offer'
  sort_by?: 'date' | 'relevance' | 'type'
  sort_order?: 'asc' | 'desc'
  skip?: number
  limit?: number
}

export const recommendationsService = {
  // Get recommendations for current user
  async getRecommendations(filters?: RecommendationsFilters): Promise<RecommendationsResponse> {
    const params = new URLSearchParams()

    if (filters?.status) {
      params.append('status', filters.status)
    }
    if (filters?.type) {
      params.append('type', filters.type)
    }
    if (filters?.sort_by) {
      params.append('sort_by', filters.sort_by)
    }
    if (filters?.sort_order) {
      params.append('sort_order', filters.sort_order)
    }
    if (filters?.skip !== undefined) {
      params.append('skip', filters.skip.toString())
    }
    if (filters?.limit !== undefined) {
      params.append('limit', filters.limit.toString())
    }

    try {
      const response = await apiClient.get<RecommendationsResponse>(
        `/api/v1/recommendations?${params.toString()}`
      )
      return response.data
    } catch (error: any) {
      // Gracefully handle missing endpoint (404) - return empty list
      if (error.response?.status === 404) {
        return {
          items: [],
          total: 0,
          skip: filters?.skip || 0,
          limit: filters?.limit || 10,
        }
      }
      throw error
    }
  },

  // Get single recommendation detail
  async getRecommendationDetail(recommendationId: string): Promise<Recommendation> {
    try {
      const response = await apiClient.get<Recommendation>(
        `/api/v1/recommendations/${recommendationId}`
      )
      return response.data
    } catch (error: any) {
      // Gracefully handle missing endpoint (404)
      if (error.response?.status === 404) {
        throw new Error('Recommendation not found')
      }
      throw error
    }
  },

  // Submit feedback for a recommendation
  async submitFeedback(
    recommendationId: string,
    feedback: {
      rating?: number
      helpful?: boolean
      comment?: string
    }
  ): Promise<void> {
    // Note: This endpoint may not exist yet - will be added when backend is implemented
    try {
      await apiClient.post(`/api/v1/recommendations/${recommendationId}/feedback`, feedback)
    } catch (error: any) {
      // Gracefully handle missing endpoint (404)
      if (error.response?.status === 404) {
        console.warn('Feedback endpoint not yet implemented')
      } else {
        throw error
      }
    }
  },

  // Dismiss a recommendation
  async dismissRecommendation(recommendationId: string): Promise<void> {
    // Note: This endpoint may not exist yet - will be added when backend is implemented
    try {
      await apiClient.post(`/api/v1/recommendations/${recommendationId}/dismiss`)
    } catch (error: any) {
      // Gracefully handle missing endpoint (404)
      if (error.response?.status === 404) {
        console.warn('Dismiss endpoint not yet implemented')
      } else {
        throw error
      }
    }
  },

  // Save/bookmark a recommendation
  async saveRecommendation(recommendationId: string): Promise<void> {
    // Note: This endpoint may not exist yet - will be added when backend is implemented
    try {
      await apiClient.post(`/api/v1/recommendations/${recommendationId}/save`)
    } catch (error: any) {
      // Gracefully handle missing endpoint (404)
      if (error.response?.status === 404) {
        console.warn('Save endpoint not yet implemented')
      } else {
        throw error
      }
    }
  },
}

