import React from 'react'
import { Link } from 'react-router-dom'
import { FaInfoCircle, FaUpload, FaPlus, FaArrowRight } from 'react-icons/fa'

interface EmptyStateProps {
  title: string
  description: string
  icon?: React.ReactNode
  action?: {
    label: string
    to?: string
    onClick?: () => void
    icon?: React.ReactNode
  }
  secondaryAction?: {
    label: string
    to?: string
    onClick?: () => void
  }
  className?: string
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
  secondaryAction,
  className = '',
}) => {
  const defaultIcon = icon || <FaInfoCircle className="mx-auto h-12 w-12 text-gray-400" />

  const ActionButton = action ? (
    action.to ? (
      <Link
        to={action.to}
        className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200 font-medium"
      >
        {action.icon || <FaArrowRight className="h-5 w-5" aria-hidden="true" />}
        {action.label}
      </Link>
    ) : (
      <button
        onClick={action.onClick}
        className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200 font-medium"
      >
        {action.icon || <FaArrowRight className="h-5 w-5" aria-hidden="true" />}
        {action.label}
      </button>
    )
  ) : null

  const SecondaryButton = secondaryAction ? (
    secondaryAction.to ? (
      <Link
        to={secondaryAction.to}
        className="inline-flex items-center gap-2 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 font-medium"
      >
        {secondaryAction.label}
      </Link>
    ) : (
      <button
        onClick={secondaryAction.onClick}
        className="inline-flex items-center gap-2 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 font-medium"
      >
        {secondaryAction.label}
      </button>
    )
  ) : null

  return (
    <div
      className={`bg-white border border-gray-200 rounded-lg p-12 text-center ${className}`}
      role="status"
      aria-live="polite"
    >
      <div className="flex justify-center mb-4" aria-hidden="true">
        {defaultIcon}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600 mb-6 max-w-md mx-auto">{description}</p>
      {(action || secondaryAction) && (
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          {ActionButton}
          {SecondaryButton}
        </div>
      )}
    </div>
  )
}

export default EmptyState



