import { useState } from 'react'
import { authService } from '@/services/authService'
import { FaGoogle, FaGithub, FaFacebook, FaApple } from 'react-icons/fa'

const OAuthButtons = () => {
  const [loading, setLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const providers = [
    {
      name: 'google',
      label: 'Google',
      icon: FaGoogle,
      bgColor: 'bg-white hover:bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-300',
    },
    {
      name: 'github',
      label: 'GitHub',
      icon: FaGithub,
      bgColor: 'bg-gray-900 hover:bg-gray-800',
      textColor: 'text-white',
      borderColor: 'border-gray-900',
    },
    {
      name: 'facebook',
      label: 'Facebook',
      icon: FaFacebook,
      bgColor: 'bg-blue-600 hover:bg-blue-700',
      textColor: 'text-white',
      borderColor: 'border-blue-600',
    },
    {
      name: 'apple',
      label: 'Apple',
      icon: FaApple,
      bgColor: 'bg-black hover:bg-gray-900',
      textColor: 'text-white',
      borderColor: 'border-black',
    },
  ]

  const handleOAuthLogin = async (provider: string) => {
    setLoading(provider)
    setError(null)
    try {
      const response = await authService.getOAuthAuthorizeUrl(provider)
      // Redirect to OAuth provider
      window.location.href = response.authorize_url
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || `Failed to initiate ${provider} login`
      setError(errorMessage)
      setLoading(null)
    }
  }

  return (
    <div className="space-y-3">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {providers.map((provider) => {
        const Icon = provider.icon
        const isLoading = loading === provider.name
        const isDisabled = loading !== null

        return (
          <button
            key={provider.name}
            type="button"
            onClick={() => handleOAuthLogin(provider.name)}
            disabled={isDisabled}
            className={`
              w-full flex items-center justify-center gap-3 px-4 py-3 
              border rounded-lg font-medium transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
              focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
              ${provider.bgColor} ${provider.textColor} ${provider.borderColor}
            `}
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin h-5 w-5"
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
                <span>Connecting...</span>
              </>
            ) : (
              <>
                <Icon className="w-5 h-5" />
                <span>Continue with {provider.label}</span>
              </>
            )}
          </button>
        )
      })}

      <p className="text-xs text-gray-500 text-center mt-2">
        OAuth providers require backend configuration to be fully functional
      </p>
    </div>
  )
}

export default OAuthButtons
