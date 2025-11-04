import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/utils/queryClient'
import { useAuthStore } from '@/store'

// Pages (to be created in Task 10.2)
import Dashboard from '@/pages/Dashboard'
import Login from '@/pages/Login'
import Register from '@/pages/Register'
import Profile from '@/pages/Profile'
import Recommendations from '@/pages/Recommendations'
import RecommendationDetail from '@/pages/RecommendationDetail'
import Settings from '@/pages/Settings'
import Upload from '@/pages/Upload'
import OperatorDashboard from '@/pages/OperatorDashboard'
import OperatorReview from '@/pages/OperatorReview'
import OperatorAnalytics from '@/pages/OperatorAnalytics'

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
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
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recommendations"
            element={
              <ProtectedRoute>
                <Recommendations />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recommendations/:id"
            element={
              <ProtectedRoute>
                <RecommendationDetail />
              </ProtectedRoute>
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
              <ProtectedRoute>
                <Upload />
              </ProtectedRoute>
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
          
          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

