import { useState, useEffect } from 'react'
import { useAuthStore } from '@/store'
import { authService, userService } from '@/services'
import { validatePhone } from '@/utils/validation'
import PhoneVerification from './PhoneVerification'
import { FaGoogle, FaGithub, FaFacebook, FaApple, FaPhone, FaEnvelope, FaUnlink } from 'react-icons/fa'

interface AccountLinkingProps {
  onUpdate?: () => void
}

const AccountLinking = ({ onUpdate }: AccountLinkingProps) => {
  const { user, setUser } = useAuthStore()
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [linkingProvider, setLinkingProvider] = useState<string | null>(null)
  const [showPhoneVerification, setShowPhoneVerification] = useState(false)
  const [phoneToLink, setPhoneToLink] = useState('')
  const [unlinkingProvider, setUnlinkingProvider] = useState<string | null>(null)
  const [showUnlinkConfirm, setShowUnlinkConfirm] = useState(false)
  const [unlinkType, setUnlinkType] = useState<'oauth' | 'phone' | null>(null)

  const providers = [
    {
      name: 'google',
      label: 'Google',
      icon: FaGoogle,
      color: 'text-blue-600',
    },
    {
      name: 'github',
      label: 'GitHub',
      icon: FaGithub,
      color: 'text-gray-900',
    },
    {
      name: 'facebook',
      label: 'Facebook',
      icon: FaFacebook,
      color: 'text-blue-600',
    },
    {
      name: 'apple',
      label: 'Apple',
      icon: FaApple,
      color: 'text-gray-900',
    },
  ]

  useEffect(() => {
    loadProfile()
  }, [])

  // Handle OAuth callback for account linking
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const state = urlParams.get('state')
    const action = urlParams.get('action')
    const provider = urlParams.get('provider') || sessionStorage.getItem('oauth_provider')

    // Check if this is an account linking callback
    const isLinking = sessionStorage.getItem('oauth_linking') === 'true'
    const storedState = sessionStorage.getItem('oauth_state')

    if (code && state && (action === 'link' || isLinking) && provider) {
      // Verify state matches
      if (state === storedState) {
        handleOAuthCallback(code, state, provider)
      } else {
        setError('Invalid OAuth state. Please try again.')
        // Clear URL parameters
        window.history.replaceState({}, document.title, window.location.pathname)
      }
    }
  }, [])

  const loadProfile = async () => {
    try {
      setLoading(true)
      setError(null)
      const profileData = await userService.getProfile()
      setProfile(profileData)
      
      // Update user in store if needed
      if (user) {
        setUser({
          ...user,
          email: profileData.email || user.email,
          phone: profileData.phone_number || user.phone,
          oauth_providers: profileData.oauth_providers || {},
        })
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleOAuthCallback = async (code: string, state: string, provider: string) => {
    try {
      setLoading(true)
      setError(null)
      
      // Construct redirect_uri that was used in the authorize request
      const redirectUri = `${window.location.origin}/settings?action=link&provider=${provider}`
      
      const response = await authService.linkOAuthProvider({
        code,
        state,
        redirect_uri: redirectUri,
      })

      if (response.merged_account) {
        setSuccess(`Successfully linked ${provider} account and merged duplicate account data.`)
      } else {
        setSuccess(`Successfully linked ${provider} account.`)
      }

      // Clear sessionStorage
      sessionStorage.removeItem('oauth_linking')
      sessionStorage.removeItem('oauth_provider')
      sessionStorage.removeItem('oauth_state')

      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname)

      // Reload profile
      await loadProfile()
      if (onUpdate) onUpdate()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || `Failed to link ${provider} account`)
      
      // Clear sessionStorage on error
      sessionStorage.removeItem('oauth_linking')
      sessionStorage.removeItem('oauth_provider')
      sessionStorage.removeItem('oauth_state')
    } finally {
      setLoading(false)
    }
  }

  const handleLinkOAuth = async (provider: string) => {
    try {
      setLinkingProvider(provider)
      setError(null)
      
      // Set redirect_uri to settings page for account linking
      const redirectUri = `${window.location.origin}/settings?action=link&provider=${provider}`
      
      // Get OAuth authorize URL with linking redirect_uri
      const response = await authService.getOAuthAuthorizeUrl(provider, redirectUri)
      
      // Store state in sessionStorage for callback
      sessionStorage.setItem('oauth_linking', 'true')
      sessionStorage.setItem('oauth_provider', provider)
      sessionStorage.setItem('oauth_state', response.state)
      
      // Redirect to OAuth provider
      window.location.href = response.authorize_url
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || `Failed to initiate ${provider} linking`)
      setLinkingProvider(null)
    }
  }

  const handleLinkPhone = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate phone
    const phoneError = validatePhone(phoneToLink)
    if (phoneError) {
      setError(phoneError.message)
      return
    }

    try {
      setLoading(true)
      await authService.requestPhoneVerification(phoneToLink)
      setShowPhoneVerification(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to send verification code')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyPhone = async (code: string) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await authService.linkPhoneNumber({
        phone: phoneToLink,
        code,
      })

      if (response.merged_account) {
        setSuccess('Successfully linked phone number and merged duplicate account data.')
      } else {
        setSuccess('Successfully linked phone number.')
      }

      setShowPhoneVerification(false)
      setPhoneToLink('')
      await loadProfile()
      if (onUpdate) onUpdate()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to link phone number')
    } finally {
      setLoading(false)
    }
  }

  const handleUnlink = async () => {
    try {
      setLoading(true)
      setError(null)

      if (unlinkType === 'oauth' && unlinkingProvider) {
        await authService.unlinkOAuthProvider(unlinkingProvider)
        setSuccess(`Successfully unlinked ${unlinkingProvider} account.`)
      } else if (unlinkType === 'phone') {
        await authService.unlinkPhoneNumber()
        setSuccess('Successfully unlinked phone number.')
      }

      setShowUnlinkConfirm(false)
      setUnlinkingProvider(null)
      setUnlinkType(null)
      await loadProfile()
      if (onUpdate) onUpdate()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to unlink account')
    } finally {
      setLoading(false)
    }
  }

  const isLinked = (provider: string) => {
    return profile?.oauth_providers?.[provider.toLowerCase()] !== undefined
  }

  const hasEmailPassword = () => {
    return profile?.email && profile?.email !== ''
  }

  const hasPhone = () => {
    return profile?.phone_number && profile?.phone_number !== ''
  }

  const countAuthMethods = () => {
    let count = 0
    if (hasEmailPassword()) count++
    if (hasPhone()) count++
    if (profile?.oauth_providers) {
      count += Object.keys(profile.oauth_providers).length
    }
    return count
  }

  if (showPhoneVerification) {
    return (
      <PhoneVerification
        phone={phoneToLink}
        onVerify={handleVerifyPhone}
        onBack={() => {
          setShowPhoneVerification(false)
          setPhoneToLink('')
        }}
        onResend={async () => {
          try {
            await authService.requestPhoneVerification(phoneToLink)
          } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to resend code')
          }
        }}
      />
    )
  }

  if (loading && !profile) {
    return (
      <div className="flex justify-center items-center py-8">
        <svg
          className="animate-spin h-8 w-8 text-primary-600"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Linked Accounts</h3>
        <p className="mt-1 text-sm text-gray-500">
          Link multiple authentication methods to your account for easier access.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">
          {success}
        </div>
      )}

      {/* Email/Password Account */}
      <div className="border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FaEnvelope className="text-gray-600 text-xl" />
            <div>
              <p className="font-medium text-gray-900">Email/Password</p>
              <p className="text-sm text-gray-500">
                {hasEmailPassword() ? profile?.email : 'Not linked'}
              </p>
            </div>
          </div>
          {hasEmailPassword() && (
            <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
              Linked
            </span>
          )}
        </div>
      </div>

      {/* Phone Number */}
      <div className="border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <FaPhone className="text-gray-600 text-xl" />
            <div>
              <p className="font-medium text-gray-900">Phone Number</p>
              <p className="text-sm text-gray-500">
                {hasPhone() ? profile?.phone_number : 'Not linked'}
              </p>
            </div>
          </div>
          {hasPhone() ? (
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                Linked
              </span>
              <button
                type="button"
                onClick={() => {
                  setUnlinkingProvider(null)
                  setUnlinkType('phone')
                  setShowUnlinkConfirm(true)
                }}
                disabled={countAuthMethods() <= 1}
                className="text-red-600 hover:text-red-700 disabled:text-gray-400 disabled:cursor-not-allowed"
                title={
                  countAuthMethods() <= 1
                    ? 'Cannot unlink: You must have at least one authentication method'
                    : 'Unlink phone number'
                }
              >
                <FaUnlink className="text-sm" />
              </button>
            </div>
          ) : (
            <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded">
              Not linked
            </span>
          )}
        </div>
        {!hasPhone() && (
          <form onSubmit={handleLinkPhone} className="mt-4 flex gap-2">
            <input
              type="tel"
              value={phoneToLink}
              onChange={(e) => setPhoneToLink(e.target.value)}
              placeholder="+1234567890"
              className="
                flex-1 px-3 py-2 border border-gray-300 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                text-sm
              "
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading}
              className="
                px-4 py-2 bg-primary-600 text-white rounded-lg
                hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                disabled:opacity-50 disabled:cursor-not-allowed
                text-sm font-medium transition-colors duration-200
              "
            >
              Link
            </button>
          </form>
        )}
      </div>

      {/* OAuth Providers */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-900">OAuth Providers</h4>
        {providers.map((provider) => {
          const Icon = provider.icon
          const linked = isLinked(provider.name)
          const isLinking = linkingProvider === provider.name

          return (
            <div key={provider.name} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Icon className={`${provider.color} text-xl`} />
                  <div>
                    <p className="font-medium text-gray-900">{provider.label}</p>
                    <p className="text-sm text-gray-500">
                      {linked ? 'Linked' : 'Not linked'}
                    </p>
                  </div>
                </div>
                {linked ? (
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                      Linked
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setUnlinkingProvider(provider.name)
                        setUnlinkType('oauth')
                        setShowUnlinkConfirm(true)
                      }}
                      disabled={countAuthMethods() <= 1}
                      className="text-red-600 hover:text-red-700 disabled:text-gray-400 disabled:cursor-not-allowed"
                      title={
                        countAuthMethods() <= 1
                          ? 'Cannot unlink: You must have at least one authentication method'
                          : `Unlink ${provider.label}`
                      }
                    >
                      <FaUnlink className="text-sm" />
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => handleLinkOAuth(provider.name)}
                    disabled={isLinking || loading}
                    className="
                      px-4 py-2 bg-primary-600 text-white rounded-lg
                      hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                      disabled:opacity-50 disabled:cursor-not-allowed
                      text-sm font-medium transition-colors duration-200
                    "
                  >
                    {isLinking ? 'Connecting...' : 'Link'}
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Unlink Confirmation Dialog */}
      {showUnlinkConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Unlink Account</h3>
            <p className="text-sm text-gray-600 mb-4">
              Are you sure you want to unlink this authentication method? You will no longer be able to sign in using this method.
            </p>
            {countAuthMethods() <= 1 && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg text-sm mb-4">
                Warning: This is your only authentication method. You must have at least one method linked to your account.
              </div>
            )}
            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={() => {
                  setShowUnlinkConfirm(false)
                  setUnlinkingProvider(null)
                  setUnlinkType(null)
                }}
                className="
                  px-4 py-2 border border-gray-300 rounded-lg
                  text-gray-700 hover:bg-gray-50
                  focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500
                  text-sm font-medium transition-colors duration-200
                "
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleUnlink}
                disabled={loading || countAuthMethods() <= 1}
                className="
                  px-4 py-2 bg-red-600 text-white rounded-lg
                  hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500
                  disabled:opacity-50 disabled:cursor-not-allowed
                  text-sm font-medium transition-colors duration-200
                "
              >
                {loading ? 'Unlinking...' : 'Unlink'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AccountLinking

