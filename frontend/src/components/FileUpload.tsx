import { useState, useCallback, useRef, DragEvent } from 'react'
import {
  uploadFile,
  validateFileType,
  validateFileSize,
  formatFileSize,
  MAX_FILE_SIZE,
  ALLOWED_FILE_TYPES,
  type UploadProgress,
  type DataUpload,
} from '@/services/dataUploadService'

interface FileUploadProps {
  onUploadSuccess?: (upload: DataUpload) => void
  onUploadError?: (error: string) => void
  className?: string
}

export default function FileUpload({
  onUploadSuccess,
  onUploadError,
  className = '',
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragEnter = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const processFile = useCallback(
    async (file: File) => {
      setError(null)
      setSelectedFile(file)

      // Validate file type
      const typeValidation = validateFileType(file)
      if (!typeValidation.valid) {
        const errorMsg = typeValidation.error || 'Invalid file type'
        setError(errorMsg)
        onUploadError?.(errorMsg)
        return
      }

      // Validate file size
      const sizeValidation = validateFileSize(file)
      if (!sizeValidation.valid) {
        const errorMsg = sizeValidation.error || 'Invalid file size'
        setError(errorMsg)
        onUploadError?.(errorMsg)
        return
      }

      // Upload file
      setIsUploading(true)
      setUploadProgress({ loaded: 0, total: file.size, percentage: 0 })

      try {
        const upload = await uploadFile(file, (progress) => {
          setUploadProgress(progress)
        })

        setUploadProgress(null)
        setIsUploading(false)
        setSelectedFile(null)
        onUploadSuccess?.(upload)
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Upload failed'
        setError(errorMsg)
        setIsUploading(false)
        setUploadProgress(null)
        onUploadError?.(errorMsg)
      }
    },
    [onUploadSuccess, onUploadError]
  )

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        processFile(files[0])
      }
    },
    [processFile]
  )

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files && files.length > 0) {
        processFile(files[0])
      }
    },
    [processFile]
  )

  const handleBrowseClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const handleReset = useCallback(() => {
    setError(null)
    setSelectedFile(null)
    setUploadProgress(null)
    setIsUploading(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }, [])

  return (
    <div className={className}>
      {/* File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".json,.csv,application/json,text/csv"
        onChange={handleFileSelect}
        className="hidden"
        disabled={isUploading}
      />

      {/* Drag and Drop Area */}
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${
            isDragging
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/50'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          ${error ? 'border-red-300 dark:border-red-600' : ''}
        `}
        onClick={!isUploading ? handleBrowseClick : undefined}
      >
        {isUploading ? (
          <div className="space-y-4">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
            {uploadProgress && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Uploading... {uploadProgress.percentage}%
                </p>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress.percentage}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {formatFileSize(uploadProgress.loaded)} / {formatFileSize(uploadProgress.total)}
                </p>
              </div>
            )}
            {selectedFile && (
              <p className="text-sm text-gray-600 dark:text-gray-400">{selectedFile.name}</p>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {/* Icon */}
            <div className="flex justify-center">
              <svg
                className="w-16 h-16 text-gray-400 dark:text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>

            {/* Instructions */}
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
                Drag and drop your file here
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">or</p>
              <button
                type="button"
                onClick={handleBrowseClick}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Browse Files
              </button>
            </div>

            {/* File Format Info */}
            <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
              <p>Supported formats: {ALLOWED_FILE_TYPES.join(', ').toUpperCase()}</p>
              <p>Maximum file size: {formatFileSize(MAX_FILE_SIZE)}</p>
            </div>

            {/* Selected File Info */}
            {selectedFile && (
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <svg
                      className="w-5 h-5 text-blue-600 dark:text-blue-400"
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
                    <div className="text-left">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {selectedFile.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {formatFileSize(selectedFile.size)}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleReset}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-red-800 dark:text-red-300">Upload Error</p>
              <p className="text-sm text-red-600 dark:text-red-400 mt-1">{error}</p>
            </div>
            <button
              type="button"
              onClick={handleReset}
              className="text-red-400 hover:text-red-600 dark:hover:text-red-300"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}



