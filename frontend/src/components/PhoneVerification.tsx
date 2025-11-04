import { useState, useEffect } from 'react'
import { validateVerificationCode } from '@/utils/validation'

interface PhoneVerificationProps {
  phone: string
  onVerify: (code: string) => Promise<void>
  onBack: () => void
  onResend: () => Promise<void>
}

const PhoneVerification = ({ phone, onVerify, onBack, onResend }: PhoneVerificationProps) => {
  const [code, setCode] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [resendLoading, setResendLoading] = useState(false)
  const [timeLeft, setTimeLeft] = useState(600) // 10 minutes in seconds
  const [canResend, setCanResend] = useState(false)

  // Countdown timer
  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000)
      return () => clearTimeout(timer)
    } else {
      setCanResend(true)
    }
  }, [timeLeft])

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate code
    const codeError = validateVerificationCode(code)
    if (codeError) {
      setError(codeError.message)
      return
    }

    setLoading(true)
    try {
      await onVerify(code)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Verification failed')
      setLoading(false)
    }
  }

  const handleResend = async () => {
    setResendLoading(true)
    setError(null)
    try {
      await onResend()
      setTimeLeft(600) // Reset timer
      setCanResend(false)
      setCode('') // Clear code input
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to resend code')
    } finally {
      setResendLoading(false)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Verify your phone
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            We sent a 6-digit verification code to
          </p>
          <p className="text-center text-sm font-medium text-gray-900">
            {phone}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleVerify} className="mt-8 space-y-6">
          <div>
            <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1 text-center">
              Verification Code
            </label>
            <input
              id="code"
              type="text"
              value={code}
              onChange={(e) => {
                // Only allow digits, max 6
                const value = e.target.value.replace(/\D/g, '').slice(0, 6)
                setCode(value)
              }}
              placeholder="000000"
              maxLength={6}
              className={`
                appearance-none block w-full px-3 py-3 border rounded-lg
                text-center text-2xl tracking-widest font-mono
                placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                ${error ? 'border-red-300' : 'border-gray-300'}
              `}
              disabled={loading}
              autoFocus
            />
          </div>

          {/* Timer */}
          {!canResend && (
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Code expires in:{' '}
                <span className="font-medium text-gray-900">{formatTime(timeLeft)}</span>
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              type="submit"
              disabled={loading || code.length !== 6}
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
                'Verify code'
              )}
            </button>

            <button
              type="button"
              onClick={handleResend}
              disabled={!canResend || resendLoading}
              className="
                w-full flex justify-center py-3 px-4 border border-gray-300 rounded-lg
                text-sm font-medium text-gray-700 bg-white hover:bg-gray-50
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200
              "
            >
              {resendLoading ? (
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
                'Resend code'
              )}
            </button>

            <button
              type="button"
              onClick={onBack}
              className="
                w-full flex justify-center py-3 px-4 border border-gray-300 rounded-lg
                text-sm font-medium text-gray-700 bg-white hover:bg-gray-50
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500
                transition-colors duration-200
              "
            >
              Back
            </button>
          </div>
        </form>

        <div className="text-center">
          <p className="text-xs text-gray-500">
            Didn't receive the code? Check your phone number and try resending.
          </p>
        </div>
      </div>
    </div>
  )
}

export default PhoneVerification
