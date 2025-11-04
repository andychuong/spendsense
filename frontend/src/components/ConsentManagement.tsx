import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { consentService, type ConsentStatus } from '@/services/consentService'
import { FaExclamationTriangle, FaCheckCircle, FaInfoCircle, FaHistory, FaClock } from 'react-icons/fa'

/**
 * Financial advice disclaimer text
 * This disclaimer is prominently displayed during consent grant.
 * By granting consent, users acknowledge they have read this disclaimer.
 */
const FINANCIAL_ADVICE_DISCLAIMER = `This is educational content, not financial advice. Consult a licensed advisor for personalized guidance.`

const ConsentManagement = () => {
  const queryClient = useQueryClient()
  const [showRevokeConfirm, setShowRevokeConfirm] = useState(false)

  // Fetch consent status
  const {
    data: consentStatus,
    isLoading,
    isError,
  } = useQuery<ConsentStatus>({
    queryKey: ['consentStatus'],
    queryFn: () => consentService.getConsentStatus(),
  })

  // Grant consent mutation
  const grantConsentMutation = useMutation({
    mutationFn: () => consentService.grantConsent({ tos_accepted: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['consentStatus'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  // Revoke consent mutation
  const revokeConsentMutation = useMutation({
    mutationFn: (deleteData: boolean) =>
      consentService.revokeConsent({ delete_data: deleteData }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['consentStatus'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      setShowRevokeConfirm(false)
    },
  })

  const handleGrantConsent = () => {
    grantConsentMutation.mutate()
  }

  const handleRevokeConsent = (deleteData: boolean = false) => {
    revokeConsentMutation.mutate(deleteData)
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-48"></div>
          <div className="h-24 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded w-32"></div>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="text-center py-8">
          <FaExclamationTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Consent Status</h3>
          <p className="text-sm text-gray-600">
            Unable to load your consent status. Please try again later.
          </p>
        </div>
      </div>
    )
  }

  const hasConsent = consentStatus?.consent_status === true

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Consent Management</h2>
        <p className="text-sm text-gray-600">
          Manage your consent for data processing and personalized recommendations.
        </p>
      </div>

      {/* Current Status */}
      <div
        className={`p-4 rounded-lg border-2 ${
          hasConsent
            ? 'bg-green-50 border-green-200'
            : 'bg-yellow-50 border-yellow-200'
        }`}
      >
        <div className="flex items-start gap-3">
          {hasConsent ? (
            <FaCheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
          ) : (
            <FaExclamationTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
          )}
          <div className="flex-1">
            <h3
              className={`text-lg font-semibold ${
                hasConsent ? 'text-green-700' : 'text-yellow-700'
              }`}
            >
              Consent Status: {hasConsent ? 'Granted' : 'Not Granted'}
            </h3>
            <p className={`text-sm mt-1 ${hasConsent ? 'text-green-600' : 'text-yellow-600'}`}>
              {hasConsent
                ? `You granted consent on ${consentStatus?.consent_granted_at ? new Date(consentStatus.consent_granted_at).toLocaleDateString() : 'previously'}. Your personalized recommendations are active.`
                : 'Consent is required to process your data and generate personalized recommendations.'}
            </p>
            {hasConsent && consentStatus?.consent_version && (
              <p className="text-xs text-green-600 mt-1">
                Consent Version: {consentStatus.consent_version}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Financial Advice Disclaimer - Prominently Displayed */}
      {!hasConsent && (
        <div className="border-2 border-blue-200 bg-blue-50 rounded-lg p-6">
          <div className="flex items-start gap-3 mb-4">
            <FaInfoCircle className="h-6 w-6 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                Financial Advice Disclaimer
              </h3>
              <div className="bg-white rounded p-4 border border-blue-200">
                <p className="text-sm font-medium text-gray-900 leading-relaxed">
                  {FINANCIAL_ADVICE_DISCLAIMER}
                </p>
              </div>
              <p className="text-xs text-blue-700 mt-3">
                By granting consent below, you acknowledge that you have read and understood this
                disclaimer.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        {!hasConsent ? (
          <button
            onClick={handleGrantConsent}
            disabled={grantConsentMutation.isPending}
            className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {grantConsentMutation.isPending ? 'Granting Consent...' : 'Grant Consent'}
          </button>
        ) : (
          <>
            {!showRevokeConfirm ? (
              <button
                onClick={() => setShowRevokeConfirm(true)}
                className="px-6 py-3 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200 font-medium"
              >
                Revoke Consent
              </button>
            ) : (
              <div className="flex flex-col sm:flex-row gap-3 flex-1">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex-1">
                  <p className="text-sm text-yellow-800 font-medium mb-2">
                    Are you sure you want to revoke consent?
                  </p>
                  <p className="text-xs text-yellow-700">
                    Revoking consent will stop personalized recommendations. You can optionally
                    delete all your data.
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleRevokeConsent(false)}
                    disabled={revokeConsentMutation.isPending}
                    className="px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {revokeConsentMutation.isPending ? 'Revoking...' : 'Revoke Only'}
                  </button>
                  <button
                    onClick={() => handleRevokeConsent(true)}
                    disabled={revokeConsentMutation.isPending}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {revokeConsentMutation.isPending
                      ? 'Revoking...'
                      : 'Revoke & Delete Data'}
                  </button>
                  <button
                    onClick={() => setShowRevokeConfirm(false)}
                    disabled={revokeConsentMutation.isPending}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Consent History / Audit Log */}
      {(consentStatus?.consent_granted_at || consentStatus?.consent_revoked_at || consentStatus?.updated_at) && (
        <div className="border-t border-gray-200 pt-6">
          <div className="flex items-center gap-2 mb-4">
            <FaHistory className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Consent History</h3>
          </div>
          <div className="space-y-3">
            {consentStatus.consent_granted_at && (
              <div className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                <FaCheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-green-900">Consent Granted</p>
                  <div className="flex items-center gap-2 mt-1">
                    <FaClock className="h-3 w-3 text-green-600" />
                    <p className="text-xs text-green-700">
                      {new Date(consentStatus.consent_granted_at).toLocaleString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                  {consentStatus.consent_version && (
                    <p className="text-xs text-green-600 mt-1">
                      Version: {consentStatus.consent_version}
                    </p>
                  )}
                </div>
              </div>
            )}
            {consentStatus.consent_revoked_at && (
              <div className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                <FaExclamationTriangle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-red-900">Consent Revoked</p>
                  <div className="flex items-center gap-2 mt-1">
                    <FaClock className="h-3 w-3 text-red-600" />
                    <p className="text-xs text-red-700">
                      {new Date(consentStatus.consent_revoked_at).toLocaleString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>
              </div>
            )}
            {consentStatus.updated_at && !consentStatus.consent_granted_at && !consentStatus.consent_revoked_at && (
              <div className="flex items-start gap-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <FaClock className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Last Updated</p>
                  <p className="text-xs text-gray-600 mt-1">
                    {new Date(consentStatus.updated_at).toLocaleString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error Messages */}
      {grantConsentMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            Failed to grant consent. Please try again.
          </p>
        </div>
      )}

      {revokeConsentMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            Failed to revoke consent. Please try again.
          </p>
        </div>
      )}
    </div>
  )
}

export default ConsentManagement

