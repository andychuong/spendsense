import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { useQuery } from '@tanstack/react-query'
import { queryClient } from '@/utils/queryClient'
import { useAuthStore } from '@/store'
import Navigation from '@/components/Navigation'
import SkipLink from '@/components/SkipLink'
import { consentService } from '@/services/consentService'

// Pages (to be created in Task 10.2)
import Dashboard from '@/pages/Dashboard'
import Login from '@/pages/Login'
import Register from '@/pages/Register'
import Profile from '@/pages/Profile'
import Recommendations from '@/pages/Recommendations'
import RecommendationDetail from '@/pages/RecommendationDetail'
import Settings from '@/pages/Settings'
import Upload from '@/pages/Upload'
import Consent from '@/pages/Consent'
import OperatorDashboard from '@/pages/OperatorDashboard'
import OperatorReview from '@/pages/OperatorReview'
import ReviewQueueList from '@/pages/ReviewQueueList'
import OperatorAnalytics from '@/pages/OperatorAnalytics'
import UserDetail from '@/pages/UserDetail'

// Protected Route Component (checks authentication)
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Consent Route Component (checks consent status)
const ConsentRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()

  // Check authentication first
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Check consent status
  const { data: consentStatus, isLoading } = useQuery({
    queryKey: ['consentStatus'],
    queryFn: () => consentService.getConsentStatus(),
    enabled: isAuthenticated,
  })

  // Show loading while checking consent
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  // Redirect to consent page if consent not granted
  if (consentStatus && !consentStatus.consent_status) {
    return <Navigate to="/consent" replace />
  }

  return <>{children}</>
}

// Operator Route Component
const OperatorRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, user } = useAuthStore()
  const isOperator = user?.role === 'operator' || user?.role === 'admin'

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!isOperator) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <SkipLink href="#main-content" />
        <Navigation />
        <main id="main-content" tabIndex={-1}>
          <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Consent Page (public but requires auth) */}
          <Route
            path="/consent"
            element={
              <ProtectedRoute>
                <Consent />
              </ProtectedRoute>
            }
          />

          {/* Protected Routes (require consent) */}
          <Route
            path="/"
            element={
              <ConsentRoute>
                <Dashboard />
              </ConsentRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ConsentRoute>
                <Profile />
              </ConsentRoute>
            }
          />
          <Route
            path="/recommendations"
            element={
              <ConsentRoute>
                <Recommendations />
              </ConsentRoute>
            }
          />
          <Route
            path="/recommendations/:id"
            element={
              <ConsentRoute>
                <RecommendationDetail />
              </ConsentRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <ConsentRoute>
                <Upload />
              </ConsentRoute>
            }
          />

          {/* Operator Routes */}
          <Route
            path="/operator"
            element={
              <OperatorRoute>
                <OperatorDashboard />
              </OperatorRoute>
            }
          />
          <Route
            path="/operator/review"
            element={
              <OperatorRoute>
                <ReviewQueueList />
              </OperatorRoute>
            }
          />
          <Route
            path="/operator/review/:id"
            element={
              <OperatorRoute>
                <OperatorReview />
              </OperatorRoute>
            }
          />
          <Route
            path="/operator/analytics"
            element={
              <OperatorRoute>
                <OperatorAnalytics />
              </OperatorRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin/users/:userId"
            element={
              <OperatorRoute>
                <UserDetail />
              </OperatorRoute>
            }
          />

          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </main>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

