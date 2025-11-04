import apiClient from './api'

export interface ReviewQueueItem {
  recommendation_id: string
  user_id: string
  user_name?: string
  user_email?: string
  type: 'education' | 'partner_offer'
  status: 'pending' | 'approved' | 'rejected'
  title: string
  created_at: string
  persona_id?: number
  persona_name?: string
}

export interface ReviewQueueResponse {
  items: ReviewQueueItem[]
  total: number
  skip: number
  limit: number
}

export interface ReviewQueueFilters {
  status?: 'pending' | 'approved' | 'rejected' | 'all'
  user_id?: string
  type?: 'education' | 'partner_offer' | 'all'
  persona_id?: number
  skip?: number
  limit?: number
  sort_by?: 'priority' | 'date' | 'user'
  sort_order?: 'asc' | 'desc'
  search?: string
  date_from?: string
  date_to?: string
}

export interface RecommendationReviewDetail {
  recommendation_id: string
  user_id: string
  user_name?: string
  user_email?: string
  type: 'education' | 'partner_offer'
  status: 'pending' | 'approved' | 'rejected'
  title: string
  content: string
  rationale: string
  created_at: string
  approved_at?: string
  approved_by?: string
  rejected_at?: string
  rejected_by?: string
  rejection_reason?: string
  persona_id?: number
  persona_name?: string
  decision_trace?: DecisionTrace
}

export interface DecisionTrace {
  recommendation_id: string
  user_id: string
  timestamp: string
  detected_signals: {
    subscriptions: {
      '30d': SignalData
      '180d': SignalData
    }
    savings: {
      '30d': SignalData
      '180d': SignalData
    }
    credit: {
      '30d': SignalData
      '180d': SignalData
    }
    income: {
      '30d': SignalData
      '180d': SignalData
    }
  }
  persona_assignment: {
    persona_id: number
    persona_name: string
    criteria_met: string[]
    priority: number
    rationale: string
    persona_changed?: boolean
  }
  recommendation?: {
    recommendation_id: string
    type: string
    title: string
    content_preview?: string
    rationale_preview?: string
    guardrails?: GuardrailsInfo
  }
  generation_time_ms?: number
}

export interface SignalData {
  [key: string]: any
}

export interface GuardrailsInfo {
  consent?: {
    status: string
    checked_at?: string
  }
  eligibility?: {
    status: string
    explanation?: string
    details?: {
      income?: number
      credit_score?: number
      existing_products?: string[]
      harmful_products?: string[]
    }
  }
  tone?: {
    status: string
    score?: number
    explanation?: string
  }
  disclaimer?: {
    present: boolean
    text?: string
  }
}

export interface SystemAnalytics {
  coverage: {
    users_with_persona: number
    users_with_persona_percent: number
    users_with_behaviors: number
    users_with_behaviors_percent: number
    users_with_both: number
    users_with_both_percent: number
  }
  explainability: {
    recommendations_with_rationales: number
    recommendations_with_rationales_percent: number
    rationales_with_data_points: number
    rationales_with_data_points_percent: number
    rationale_quality_score: number
  }
  performance: {
    p50_latency_ms: number
    p95_latency_ms: number
    p99_latency_ms: number
    mean_latency_ms: number
    min_latency_ms: number
    max_latency_ms: number
    recommendations_within_target: number
    recommendations_within_target_percent: number
  }
  engagement: {
    total_users: number
    active_users: number
    recommendations_sent: number
    recommendations_viewed: number
    recommendations_actioned: number
  }
  fairness?: {
    persona_balance_score: number
    persona_distribution: {
      [personaId: string]: {
        recommendations_count: number
        recommendations_percent: number
        users_count: number
        users_percent: number
      }
    }
    signal_detection_by_persona: {
      [personaId: string]: {
        avg_behaviors_detected: number
        profiles_count: number
      }
    }
  }
}

export const operatorService = {
  // Get review queue
  async getReviewQueue(filters: ReviewQueueFilters = {}): Promise<ReviewQueueResponse> {
    const params: Record<string, any> = {
      skip: filters.skip ?? 0,
      limit: filters.limit ?? 100,
    }

    if (filters.status && filters.status !== 'all') {
      params.status = filters.status
    }
    if (filters.user_id) {
      params.user_id = filters.user_id
    }
    if (filters.type && filters.type !== 'all') {
      params.type = filters.type
    }
    if (filters.persona_id) {
      params.persona_id = filters.persona_id
    }

    const response = await apiClient.get<ReviewQueueResponse>('/api/v1/operator/review', {
      params,
    })
    return response.data
  },

  // Get recommendation for review
  async getRecommendationForReview(recommendationId: string): Promise<RecommendationReviewDetail> {
    const response = await apiClient.get<RecommendationReviewDetail>(`/api/v1/operator/review/${recommendationId}`)
    return response.data
  },

  // Approve recommendation
  async approveRecommendation(recommendationId: string) {
    const response = await apiClient.post(`/api/v1/operator/review/${recommendationId}/approve`)
    return response.data
  },

  // Reject recommendation
  async rejectRecommendation(recommendationId: string, reason: string) {
    const response = await apiClient.post(`/api/v1/operator/review/${recommendationId}/reject`, {
      reason,
    })
    return response.data
  },

  // Modify recommendation
  async modifyRecommendation(
    recommendationId: string,
    updates: { title?: string; content?: string; rationale?: string }
  ) {
    const response = await apiClient.put(`/api/v1/operator/review/${recommendationId}`, updates)
    return response.data
  },

  // Bulk approve recommendations
  async bulkApproveRecommendations(recommendationIds: string[]) {
    const response = await apiClient.post('/api/v1/operator/review/bulk', {
      action: 'approve',
      recommendation_ids: recommendationIds,
    })
    return response.data
  },

  // Bulk reject recommendations
  async bulkRejectRecommendations(recommendationIds: string[], reason: string) {
    const response = await apiClient.post('/api/v1/operator/review/bulk', {
      action: 'reject',
      recommendation_ids: recommendationIds,
      reason,
    })
    return response.data
  },

  // Get system analytics
  async getAnalytics(): Promise<SystemAnalytics> {
    const response = await apiClient.get<SystemAnalytics>('/api/v1/operator/analytics')
    return response.data
  },

  // Export metrics as JSON
  async exportMetricsJSON(): Promise<Blob> {
    const response = await apiClient.get('/api/v1/operator/analytics/export/json', {
      responseType: 'blob',
    })
    return response.data
  },

  // Export metrics as CSV
  async exportMetricsCSV(): Promise<Blob> {
    const response = await apiClient.get('/api/v1/operator/analytics/export/csv', {
      responseType: 'blob',
    })
    return response.data
  },

  // Export summary report
  async exportSummaryReport(): Promise<Blob> {
    const response = await apiClient.get('/api/v1/operator/analytics/export/summary', {
      responseType: 'blob',
    })
    return response.data
  },
}

export type {
  ReviewQueueItem,
  ReviewQueueResponse,
  ReviewQueueFilters,
  RecommendationReviewDetail,
  DecisionTrace,
  SignalData,
  GuardrailsInfo,
  SystemAnalytics,
}

