import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { consentService, type ConsentStatus } from '@/services/consentService'
import { FaInfoCircle, FaCheckCircle } from 'react-icons/fa'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'

/**
 * Financial advice disclaimer text
 * This disclaimer is prominently displayed during consent grant.
 * By granting consent, users acknowledge they have read this disclaimer.
 */
const FINANCIAL_ADVICE_DISCLAIMER = `This is educational content, not financial advice. Consult a licensed advisor for personalized guidance.`

const ConsentPage = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isGranting, setIsGranting] = useState(false)

  // Fetch consent status
  const {
    data: consentStatus,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<ConsentStatus>({
    queryKey: ['consentStatus'],
    queryFn: () => consentService.getConsentStatus(),
  })

  // Redirect if consent is already granted
  useEffect(() => {
    if (consentStatus?.consent_status === true) {
      navigate('/', { replace: true })
    }
  }, [consentStatus, navigate])

  // Grant consent mutation
  const grantConsentMutation = useMutation({
    mutationFn: () => consentService.grantConsent({ tos_accepted: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['consentStatus'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      setIsGranting(false)
      // Redirect to dashboard after granting consent
      navigate('/', { replace: true })
    },
    onError: () => {
      setIsGranting(false)
    },
  })

  const handleGrantConsent = () => {
    setIsGranting(true)
    grantConsentMutation.mutate()
  }

  // Loading skeleton
  if (isLoading) {
    return <PageSkeleton sections={3} />
  }

  // Error state
  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorState
            title="Error Loading Consent Status"
            error={error}
            onRetry={() => refetch()}
            retryLabel="Retry"
          />
        </div>
      </div>
    )
  }

  // Don't show page if consent is already granted (will redirect)
  if (consentStatus?.consent_status === true) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-8 text-center">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Consent Required
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            To use SpendSense and receive personalized financial recommendations, you need to grant
            consent for data processing.
          </p>
        </header>

        {/* Main Content Card */}
        <div className="bg-white rounded-lg shadow-sm p-6 lg:p-8 space-y-8">
          {/* Financial Advice Disclaimer - Prominently Displayed */}
          <div className="border-2 border-blue-200 bg-blue-50 rounded-lg p-6 lg:p-8">
            <div className="flex items-start gap-4 mb-4">
              <FaInfoCircle className="h-8 w-8 text-blue-600 mt-1 flex-shrink-0" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-blue-900 mb-3">
                  Financial Advice Disclaimer
                </h2>
                <div className="bg-white rounded-lg p-6 border border-blue-200 mb-4">
                  <p className="text-base font-medium text-gray-900 leading-relaxed">
                    {FINANCIAL_ADVICE_DISCLAIMER}
                  </p>
                </div>
                <p className="text-sm text-blue-700">
                  By granting consent below, you acknowledge that you have read and understood this
                  disclaimer.
                </p>
              </div>
            </div>
          </div>

          {/* What Consent Means */}
          <div className="border border-gray-200 rounded-lg p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              What does consent mean?
            </h3>
            <ul className="space-y-3 text-gray-700">
              <li className="flex items-start gap-3">
                <FaCheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                <span>
                  <strong>Data Processing:</strong> We'll analyze your transaction data to detect
                  behavioral patterns (subscriptions, savings, credit utilization, income stability).
                </span>
              </li>
              <li className="flex items-start gap-3">
                <FaCheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                <span>
                  <strong>Personalized Recommendations:</strong> Based on your financial patterns,
                  we'll provide educational content and partner offers tailored to your persona.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <FaCheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                <span>
                  <strong>Your Control:</strong> You can revoke consent at any time in Settings.
                  You can also choose to delete your data when revoking consent.
                </span>
              </li>
            </ul>
          </div>

          {/* Grant Consent Button */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleGrantConsent}
              disabled={isGranting || grantConsentMutation.isPending}
              className="flex-1 px-8 py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200 font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isGranting || grantConsentMutation.isPending ? (
                <>
                  <svg
                    className="animate-spin h-5 w-5 text-white"
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
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Granting Consent...
                </>
              ) : (
                <>
                  <FaCheckCircle className="h-5 w-5" />
                  Grant Consent and Continue
                </>
              )}
            </button>
          </div>

          {/* Error Message */}
          {grantConsentMutation.isError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800 font-medium">
                Failed to grant consent. Please try again.
              </p>
            </div>
          )}
        </div>

        {/* Footer Note */}
        <p className="mt-6 text-center text-sm text-gray-500">
          You can manage your consent preferences at any time in{' '}
          <a href="/settings" className="text-primary-600 hover:text-primary-700 underline">
            Settings
          </a>
          .
        </p>
      </div>
    </div>
  )
}

export default ConsentPage

