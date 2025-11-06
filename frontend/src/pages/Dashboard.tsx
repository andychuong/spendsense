import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { dashboardService, type DashboardData, type SpendingData } from '@/services/dashboardService'
import BehavioralSignals from '@/components/BehavioralSignals'
import SpendingBreakdown from '@/components/SpendingBreakdown'
import IncomeAnalysis from '@/components/IncomeAnalysis'
import RecommendationsList from '@/components/RecommendationsList'
import UsersList from '@/components/UsersList'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import EmptyState from '@/components/EmptyState'
import { FaUpload, FaUsers, FaChartBar, FaCog, FaChevronUp, FaChevronDown, FaList } from 'react-icons/fa'
import { useAuthStore } from '@/store/authStore'

const Dashboard = () => {
  const { user } = useAuthStore()
  const isAdmin = user?.role === 'admin'
  const isOperator = user?.role === 'operator' || user?.role === 'admin'
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['financialMetrics', 'income', 'recommendations', 'transactions', 'transactionSpendingBreakdown'])
  )
  const [transactionsPage, setTransactionsPage] = useState(0)
  const transactionsPerPage = 20
  const [sortBy, setSortBy] = useState<'date' | 'merchant' | 'category' | 'amount'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }
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

  // Fetch transactions for regular users
  const {
    data: transactionsData,
    isLoading: transactionsLoading,
    isError: transactionsError,
  } = useQuery({
    queryKey: ['dashboard', 'transactions', dashboardData?.profile.user_id, transactionsPage],
    queryFn: () => dashboardService.getUserTransactions(
      dashboardData!.profile.user_id,
      transactionsPage * transactionsPerPage,
      transactionsPerPage
    ),
    enabled: !!dashboardData?.profile.user_id && !isAdmin && !isOperator,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Fetch spending categories for regular users
  const {
    data: spendingData,
    isLoading: spendingLoading,
    isError: spendingError,
  } = useQuery<SpendingData>({
    queryKey: ['dashboard', 'spending', dashboardData?.profile.user_id],
    queryFn: () => dashboardService.getSpendingCategories(dashboardData!.profile.user_id),
    enabled: !!dashboardData?.profile.user_id && !isAdmin && !isOperator,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)
  }

  const getCategoryColor = (category: string): string => {
    const categoryColors: Record<string, string> = {
      // Food & Dining (Red)
      'Food & Dining': '#ef4444',
      'Food and Drink': '#ef4444',
      'Food & Drink': '#ef4444',
      'Restaurants': '#ef4444',
      'Fast Food': '#ef4444',
      'Coffee Shops': '#ef4444',
      'Bars': '#ef4444',
      'Food Delivery': '#ef4444',
      'Dining': '#ef4444',
      
      // Groceries (Orange)
      'Groceries': '#f97316',
      'Supermarkets and Groceries': '#f97316',
      
      // Transportation (Amber)
      'Transportation': '#f59e0b',
      'Transport': '#f59e0b',
      'Gas Stations': '#f59e0b',
      'Parking': '#f59e0b',
      'Public Transportation': '#f59e0b',
      'Ride Sharing': '#f59e0b',
      'Auto & Transport': '#f59e0b',
      
      // Shopping (Yellow)
      'Shopping': '#eab308',
      'General Merchandise': '#eab308',
      'Clothing and Apparel': '#eab308',
      'Electronics and Software': '#eab308',
      'Home Improvement': '#eab308',
      'Online Marketplaces': '#eab308',
      'Retail': '#eab308',
      
      // Bills & Utilities (Lime)
      'Bills & Utilities': '#84cc16',
      'Internet': '#84cc16',
      'Mobile Phone': '#84cc16',
      'Utilities': '#84cc16',
      'Cable': '#84cc16',
      
      // Entertainment (Green)
      'Entertainment': '#22c55e',
      'Movies & Music': '#22c55e',
      'Sports and Recreation': '#22c55e',
      'Arts and Entertainment': '#22c55e',
      
      // Healthcare (Emerald)
      'Healthcare': '#10b981',
      'Medical': '#10b981',
      'Pharmacies': '#10b981',
      
      // Travel (Teal)
      'Travel': '#14b8a6',
      'Airlines and Aviation Services': '#14b8a6',
      'Hotels and Accommodations': '#14b8a6',
      
      // Personal Care (Cyan)
      'Personal Care': '#06b6d4',
      'Gyms and Fitness Centers': '#06b6d4',
      'Hair Salons and Barbers': '#06b6d4',
      
      // Financial (Sky)
      'Financial': '#0ea5e9',
      'Bank Fees': '#0ea5e9',
      'ATM Fees': '#0ea5e9',
      'Wire Transfer': '#0ea5e9',
      'Credit Card': '#0ea5e9',
      'Loan Payment': '#0ea5e9',
    }
    return categoryColors[category] || '#6b7280'
  }

  const handleSort = (column: 'date' | 'merchant' | 'category' | 'amount') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('asc')
    }
  }

  const sortedTransactions = transactionsData?.items ? [...transactionsData.items].sort((a, b) => {
    let comparison = 0
    
    switch (sortBy) {
      case 'date':
        comparison = new Date(a.date).getTime() - new Date(b.date).getTime()
        break
      case 'merchant':
        comparison = (a.merchant_name || '').localeCompare(b.merchant_name || '')
        break
      case 'category':
        comparison = (a.category_primary || '').localeCompare(b.category_primary || '')
        break
      case 'amount':
        comparison = Math.abs(a.amount) - Math.abs(b.amount)
        break
    }
    
    return sortOrder === 'asc' ? comparison : -comparison
  }) : []

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
              <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <button
                  onClick={() => toggleSection('adminBehavioralSignals')}
                  className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                  aria-expanded={expandedSections.has('adminBehavioralSignals')}
                  aria-controls="admin-behavioral-signals-content"
                >
                  <h3 className="text-lg font-semibold text-gray-900">Your Personal Data</h3>
                  {expandedSections.has('adminBehavioralSignals') ? (
                    <FaChevronUp className="h-5 w-5 text-gray-400" />
                  ) : (
                    <FaChevronDown className="h-5 w-5 text-gray-400" />
                  )}
                </button>
                <div
                  id="admin-behavioral-signals-content"
                  className={`transition-all duration-300 ease-in-out ${
                    expandedSections.has('adminBehavioralSignals') ? 'max-h-[5000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
                  }`}
                >
                  <div className="px-6 pb-6">
                    <BehavioralSignals
                      signals30d={dashboardData.behavioralProfile.signals_30d}
                      signals180d={dashboardData.behavioralProfile.signals_180d}
                      showTitle={false}
                    />
                  </div>
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
            {/* Financial Metrics */}
            {dashboardData?.behavioralProfile && (
              <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <button
                  onClick={() => toggleSection('financialMetrics')}
                  className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                  aria-expanded={expandedSections.has('financialMetrics')}
                  aria-controls="financial-metrics-content"
                >
                  <h2 className="text-lg font-semibold text-gray-900">Financial Metrics</h2>
                  {expandedSections.has('financialMetrics') ? (
                    <FaChevronUp className="h-5 w-5 text-gray-400" />
                  ) : (
                    <FaChevronDown className="h-5 w-5 text-gray-400" />
                  )}
                </button>
                <div
                  id="financial-metrics-content"
                  className={`transition-all duration-300 ease-in-out ${
                    expandedSections.has('financialMetrics') ? 'max-h-[5000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
                  }`}
                >
                  <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {/* Subscriptions */}
                      <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Subscriptions</h3>
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-600">Monthly Spend</span>
                            <span className="text-lg font-bold text-gray-900">
                              {formatCurrency(dashboardData.behavioralProfile.signals_30d?.subscriptions?.total_recurring_spend ?? 0)}
                            </span>
                          </div>
                          <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="absolute h-full bg-blue-500 rounded-full transition-all"
                              style={{ 
                                width: `${Math.min(100, ((dashboardData.behavioralProfile.signals_30d?.subscriptions?.total_recurring_spend ?? 0) / (dashboardData.behavioralProfile.signals_30d?.subscriptions?.total_spend ?? 1)) * 100)}%` 
                              }}
                            />
                          </div>
                          <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>30d: {formatCurrency(dashboardData.behavioralProfile.signals_30d?.subscriptions?.total_recurring_spend ?? 0)}</span>
                            <span>180d: {formatCurrency(dashboardData.behavioralProfile.signals_180d?.subscriptions?.total_recurring_spend ?? 0)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Savings */}
                      <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Savings</h3>
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-600">Net Inflow</span>
                            <span className="text-lg font-bold text-gray-900">
                              {formatCurrency(dashboardData.behavioralProfile.signals_30d?.savings?.net_inflow?.net_inflow ?? 0)}
                            </span>
                          </div>
                          <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="absolute h-full bg-green-500 rounded-full transition-all"
                              style={{ 
                                width: `${Math.min(100, Math.abs((dashboardData.behavioralProfile.signals_30d?.savings?.net_inflow?.net_inflow ?? 0) / 1000) * 100)}%` 
                              }}
                            />
                          </div>
                          <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>30d: {formatCurrency(dashboardData.behavioralProfile.signals_30d?.savings?.net_inflow?.net_inflow ?? 0)}</span>
                            <span>180d: {formatCurrency(dashboardData.behavioralProfile.signals_180d?.savings?.net_inflow?.net_inflow ?? 0)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Credit */}
                      <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Credit</h3>
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-600">Utilization</span>
                            <span className="text-lg font-bold text-gray-900">
                              {(dashboardData.behavioralProfile.signals_30d?.credit?.total_utilization ?? 0).toFixed(1)}%
                            </span>
                          </div>
                          <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="absolute h-full bg-red-500 rounded-full transition-all"
                              style={{ 
                                width: `${Math.min(100, dashboardData.behavioralProfile.signals_30d?.credit?.total_utilization ?? 0)}%` 
                              }}
                            />
                          </div>
                          <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>30d: {(dashboardData.behavioralProfile.signals_30d?.credit?.total_utilization ?? 0).toFixed(1)}%</span>
                            <span>180d: {(dashboardData.behavioralProfile.signals_180d?.credit?.total_utilization ?? 0).toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Income */}
            {dashboardData?.behavioralProfile?.signals_180d?.income && (
              <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <button
                  onClick={() => toggleSection('income')}
                  className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                  aria-expanded={expandedSections.has('income')}
                  aria-controls="income-content"
                >
                  <h2 className="text-lg font-semibold text-gray-900">Income</h2>
                  {expandedSections.has('income') ? (
                    <FaChevronUp className="h-5 w-5 text-gray-400" />
                  ) : (
                    <FaChevronDown className="h-5 w-5 text-gray-400" />
                  )}
                </button>
                <div
                  id="income-content"
                  className={`transition-all duration-300 ease-in-out ${
                    expandedSections.has('income') ? 'max-h-[5000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
                  }`}
                >
                  <div className="p-6">
                    <IncomeAnalysis
                      signals={dashboardData.behavioralProfile.signals_180d.income}
                      period="180 days"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <button
                onClick={() => toggleSection('recommendations')}
                className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                aria-expanded={expandedSections.has('recommendations')}
                aria-controls="recommendations-content"
              >
                <div className="flex items-center gap-3">
                  <h2 className="text-lg font-semibold text-gray-900">Recommendations</h2>
                  {dashboardData?.recommendations && dashboardData.recommendations.length > 0 && (
                    <span className="text-sm text-gray-500">
                      ({dashboardData.recommendations.length})
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {dashboardData?.recommendations && dashboardData.recommendations.length > 0 && (
                    <Link
                      to="/recommendations"
                      onClick={(e) => e.stopPropagation()}
                      className="text-sm text-primary-600 hover:text-primary-700 font-medium cursor-pointer"
                    >
                      View all
                    </Link>
                  )}
                  {expandedSections.has('recommendations') ? (
                    <FaChevronUp className="h-5 w-5 text-gray-400" />
                  ) : (
                    <FaChevronDown className="h-5 w-5 text-gray-400" />
                  )}
                </div>
              </button>
              <div
                id="recommendations-content"
                className={`transition-all duration-300 ease-in-out ${
                  expandedSections.has('recommendations') ? 'max-h-[5000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
                }`}
              >
                <div className="px-6 pb-6">
                  {dashboardData?.recommendations && (
                    <RecommendationsList recommendations={dashboardData.recommendations} showHeader={false} />
                  )}
                </div>
              </div>
            </div>

            {/* Recent Transactions */}
            {dashboardData?.profile.user_id && (
              <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <button
                  onClick={() => toggleSection('transactions')}
                  className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                  aria-expanded={expandedSections.has('transactions')}
                  aria-controls="transactions-content"
                >
                  <div className="flex items-center gap-2">
                    <FaList className="h-5 w-5 text-primary-600" />
                    <h2 className="text-lg font-semibold text-gray-900">
                      Recent Transactions {transactionsData ? `(${transactionsData.total})` : ''}
                    </h2>
                  </div>
                  {expandedSections.has('transactions') ? (
                    <FaChevronUp className="h-5 w-5 text-gray-400" />
                  ) : (
                    <FaChevronDown className="h-5 w-5 text-gray-400" />
                  )}
                </button>
                <div
                  id="transactions-content"
                  className={`transition-all duration-300 ease-in-out ${
                    expandedSections.has('transactions') ? 'max-h-[5000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
                  }`}
                >
                  <div className="px-6 pb-6">
                    {transactionsError ? (
                      <ErrorState title="Failed to load transactions" error={transactionsError} />
                    ) : transactionsLoading ? (
                      <div className="text-center py-8">
                        <p className="text-gray-500 text-sm">Loading transactions...</p>
                      </div>
                    ) : transactionsData && transactionsData.items.length > 0 ? (
                      <>
                        {/* Spending Breakdown Collapsible */}
                        <div className="mb-4 border-b border-gray-200">
                          <button
                            onClick={() => toggleSection('transactionSpendingBreakdown')}
                            className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                            aria-expanded={expandedSections.has('transactionSpendingBreakdown')}
                            aria-controls="transaction-spending-breakdown-content"
                          >
                            <h3 className="text-md font-semibold text-gray-900">Spending Breakdown</h3>
                            {expandedSections.has('transactionSpendingBreakdown') ? (
                              <FaChevronUp className="h-4 w-4 text-gray-400" />
                            ) : (
                              <FaChevronDown className="h-4 w-4 text-gray-400" />
                            )}
                          </button>
                          <div
                            id="transaction-spending-breakdown-content"
                            className={`transition-all duration-300 ease-in-out ${
                              expandedSections.has('transactionSpendingBreakdown') ? 'max-h-[5000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
                            }`}
                          >
                            <div className="px-4 pb-4">
                              {spendingLoading ? (
                                <div className="text-center py-8 text-gray-500">
                                  <p className="text-sm">Loading spending data...</p>
                                </div>
                              ) : spendingError ? (
                                <div className="text-center py-8 text-gray-500">
                                  <FaChartBar className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                                  <p className="text-sm">Unable to load spending data</p>
                                </div>
                              ) : spendingData && spendingData.signals_30d.categories.length > 0 ? (
                                <SpendingBreakdown
                                  categories={spendingData.signals_30d.categories}
                                  totalSpending={spendingData.signals_30d.total_spending}
                                  period="30 days"
                                />
                              ) : (
                                <div className="text-center py-8 text-gray-500">
                                  <FaChartBar className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                                  <p className="text-sm">No spending data available</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th 
                                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                  onClick={() => handleSort('date')}
                                >
                                  <div className="flex items-center gap-1">
                                    Date
                                    {sortBy === 'date' && (
                                      <span className="text-primary-600">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                  </div>
                                </th>
                                <th 
                                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                  onClick={() => handleSort('merchant')}
                                >
                                  <div className="flex items-center gap-1">
                                    Merchant
                                    {sortBy === 'merchant' && (
                                      <span className="text-primary-600">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                  </div>
                                </th>
                                <th 
                                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                  onClick={() => handleSort('category')}
                                >
                                  <div className="flex items-center gap-1">
                                    Category
                                    {sortBy === 'category' && (
                                      <span className="text-primary-600">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                  </div>
                                </th>
                                <th 
                                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                  onClick={() => handleSort('amount')}
                                >
                                  <div className="flex items-center gap-1">
                                    Amount
                                    {sortBy === 'amount' && (
                                      <span className="text-primary-600">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                  </div>
                                </th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {sortedTransactions.map((transaction) => (
                                <tr key={transaction.id}>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {formatDate(transaction.date)}
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    <div className="flex items-center gap-2">
                                      <div 
                                        className="w-2 h-2 rounded-full flex-shrink-0"
                                        style={{ backgroundColor: getCategoryColor(transaction.category_primary) }}
                                      />
                                      <span>{transaction.merchant_name || 'N/A'}</span>
                                    </div>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {transaction.category_primary}
                                  </td>
                                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${
                                    transaction.amount > 0 
                                      ? 'text-green-600' 
                                      : 'text-red-600'
                                  }`}>
                                    {transaction.amount > 0 ? '+' : '-'}{formatCurrency(Math.abs(transaction.amount))}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                        {/* Pagination */}
                        {transactionsData.total > transactionsPerPage && (
                          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 sm:px-6">
                            <div className="flex-1 flex justify-between sm:hidden">
                              <button
                                onClick={() => setTransactionsPage(Math.max(0, transactionsPage - 1))}
                                disabled={transactionsPage === 0}
                                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                Previous
                              </button>
                              <button
                                onClick={() => setTransactionsPage(transactionsPage + 1)}
                                disabled={(transactionsPage + 1) * transactionsPerPage >= transactionsData.total}
                                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                Next
                              </button>
                            </div>
                            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                              <div>
                                <p className="text-sm text-gray-700">
                                  Showing{' '}
                                  <span className="font-medium">{transactionsPage * transactionsPerPage + 1}</span>
                                  {' '}to{' '}
                                  <span className="font-medium">
                                    {Math.min((transactionsPage + 1) * transactionsPerPage, transactionsData.total)}
                                  </span>
                                  {' '}of{' '}
                                  <span className="font-medium">{transactionsData.total}</span>
                                  {' '}transactions
                                </p>
                              </div>
                              <div>
                                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                                  <button
                                    onClick={() => setTransactionsPage(Math.max(0, transactionsPage - 1))}
                                    disabled={transactionsPage === 0}
                                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    <span className="sr-only">Previous</span>
                                    &larr;
                                  </button>
                                  {Array.from({ length: Math.ceil(transactionsData.total / transactionsPerPage) }, (_, i) => i)
                                    .filter(pageNum => {
                                      const totalPages = Math.ceil(transactionsData.total / transactionsPerPage)
                                      if (totalPages <= 7) return true
                                      if (pageNum === 0 || pageNum === totalPages - 1) return true
                                      if (Math.abs(pageNum - transactionsPage) <= 1) return true
                                      return false
                                    })
                                    .map((pageNum, idx, arr) => {
                                      const prevPageNum = arr[idx - 1]
                                      const showEllipsis = prevPageNum !== undefined && pageNum - prevPageNum > 1
                                      return (
                                        <div key={pageNum} className="inline-flex">
                                          {showEllipsis && (
                                            <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                                              ...
                                            </span>
                                          )}
                                          <button
                                            onClick={() => setTransactionsPage(pageNum)}
                                            className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                                              pageNum === transactionsPage
                                                ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                                                : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                                            }`}
                                          >
                                            {pageNum + 1}
                                          </button>
                                        </div>
                                      )
                                    })}
                                  <button
                                    onClick={() => setTransactionsPage(transactionsPage + 1)}
                                    disabled={(transactionsPage + 1) * transactionsPerPage >= transactionsData.total}
                                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    <span className="sr-only">Next</span>
                                    &rarr;
                                  </button>
                                </nav>
                              </div>
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      <p className="text-gray-500 text-center py-8">No transactions found</p>
                    )}
                  </div>
                </div>
              </div>
            )}

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
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 cursor-pointer"
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
