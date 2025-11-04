import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import FileUpload from '@/components/FileUpload'
import {
  getUploadHistory,
  formatFileSize,
  type DataUpload,
} from '@/services/dataUploadService'

const Upload = () => {
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Fetch upload history
  const {
    data: uploadHistory = [],
    isLoading,
    error,
    refetch,
  } = useQuery<DataUpload[]>({
    queryKey: ['uploadHistory'],
    queryFn: getUploadHistory,
    retry: false, // Don't retry if endpoint doesn't exist
  })

  const handleUploadSuccess = (upload: DataUpload) => {
    setSuccessMessage(`File "${upload.file_name}" uploaded successfully!`)
    // Refetch upload history if endpoint exists
    refetch()
    // Clear success message after 5 seconds
    setTimeout(() => {
      setSuccessMessage(null)
    }, 5000)
  }

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error)
    // Error is already displayed in FileUpload component
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
      case 'processing':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
      case 'pending':
      default:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6 lg:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            Upload Transaction Data
          </h1>
          <p className="text-sm text-gray-600">
            Upload your Plaid-style transaction data in JSON or CSV format to get personalized
            financial recommendations.
          </p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
            <div className="flex items-center">
              <svg
                className="w-5 h-5 text-green-600 dark:text-green-400 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-sm font-medium text-green-800 dark:text-green-300">
                {successMessage}
              </p>
            </div>
          </div>
        )}

        {/* File Upload Component */}
        <div className="mb-8">
          <FileUpload onUploadSuccess={handleUploadSuccess} onUploadError={handleUploadError} />
        </div>

        {/* Upload History */}
        <div className="mt-12">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Upload History
          </h2>

        {isLoading && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="animate-pulse bg-gray-200 dark:bg-gray-700 rounded-lg h-20"
              ></div>
            ))}
          </div>
        )}

        {error && (
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
            <p className="text-sm text-yellow-800 dark:text-yellow-300">
              Upload history is not available at this time. Your uploads are still being processed.
            </p>
          </div>
        )}

        {!isLoading && !error && uploadHistory.length === 0 && (
          <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <svg
              className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-gray-600 dark:text-gray-400 mb-2">No uploads yet</p>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              Upload your first file to get started with personalized recommendations.
            </p>
          </div>
        )}

        {!isLoading && !error && uploadHistory.length > 0 && (
          <div className="space-y-4">
            {uploadHistory.map((upload) => (
              <div
                key={upload.upload_id}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1">
                    {/* File Icon */}
                    <div className="flex-shrink-0">
                      <svg
                        className="w-8 h-8 text-gray-400 dark:text-gray-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                    </div>

                    {/* File Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {upload.file_name}
                        </p>
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(
                            upload.status
                          )}`}
                        >
                          {upload.status.charAt(0).toUpperCase() + upload.status.slice(1)}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>{formatFileSize(upload.file_size)}</span>
                        <span className="uppercase">{upload.file_type}</span>
                        <span>{formatDate(upload.created_at)}</span>
                        {upload.processed_at && (
                          <span>Processed: {formatDate(upload.processed_at)}</span>
                        )}
                      </div>
                      {upload.validation_errors &&
                       typeof upload.validation_errors === 'object' &&
                       'errors' in upload.validation_errors &&
                       Array.isArray(upload.validation_errors.errors) &&
                       upload.validation_errors.errors.length > 0 && (
                        <div className="mt-2 text-xs text-red-600 dark:text-red-400">
                          Validation errors detected ({upload.validation_errors.errors.length})
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        </div>
      </div>
    </div>
  )
}

export default Upload
