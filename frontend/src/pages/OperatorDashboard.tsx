import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { operatorService, type SystemAnalytics } from '@/services/operatorService'
import { adminService } from '@/services/adminService'
import ReviewQueue from '@/components/ReviewQueue'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import { FaUsers, FaChartBar, FaClipboardCheck, FaClock, FaCheckCircle, FaTimesCircle, FaSpinner } from 'react-icons/fa'
import { useAuthStore } from '@/store/authStore'

const OperatorDashboard = () => {
  const { user } = useAuthStore()
  const isAdmin = user?.role === 'admin'

  // Fetch analytics
  const {
    data: analytics,
    isLoading: isLoadingAnalytics,
    isError: isErrorAnalytics,
    error: analyticsError,
    refetch: refetchAnalytics,
  } = useQuery<SystemAnalytics>({
    queryKey: ['operator', 'analytics'],
    queryFn: () => operatorService.getAnalytics(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Fetch user count (admin only)
  const {
    data: usersData,
    isLoading: isLoadingUsers,
  } = useQuery({
    queryKey: ['admin', 'users', 'count'],
    queryFn: () => adminService.getAllUsers(0, 1),
    enabled: isAdmin,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Loading state
  if (isLoadingAnalytics) {
    return <PageSkeleton sections={4} />
  }

  // Error state
  if (isErrorAnalytics) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorState
            title="Failed to load dashboard"
            error={analyticsError}
            onRetry={() => refetchAnalytics()}
            retryLabel="Retry"
          />
        </div>
      </div>
    )
  }

  const stats = analytics || {
    coverage: { users_with_persona: 0, users_with_persona_percent: 0 },
    explainability: { recommendations_with_rationales_percent: 0 },
    performance: { p95_latency_ms: 0 },
    engagement: { total_users: 0, active_users: 0 },
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-6 lg:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
            Operator Dashboard
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Platform management and user oversight
          </p>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Total Users */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {isLoadingUsers ? (
                    <FaSpinner className="animate-spin h-6 w-6 text-gray-400" />
                  ) : (
                    usersData?.total?.toLocaleString() || stats.engagement.total_users.toLocaleString()
                  )}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <FaUsers className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Active Users */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.engagement.active_users.toLocaleString()}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <FaCheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          {/* Users with Persona */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Users with Persona</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.coverage.users_with_persona_percent.toFixed(0)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {stats.coverage.users_with_persona} users
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <FaChartBar className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>

          {/* Explainability */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Rationales Coverage</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.explainability.recommendations_with_rationales_percent.toFixed(0)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Recommendations with rationales
                </p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <FaClipboardCheck className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            <Link
              to="/operator/review"
              className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors"
            >
              <FaClipboardCheck className="h-5 w-5 text-primary-600" />
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
            {isAdmin && (
              <Link
                to="/admin/management"
                className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors"
              >
                <FaUsers className="h-5 w-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">User Management</p>
                  <p className="text-xs text-gray-500">Manage users & staff</p>
                </div>
              </Link>
            )}
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Review Queue */}
          <div>
            <ReviewQueue limit={10} />
          </div>

          {/* System Metrics */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">System Metrics</h2>
            <div className="space-y-4">
              {/* Performance */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Performance (p95 latency)</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {stats.performance.p95_latency_ms > 0
                      ? `${(stats.performance.p95_latency_ms / 1000).toFixed(2)}s`
                      : 'N/A'}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      stats.performance.p95_latency_ms < 5000
                        ? 'bg-green-500'
                        : stats.performance.p95_latency_ms < 10000
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{
                      width: `${Math.min(
                        (stats.performance.p95_latency_ms / 10000) * 100,
                        100
                      )}%`,
                    }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Target: &lt;5s ({stats.performance.recommendations_within_target_percent?.toFixed(0) || 0}% within target)
                </p>
              </div>

              {/* Coverage Metrics */}
              <div className="pt-4 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Coverage</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-600">Users with behaviors</span>
                    <span className="text-xs font-semibold text-gray-900">
                      {stats.coverage.users_with_behaviors_percent?.toFixed(0) || 0}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-600">Users with both</span>
                    <span className="text-xs font-semibold text-gray-900">
                      {stats.coverage.users_with_both_percent?.toFixed(0) || 0}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Engagement Metrics */}
              <div className="pt-4 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Engagement</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-600">Recommendations sent</span>
                    <span className="text-xs font-semibold text-gray-900">
                      {stats.engagement.recommendations_sent?.toLocaleString() || '0'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-600">Recommendations viewed</span>
                    <span className="text-xs font-semibold text-gray-900">
                      {stats.engagement.recommendations_viewed?.toLocaleString() || '0'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-600">Recommendations actioned</span>
                    <span className="text-xs font-semibold text-gray-900">
                      {stats.engagement.recommendations_actioned?.toLocaleString() || '0'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OperatorDashboard
