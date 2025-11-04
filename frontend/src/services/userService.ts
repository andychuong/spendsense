import apiClient from './api'

interface UserProfileResponse {
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

export const userService = {
  // Get current user profile
  async getProfile(): Promise<UserProfileResponse> {
    const response = await apiClient.get<UserProfileResponse>('/api/v1/users/me')
    return response.data
  },

  // Update user profile
  async updateProfile(data: { email?: string; phone_number?: string }): Promise<UserProfileResponse> {
    const response = await apiClient.put<UserProfileResponse>('/api/v1/users/me', data)
    return response.data
  },
}

