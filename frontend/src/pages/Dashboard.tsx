import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { dashboardService, type DashboardData } from '@/services/dashboardService'
import PersonaBadge from '@/components/PersonaBadge'
import BehavioralSignals from '@/components/BehavioralSignals'
import RecommendationsList from '@/components/RecommendationsList'
import ConsentStatusBadge from '@/components/ConsentStatusBadge'
import { FaUpload, FaSync, FaExclamationTriangle } from 'react-icons/fa'

const Dashboard = () => {
  const {
    data: dashboardData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: () => dashboardService.getDashboardData(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-6">
            {/* Header skeleton */}
            <div className="h-8 bg-gray-200 rounded w-64 animate-pulse"></div>

            {/* Persona skeleton */}
            <div className="h-32 bg-gray-200 rounded-lg animate-pulse"></div>

            {/* Consent skeleton */}
            <div className="h-24 bg-gray-200 rounded-lg animate-pulse"></div>

            {/* Signals skeleton */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-48 bg-gray-200 rounded-lg animate-pulse"></div>
              ))}
            </div>

            {/* Recommendations skeleton */}
            <div className="space-y-3">
              <div className="h-6 bg-gray-200 rounded w-48 animate-pulse"></div>
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 bg-gray-200 rounded-lg animate-pulse"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <FaExclamationTriangle className="mx-auto h-12 w-12 text-red-600 mb-4" />
            <h3 className="text-lg font-semibold text-red-900 mb-2">
              Failed to load dashboard
            </h3>
            <p className="text-sm text-red-700 mb-4">
              {error instanceof Error ? error.message : 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => refetch()}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
            >
              <FaSync className="h-4 w-4" />
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Empty state for new users
  if (!dashboardData?.behavioralProfile && dashboardData?.recommendations.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome to SpendSense!</h1>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Get started by uploading your transaction data to receive personalized financial
              recommendations.
            </p>

            {/* Consent Status */}
            {dashboardData && (
              <div className="max-w-2xl mx-auto mb-8">
                <ConsentStatusBadge consentStatus={dashboardData.consentStatus} />
              </div>
            )}

            {/* Empty state actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/upload"
                className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200 font-medium"
              >
                <FaUpload className="h-5 w-5" />
                Upload Transaction Data
              </Link>
              <Link
                to="/settings"
                className="inline-flex items-center gap-2 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 font-medium"
              >
                Manage Consent
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Main dashboard view
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">
            Your personalized financial insights and recommendations
          </p>
        </div>

        <div className="space-y-6">
          {/* Consent Status */}
          {dashboardData && (
            <ConsentStatusBadge consentStatus={dashboardData.consentStatus} />
          )}

          {/* Persona */}
          {dashboardData?.behavioralProfile && (
            <PersonaBadge
              personaId={dashboardData.behavioralProfile.persona_id}
              personaName={dashboardData.behavioralProfile.persona_name}
            />
          )}

          {/* Behavioral Signals */}
          {dashboardData?.behavioralProfile && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <BehavioralSignals
                signals30d={dashboardData.behavioralProfile.signals_30d}
                signals180d={dashboardData.behavioralProfile.signals_180d}
              />
            </div>
          )}

          {/* Recommendations */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            {dashboardData?.recommendations && (
              <RecommendationsList recommendations={dashboardData.recommendations} />
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              <Link
                to="/upload"
                className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors duration-200"
              >
                <FaUpload className="h-5 w-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Upload Data</p>
                  <p className="text-xs text-gray-500">Add transaction data</p>
                </div>
              </Link>
              <Link
                to="/profile"
                className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors duration-200"
              >
                <div className="h-5 w-5 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-xs font-medium text-primary-600">P</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">View Profile</p>
                  <p className="text-xs text-gray-500">See detailed insights</p>
                </div>
              </Link>
              <Link
                to="/recommendations"
                className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors duration-200"
              >
                <div className="h-5 w-5 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-xs font-medium text-primary-600">R</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">All Recommendations</p>
                  <p className="text-xs text-gray-500">View all recommendations</p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
