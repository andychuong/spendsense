import apiClient from './api'

// Auth API response types
interface RegisterResponse {
  user_id: string
  email: string
  access_token: string
  refresh_token: string
  token_type: string
}

interface LoginResponse {
  user_id: string
  email: string
  access_token: string
  refresh_token: string
  token_type: string
}

interface PhoneRequestResponse {
  message: string
  phone: string
}

interface PhoneVerifyResponse {
  user_id: string
  phone: string
  access_token: string
  refresh_token: string
  token_type: string
  is_new_user: boolean
}

interface OAuthAuthorizeResponse {
  authorize_url: string
  state: string
}

interface OAuthLinkRequest {
  code: string
  state: string
  redirect_uri: string
}

interface OAuthLinkResponse {
  message: string
  provider: string
  merged_account: boolean
}

interface PhoneLinkRequest {
  phone: string
  code: string
}

interface PhoneLinkResponse {
  message: string
  phone: string
  merged_account: boolean
}

interface UnlinkResponse {
  message: string
}

// Auth Service Functions
export const authService = {
  // Email/Password Registration
  async register(email: string, password: string): Promise<RegisterResponse> {
    const response = await apiClient.post<RegisterResponse>('/api/v1/auth/register', {
      email,
      password,
    })
    return response.data
  },

  // Email/Password Login
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/api/v1/auth/login', {
      email,
      password,
    })
    return response.data
  },

  // Phone Verification Request
  async requestPhoneVerification(phone: string): Promise<PhoneRequestResponse> {
    const response = await apiClient.post<PhoneRequestResponse>(
      '/api/v1/auth/phone/request',
      { phone }
    )
    return response.data
  },

  // Phone Verification Verify
  async verifyPhoneCode(phone: string, code: string): Promise<PhoneVerifyResponse> {
    const response = await apiClient.post<PhoneVerifyResponse>(
      '/api/v1/auth/phone/verify',
      { phone, code }
    )
    return response.data
  },

  // OAuth Authorization
  async getOAuthAuthorizeUrl(provider: string, redirectUri?: string): Promise<OAuthAuthorizeResponse> {
    const params = redirectUri ? { redirect_uri: redirectUri } : {}
    const response = await apiClient.get<OAuthAuthorizeResponse>(
      `/api/v1/auth/oauth/${provider}/authorize`,
      { params }
    )
    return response.data
  },

  // Logout
  async logout(): Promise<void> {
    await apiClient.post('/api/v1/auth/logout')
  },

  // Account Linking - OAuth
  async linkOAuthProvider(request: OAuthLinkRequest): Promise<OAuthLinkResponse> {
    const response = await apiClient.post<OAuthLinkResponse>(
      '/api/v1/auth/oauth/link',
      request
    )
    return response.data
  },

  // Account Linking - Phone
  async linkPhoneNumber(request: PhoneLinkRequest): Promise<PhoneLinkResponse> {
    const response = await apiClient.post<PhoneLinkResponse>(
      '/api/v1/auth/phone/link',
      request
    )
    return response.data
  },

  // Account Unlinking - OAuth
  async unlinkOAuthProvider(provider: string): Promise<UnlinkResponse> {
    const response = await apiClient.delete<UnlinkResponse>(
      `/api/v1/auth/oauth/unlink/${provider}`
    )
    return response.data
  },

  // Account Unlinking - Phone
  async unlinkPhoneNumber(): Promise<UnlinkResponse> {
    const response = await apiClient.delete<UnlinkResponse>(
      '/api/v1/auth/phone/unlink'
    )
    return response.data
  },
}

