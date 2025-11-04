import React from 'react'
import { FaExclamationTriangle, FaSync } from 'react-icons/fa'

interface ErrorStateProps {
  title?: string
  message?: string
  error?: Error | unknown
  onRetry?: () => void
  retryLabel?: string
  className?: string
  showIcon?: boolean
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message,
  error,
  onRetry,
  retryLabel = 'Retry',
  className = '',
  showIcon = true,
}) => {
  const errorMessage =
    message ||
    (error instanceof Error ? error.message : 'An unexpected error occurred') ||
    'An unexpected error occurred'

  return (
    <div
      className={`bg-red-50 border border-red-200 rounded-lg p-6 text-center ${className}`}
      role="alert"
      aria-live="polite"
    >
      {showIcon && (
        <FaExclamationTriangle
          className="mx-auto h-12 w-12 text-red-600 mb-4"
          aria-hidden="true"
        />
      )}
      <h3 className="text-lg font-semibold text-red-900 mb-2" id="error-title">
        {title}
      </h3>
      <p className="text-sm text-red-700 mb-4" id="error-message">
        {errorMessage}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
          aria-describedby="error-title error-message"
        >
          <FaSync className="h-4 w-4" aria-hidden="true" />
          {retryLabel}
        </button>
      )}
    </div>
  )
}

export default ErrorState


