import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { dashboardService, type DashboardData } from '@/services/dashboardService'
import PersonaBadge from '@/components/PersonaBadge'
import BehavioralSignals from '@/components/BehavioralSignals'
import RecommendationsList from '@/components/RecommendationsList'
import UsersList from '@/components/UsersList'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import EmptyState from '@/components/EmptyState'
import { FaUpload, FaUsers, FaChartBar, FaCog } from 'react-icons/fa'
import { useAuthStore } from '@/store/authStore'

const Dashboard = () => {
  const { user } = useAuthStore()
  const isAdmin = user?.role === 'admin'
  const isOperator = user?.role === 'operator' || user?.role === 'admin'
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
    return <PageSkeleton sections={4} />
  }

  // Error state
  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorState
            title="Failed to load dashboard"
            error={error}
            onRetry={() => refetch()}
            retryLabel="Retry"
          />
        </div>
      </div>
    )
  }

  // Empty state for new users (but not for admins/operators - they should see admin dashboard)
  if (!isAdmin && !isOperator && !dashboardData?.behavioralProfile && dashboardData?.recommendations.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <header className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to SpendSense!</h1>
          </header>

          <EmptyState
            title="Get Started"
            description="Upload your transaction data to receive personalized financial recommendations tailored to your spending behavior."
            action={{
              label: 'Upload Transaction Data',
              to: '/upload',
              icon: <FaUpload className="h-5 w-5" aria-hidden="true" />,
            }}
            secondaryAction={{
              label: 'Manage Consent',
              to: '/settings',
            }}
          />
        </div>
      </div>
    )
  }

  // Main dashboard view
  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-6 lg:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
            {isAdmin ? 'Admin Dashboard' : isOperator ? 'Operator Dashboard' : 'Dashboard'}
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            {isAdmin
              ? 'System-wide insights and user management'
              : isOperator
              ? 'Platform management and user oversight'
              : 'Your personalized financial insights and recommendations'
            }
          </p>
        </header>

        {/* Admin/Operator Dashboard */}
        {(isAdmin || isOperator) && (
          <div className="space-y-6">
            {/* System Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <Link
                to="/operator"
                className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <FaUsers className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Operator Dashboard</p>
                    <p className="text-sm font-medium text-gray-900">View Dashboard</p>
                  </div>
                </div>
              </Link>

              <Link
                to="/operator/review"
                className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <FaChartBar className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Review Queue</p>
                    <p className="text-sm font-medium text-gray-900">Approve/Reject</p>
                  </div>
                </div>
              </Link>

              <Link
                to="/operator/analytics"
                className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-orange-100 rounded-lg">
                    <FaChartBar className="h-6 w-6 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Analytics</p>
                    <p className="text-sm font-medium text-gray-900">View Reports</p>
                  </div>
                </div>
              </Link>
            </div>

            {/* Quick Actions for Admin/Operator */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                <Link
                  to="/operator"
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors"
                >
                  <FaUsers className="h-5 w-5 text-primary-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Operator Dashboard</p>
                    <p className="text-xs text-gray-500">View full dashboard</p>
                  </div>
                </Link>
                <Link
                  to="/operator/review"
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors"
                >
                  <FaChartBar className="h-5 w-5 text-primary-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Review Queue</p>
                    <p className="text-xs text-gray-500">Approve/reject recommendations</p>
                  </div>
                </Link>
                <Link
                  to="/operator/analytics"
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors"
                >
                  <FaChartBar className="h-5 w-5 text-primary-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Analytics</p>
                    <p className="text-xs text-gray-500">System metrics & reports</p>
                  </div>
                </Link>
              </div>
            </div>

            {/* Personal Data Section (if admin has uploaded data) */}
            {dashboardData?.behavioralProfile && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Personal Data</h3>
                <PersonaBadge
                  personaId={dashboardData.behavioralProfile.persona_id}
                  personaName={dashboardData.behavioralProfile.persona_name}
                />
                <div className="mt-4">
                  <BehavioralSignals
                    signals30d={dashboardData.behavioralProfile.signals_30d}
                    signals180d={dashboardData.behavioralProfile.signals_180d}
                  />
                </div>
              </div>
            )}

            {/* Users List - Admin Only */}
            {isAdmin && (
              <div>
                <UsersList limit={100} />
              </div>
            )}
          </div>
        )}

        {/* Regular User Dashboard */}
        {!isAdmin && !isOperator && (
          <div className="space-y-6">
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
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  aria-label="Upload transaction data"
                >
                  <FaUpload className="h-5 w-5 text-primary-600" aria-hidden="true" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Upload Data</p>
                    <p className="text-xs text-gray-500">Add transaction data</p>
                  </div>
                </Link>
                <Link
                  to="/profile"
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  aria-label="View profile and detailed insights"
                >
                  <div className="h-5 w-5 rounded-full bg-primary-100 flex items-center justify-center" aria-hidden="true">
                    <span className="text-xs font-medium text-primary-600">P</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">View Profile</p>
                    <p className="text-xs text-gray-500">See detailed insights</p>
                  </div>
                </Link>
                <Link
                  to="/recommendations"
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  aria-label="View all recommendations"
                >
                  <div className="h-5 w-5 rounded-full bg-primary-100 flex items-center justify-center" aria-hidden="true">
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
        )}
      </div>
    </div>
  )
}

export default Dashboard
