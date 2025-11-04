// Validation utilities

export interface ValidationError {
  field: string
  message: string
}

// Email validation
export function validateEmail(email: string): ValidationError | null {
  if (!email) {
    return { field: 'email', message: 'Email is required' }
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    return { field: 'email', message: 'Please enter a valid email address' }
  }

  return null
}

// Password validation (matches backend requirements)
export function validatePassword(password: string): ValidationError | null {
  if (!password) {
    return { field: 'password', message: 'Password is required' }
  }

  if (password.length < 12) {
    return { field: 'password', message: 'Password must be at least 12 characters long' }
  }

  if (!/[A-Z]/.test(password)) {
    return { field: 'password', message: 'Password must contain at least one uppercase letter' }
  }

  if (!/[a-z]/.test(password)) {
    return { field: 'password', message: 'Password must contain at least one lowercase letter' }
  }

  if (!/\d/.test(password)) {
    return { field: 'password', message: 'Password must contain at least one digit' }
  }

  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    return { field: 'password', message: 'Password must contain at least one special character' }
  }

  return null
}

// Phone validation (E.164 format)
export function validatePhone(phone: string): ValidationError | null {
  if (!phone) {
    return { field: 'phone', message: 'Phone number is required' }
  }

  // E.164 format: + followed by 1-15 digits
  const phoneRegex = /^\+[1-9]\d{1,14}$/
  if (!phoneRegex.test(phone)) {
    return {
      field: 'phone',
      message: 'Please enter a valid phone number in E.164 format (e.g., +1234567890)',
    }
  }

  return null
}

// Verification code validation (6 digits)
export function validateVerificationCode(code: string): ValidationError | null {
  if (!code) {
    return { field: 'code', message: 'Verification code is required' }
  }

  if (code.length !== 6) {
    return { field: 'code', message: 'Verification code must be 6 digits' }
  }

  if (!/^\d{6}$/.test(code)) {
    return { field: 'code', message: 'Verification code must contain only digits' }
  }

  return null
}

// Format phone number for display (adds + if missing)
export function formatPhoneNumber(phone: string): string {
  if (!phone) return ''
  return phone.startsWith('+') ? phone : `+${phone}`
}
