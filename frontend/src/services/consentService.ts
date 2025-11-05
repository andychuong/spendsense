import apiClient from './api'
import type { AxiosResponse } from 'axios'

export interface ConsentStatus {
  user_id: string
  consent_status: boolean
  consent_version: string
  consent_granted_at: string | null
  consent_revoked_at: string | null
  updated_at: string | null
}

export interface ConsentGrantRequest {
  consent_version?: string
  tos_accepted: boolean
}

export interface ConsentRevokeRequest {
  delete_data?: boolean
}

export const consentService = {
  /**
   * Get current user's consent status
   */
  async getConsentStatus(): Promise<ConsentStatus> {
    const response: AxiosResponse<ConsentStatus> = await apiClient.get('/api/v1/consent')
    return response.data
  },

  /**
   * Grant consent for data processing
   * By granting consent, users acknowledge they have read the financial advice disclaimer
   */
  async grantConsent(request: ConsentGrantRequest = { tos_accepted: true }): Promise<ConsentStatus> {
    const response: AxiosResponse<ConsentStatus> = await apiClient.post('/api/v1/consent', {
      consent_version: request.consent_version || '1.0',
      tos_accepted: request.tos_accepted,
    })
    return response.data
  },

  /**
   * Revoke consent for data processing
   */
  async revokeConsent(request: ConsentRevokeRequest = { delete_data: false }): Promise<ConsentStatus> {
    const response: AxiosResponse<ConsentStatus> = await apiClient.delete('/api/v1/consent', {
      data: request,
    })
    return response.data
  },
}



