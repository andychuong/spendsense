import React from 'react'

interface LoadingSkeletonProps {
  variant?: 'text' | 'card' | 'list' | 'table' | 'circular'
  width?: string
  height?: string
  lines?: number
  className?: string
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'text',
  width,
  height,
  lines = 1,
  className = '',
}) => {
  const baseClasses = 'animate-pulse bg-gray-200 rounded'

  switch (variant) {
    case 'text':
      return (
        <div
          className={`${baseClasses} ${className}`}
          style={{
            width: width || '100%',
            height: height || '1rem',
          }}
          aria-label="Loading content"
          role="status"
        >
          <span className="sr-only">Loading...</span>
        </div>
      )

    case 'card':
      return (
        <div
          className={`${baseClasses} ${className}`}
          style={{
            width: width || '100%',
            height: height || '200px',
          }}
          aria-label="Loading card"
          role="status"
        >
          <span className="sr-only">Loading...</span>
        </div>
      )

    case 'list':
      return (
        <div className={`space-y-3 ${className}`} role="status" aria-label="Loading list">
          <span className="sr-only">Loading...</span>
          {Array.from({ length: lines }).map((_, i) => (
            <div
              key={i}
              className={`${baseClasses}`}
              style={{
                width: width || '100%',
                height: height || '60px',
              }}
            />
          ))}
        </div>
      )

    case 'table':
      return (
        <div className={`space-y-2 ${className}`} role="status" aria-label="Loading table">
          <span className="sr-only">Loading...</span>
          {Array.from({ length: lines }).map((_, i) => (
            <div key={i} className="flex gap-4">
              {Array.from({ length: 4 }).map((_, j) => (
                <div
                  key={j}
                  className={`${baseClasses} flex-1`}
                  style={{
                    height: height || '40px',
                  }}
                />
              ))}
            </div>
          ))}
        </div>
      )

    case 'circular':
      return (
        <div
          className={`${baseClasses} ${className}`}
          style={{
            width: width || '40px',
            height: height || '40px',
            borderRadius: '50%',
          }}
          aria-label="Loading"
          role="status"
        >
          <span className="sr-only">Loading...</span>
        </div>
      )

    default:
      return null
  }
}

interface PageSkeletonProps {
  header?: boolean
  sections?: number
  className?: string
}

export const PageSkeleton: React.FC<PageSkeletonProps> = ({
  header = true,
  sections = 3,
  className = '',
}) => {
  return (
    <div className={`min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {header && (
            <div className="space-y-2">
              <LoadingSkeleton variant="text" width="256px" height="32px" />
              <LoadingSkeleton variant="text" width="512px" height="16px" />
            </div>
          )}

          {Array.from({ length: sections }).map((_, i) => (
            <LoadingSkeleton key={i} variant="card" height="200px" />
          ))}
        </div>
      </div>
    </div>
  )
}

export default LoadingSkeleton


