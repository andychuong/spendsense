import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { authService } from '@/services/authService'
import { validateEmail, validatePhone } from '@/utils/validation'
import OAuthButtons from '@/components/OAuthButtons'
import PhoneVerification from '@/components/PhoneVerification'

type AuthMethod = 'email' | 'phone'

const Login = () => {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [authMethod, setAuthMethod] = useState<AuthMethod>('email')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Email/Password form state
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  // Phone form state
  const [phone, setPhone] = useState('')
  const [showPhoneVerification, setShowPhoneVerification] = useState(false)

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setErrors({})

    // Validate email
    const emailError = validateEmail(email)
    if (emailError) {
      setErrors({ [emailError.field]: emailError.message })
      return
    }

    // Validate password
    if (!password) {
      setErrors({ password: 'Password is required' })
      return
    }

    setLoading(true)
    try {
      const response = await authService.login(email, password)
      
      // Store auth tokens and user info
      setAuth(
        {
          id: response.user_id,
          email: response.email,
          role: 'user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          access_token: response.access_token,
          refresh_token: response.refresh_token,
          token_type: response.token_type,
        }
      )

      // Redirect to dashboard
      navigate('/')
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Login failed. Please try again.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handlePhoneRequest = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setErrors({})

    // Validate phone
    const phoneError = validatePhone(phone)
    if (phoneError) {
      setErrors({ [phoneError.field]: phoneError.message })
      return
    }

    setLoading(true)
    try {
      await authService.requestPhoneVerification(phone)
      setShowPhoneVerification(true)
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Failed to send verification code. Please try again.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handlePhoneVerify = async (code: string) => {
    setError(null)
    setLoading(true)
    try {
      const response = await authService.verifyPhoneCode(phone, code)
      
      // Store auth tokens and user info
      setAuth(
        {
          id: response.user_id,
          phone: response.phone,
          role: 'user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          access_token: response.access_token,
          refresh_token: response.refresh_token,
          token_type: response.token_type,
        }
      )

      // Redirect to dashboard
      navigate('/')
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Verification failed. Please try again.'
      setError(errorMessage)
      setLoading(false)
    }
  }

  if (showPhoneVerification) {
    return (
      <PhoneVerification
        phone={phone}
        onVerify={handlePhoneVerify}
        onBack={() => setShowPhoneVerification(false)}
        onResend={async () => {
          try {
            await authService.requestPhoneVerification(phone)
          } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to resend code')
          }
        }}
      />
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Welcome back
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your SpendSense account
          </p>
        </div>

        {/* Auth Method Tabs */}
        <div className="flex gap-2 bg-gray-100 p-1 rounded-lg">
          <button
            type="button"
            onClick={() => setAuthMethod('email')}
            className={`
              flex-1 py-2 px-4 rounded-md font-medium transition-all duration-200
              ${authMethod === 'email'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
              }
            `}
          >
            Email
          </button>
          <button
            type="button"
            onClick={() => setAuthMethod('phone')}
            className={`
              flex-1 py-2 px-4 rounded-md font-medium transition-all duration-200
              ${authMethod === 'phone'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
              }
            `}
          >
            Phone
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Email/Password Form */}
        {authMethod === 'email' && (
          <form onSubmit={handleEmailLogin} className="mt-8 space-y-6">
            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`
                    appearance-none block w-full px-3 py-2 border rounded-lg
                    placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                    ${errors.email ? 'border-red-300' : 'border-gray-300'}
                  `}
                  placeholder="you@example.com"
                  disabled={loading}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`
                    appearance-none block w-full px-3 py-2 border rounded-lg
                    placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                    ${errors.password ? 'border-red-300' : 'border-gray-300'}
                  `}
                  placeholder="••••••••"
                  disabled={loading}
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password}</p>
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="
                w-full flex justify-center py-3 px-4 border border-transparent rounded-lg
                shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200
              "
            >
              {loading ? (
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
              ) : (
                'Sign in'
              )}
            </button>
          </form>
        )}

        {/* Phone Form */}
        {authMethod === 'phone' && (
          <form onSubmit={handlePhoneRequest} className="mt-8 space-y-6">
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                Phone number
              </label>
              <input
                id="phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className={`
                  appearance-none block w-full px-3 py-2 border rounded-lg
                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                  ${errors.phone ? 'border-red-300' : 'border-gray-300'}
                `}
                placeholder="+1234567890"
                disabled={loading}
              />
              {errors.phone && (
                <p className="mt-1 text-sm text-red-600">{errors.phone}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Enter phone number in E.164 format (e.g., +1234567890)
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="
                w-full flex justify-center py-3 px-4 border border-transparent rounded-lg
                shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200
              "
            >
              {loading ? (
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
              ) : (
                'Send verification code'
              )}
            </button>
          </form>
        )}

        {/* Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-gray-50 text-gray-500">Or continue with</span>
          </div>
        </div>

        {/* OAuth Buttons */}
        <OAuthButtons />

        {/* Link to Register */}
        <p className="text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="font-medium text-primary-600 hover:text-primary-500">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Login
