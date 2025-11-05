import React from 'react'
import { FaExclamationTriangle, FaInfoCircle, FaCheckCircle, FaTimesCircle } from 'react-icons/fa'

export type DialogType = 'approve' | 'reject' | 'confirm' | 'warning' | 'info'

interface ConfirmationDialogProps {
  isOpen: boolean
  type: DialogType
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  onConfirm: () => void
  onCancel: () => void
  isLoading?: boolean
  requireTextInput?: boolean
  textInputValue?: string
  onTextInputChange?: (value: string) => void
  textInputPlaceholder?: string
  textInputLabel?: string
  textInputRequired?: boolean
}

const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  isOpen,
  type,
  title,
  message,
  confirmLabel,
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  isLoading = false,
  requireTextInput = false,
  textInputValue = '',
  onTextInputChange,
  textInputPlaceholder = '',
  textInputLabel = '',
  textInputRequired = false,
}) => {
  if (!isOpen) return null

  const getIcon = () => {
    switch (type) {
      case 'approve':
        return <FaCheckCircle className="h-6 w-6 text-green-600" />
      case 'reject':
        return <FaTimesCircle className="h-6 w-6 text-red-600" />
      case 'warning':
        return <FaExclamationTriangle className="h-6 w-6 text-yellow-600" />
      case 'info':
        return <FaInfoCircle className="h-6 w-6 text-blue-600" />
      default:
        return <FaInfoCircle className="h-6 w-6 text-gray-600" />
    }
  }

  const getConfirmButtonClass = () => {
    switch (type) {
      case 'approve':
        return 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
      case 'reject':
        return 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
      case 'warning':
        return 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
      default:
        return 'bg-primary-600 hover:bg-primary-700 focus:ring-primary-500'
    }
  }

  const getDefaultConfirmLabel = () => {
    switch (type) {
      case 'approve':
        return 'Approve'
      case 'reject':
        return 'Reject'
      default:
        return 'Confirm'
    }
  }

  const canConfirm = requireTextInput
    ? textInputValue.trim().length > 0 || !textInputRequired
    : true

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onCancel()
        }
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      aria-describedby="dialog-message"
    >
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 transform transition-all">
        <div className="flex items-start gap-4 mb-4">
          <div className="flex-shrink-0">{getIcon()}</div>
          <div className="flex-1 min-w-0">
            <h3
              id="dialog-title"
              className="text-lg font-semibold text-gray-900 mb-2"
            >
              {title}
            </h3>
            <p
              id="dialog-message"
              className="text-sm text-gray-600 whitespace-pre-wrap"
            >
              {message}
            </p>
          </div>
        </div>

        {requireTextInput && (
          <div className="mb-4">
            {textInputLabel && (
              <label
                htmlFor="dialog-text-input"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                {textInputLabel}
                {textInputRequired && <span className="text-red-600 ml-1">*</span>}
              </label>
            )}
            <textarea
              id="dialog-text-input"
              value={textInputValue}
              onChange={(e) => onTextInputChange?.(e.target.value)}
              placeholder={textInputPlaceholder}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
              aria-required={textInputRequired}
              aria-invalid={textInputRequired && !textInputValue.trim()}
            />
            {textInputRequired && !textInputValue.trim() && (
              <p className="mt-1 text-xs text-red-600">
                This field is required
              </p>
            )}
          </div>
        )}

        <div className="flex items-center gap-2 justify-end">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            aria-label="Cancel"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading || !canConfirm}
            className={`px-4 py-2 text-sm font-medium text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 ${getConfirmButtonClass()}`}
            aria-label={confirmLabel || getDefaultConfirmLabel()}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg
                  className="animate-spin h-4 w-4"
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
                Processing...
              </span>
            ) : (
              confirmLabel || getDefaultConfirmLabel()
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmationDialog


