import apiClient from './api'
import type { ApiError } from '@/types'

// Types
export type FileType = 'json' | 'csv'
export type UploadStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface DataUpload {
  upload_id: string
  user_id: string
  file_name: string
  file_size: number
  file_type: FileType
  status: UploadStatus
  validation_errors?: Record<string, any> | null
  created_at: string
  updated_at?: string | null
  processed_at?: string | null
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

// Constants
export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
export const ALLOWED_FILE_TYPES: FileType[] = ['json', 'csv']
export const ALLOWED_MIME_TYPES = {
  json: ['application/json', 'text/json'],
  csv: ['text/csv', 'application/csv', 'text/plain'],
}

/**
 * Validate file type based on extension and MIME type
 */
export function validateFileType(file: File): { valid: boolean; type?: FileType; error?: string } {
  const extension = file.name.toLowerCase().split('.').pop() as string
  const mimeType = file.type.toLowerCase()

  // Check extension
  if (!ALLOWED_FILE_TYPES.includes(extension as FileType)) {
    return {
      valid: false,
      error: `Unsupported file type. Allowed types: ${ALLOWED_FILE_TYPES.join(', ')}`,
    }
  }

  // Check MIME type if provided
  if (mimeType && !ALLOWED_MIME_TYPES[extension as FileType].includes(mimeType)) {
    // Warning only - still allow upload
    console.warn(`MIME type ${mimeType} does not match file extension ${extension}`)
  }

  return { valid: true, type: extension as FileType }
}

/**
 * Validate file size
 */
export function validateFileSize(file: File): { valid: boolean; error?: string } {
  if (file.size > MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `File size (${formatFileSize(file.size)}) exceeds maximum allowed size (${formatFileSize(MAX_FILE_SIZE)})`,
    }
  }

  if (file.size <= 0) {
    return {
      valid: false,
      error: 'File size must be greater than 0',
    }
  }

  return { valid: true }
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Upload a file to the backend
 */
export async function uploadFile(
  file: File,
  onProgress?: (progress: UploadProgress) => void
): Promise<DataUpload> {
  // Validate file type
  const typeValidation = validateFileType(file)
  if (!typeValidation.valid) {
    throw new Error(typeValidation.error || 'Invalid file type')
  }

  // Validate file size
  const sizeValidation = validateFileSize(file)
  if (!sizeValidation.valid) {
    throw new Error(sizeValidation.error || 'Invalid file size')
  }

  // Create FormData
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await apiClient.post<DataUpload>('/api/v1/data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const loaded = progressEvent.loaded
          const total = progressEvent.total
          onProgress({
            loaded,
            total,
            percentage: Math.round((loaded / total) * 100),
          })
        }
      },
    })

    return response.data
  } catch (error: any) {
    const apiError: ApiError = error.response?.data || { detail: error.message }
    throw new Error(typeof apiError.detail === 'string' ? apiError.detail : 'Upload failed')
  }
}

/**
 * Get upload status by upload ID
 */
export async function getUploadStatus(uploadId: string): Promise<DataUpload> {
  try {
    const response = await apiClient.get<DataUpload>(`/api/v1/data/upload/${uploadId}`)
    return response.data
  } catch (error: any) {
    const apiError: ApiError = error.response?.data || { detail: error.message }
    throw new Error(typeof apiError.detail === 'string' ? apiError.detail : 'Failed to get upload status')
  }
}

/**
 * Get upload history for current user
 */
export async function getUploadHistory(): Promise<DataUpload[]> {
  try {
    // Note: This endpoint doesn't exist yet, but we can prepare for it
    // For now, return empty array
    const response = await apiClient.get<DataUpload[]>('/api/v1/data/uploads')
    return response.data
  } catch (error: any) {
    // If endpoint doesn't exist, return empty array
    if (error.response?.status === 404) {
      return []
    }
    const apiError: ApiError = error.response?.data || { detail: error.message }
    throw new Error(typeof apiError.detail === 'string' ? apiError.detail : 'Failed to get upload history')
  }
}



