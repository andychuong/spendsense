import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { adminService } from '@/services/adminService'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import PersonaBadge from '@/components/PersonaBadge'
import PersonaHistoryTimeline from '@/components/PersonaHistoryTimeline'
import TimePeriodSelector from '@/components/TimePeriodSelector'
import { FaArrowLeft, FaUser, FaEnvelope, FaShieldAlt, FaCheckCircle, FaTimesCircle, FaCreditCard, FaFileInvoice, FaList, FaDollarSign, FaLightbulb, FaSync, FaChevronDown, FaChevronUp, FaChartPie } from 'react-icons/fa'
import type { Account, Transaction, Liability } from '@/services/adminService'
import SpendingBreakdown from '@/components/SpendingBreakdown'
import { dashboardService, type SpendingData } from '@/services/dashboardService'
import { formatMarkdownToReact, stripMarkdown } from '@/utils/formatMarkdown'

const UserDetail = () => {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [transactionsPage, setTransactionsPage] = useState(0)
  const [selectedPeriod, setSelectedPeriod] = useState<'30d' | '180d' | '365d'>('180d')
  const transactionsLimit = 50
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['spendingBreakdown']))

  // Fetch user profile
  const {
    data: userProfile,
    isLoading: profileLoading,
    isError: profileError,
  } = useQuery({
    queryKey: ['admin', 'user', userId, 'profile'],
    queryFn: () => adminService.getUserProfile(userId!),
    enabled: !!userId,
  })

  // Fetch accounts
  const {
    data: accountsData,
    isLoading: accountsLoading,
    isError: accountsError,
  } = useQuery({
    queryKey: ['admin', 'user', userId, 'accounts'],
    queryFn: () => adminService.getUserAccounts(userId!),
    enabled: !!userId,
  })

  // Fetch transactions (paginated)
  const {
    data: transactionsData,
    isLoading: transactionsLoading,
    isError: transactionsError,
  } = useQuery({
    queryKey: ['admin', 'user', userId, 'transactions', transactionsPage],
    queryFn: () => adminService.getUserTransactions(userId!, transactionsPage * transactionsLimit, transactionsLimit),
    enabled: !!userId,
  })

  // Fetch behavioral profile (includes income signals)
  const {
    data: behavioralProfile,
    isLoading: behavioralLoading,
    isError: behavioralError,
  } = useQuery({
    queryKey: ['admin', 'user', userId, 'behavioral-profile'],
    queryFn: () => adminService.getUserBehavioralProfile(userId!),
    enabled: !!userId,
  })

  // Fetch liabilities
  const {
    data: liabilitiesData,
    isLoading: liabilitiesLoading,
    isError: liabilitiesError,
  } = useQuery({
    queryKey: ['admin', 'user', userId, 'liabilities'],
    queryFn: () => adminService.getUserLiabilities(userId!),
    enabled: !!userId,
  })

  // Generate recommendations mutation
  const generateRecommendationsMutation = useMutation({
    mutationFn: () => adminService.generateRecommendations(userId!),
    onSuccess: () => {
      // Invalidate recommendations query to refetch
      queryClient.invalidateQueries({ queryKey: ['admin', 'user', userId, 'recommendations'] })
    },
  })

  // Fetch recommendations
  const {
    data: recommendationsData,
    isLoading: recommendationsLoading,
    isError: recommendationsError,
  } = useQuery({
    queryKey: ['admin', 'user', userId, 'recommendations'],
    queryFn: () => adminService.getUserRecommendations(userId!, 0, 100),
    enabled: !!userId,
  })

  // Fetch persona history
  const {
    data: personaHistoryData,
    isLoading: personaHistoryLoading,
    isError: personaHistoryError,
  } = useQuery({
    queryKey: ['admin', 'user', userId, 'persona-history'],
    queryFn: () => adminService.getUserPersonaHistory(userId!),
    enabled: !!userId,
  })

  // Fetch spending categories
  const {
    data: spendingData,
    isLoading: spendingLoading,
    isError: spendingError,
  } = useQuery<SpendingData>({
    queryKey: ['admin', 'user', userId, 'spending-categories'],
    queryFn: () => dashboardService.getSpendingCategories(userId!),
    enabled: !!userId,
  })

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  if (profileLoading || accountsLoading || transactionsLoading || liabilitiesLoading || behavioralLoading || recommendationsLoading || personaHistoryLoading) {
    return <PageSkeleton sections={6} />
  }

  if (profileError || !userProfile) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorState
            title="Failed to load user"
            error={profileError}
            onRetry={() => window.location.reload()}
            retryLabel="Retry"
          />
        </div>
      </div>
    )
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
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

  // Get signals based on selected period
  // 30d = signals_30d
  // 180d = signals_180d
  // 365d = signals_365d if available, otherwise fallback to signals_180d
  const getSignalsForPeriod = () => {
    if (selectedPeriod === '30d') {
      return behavioralProfile?.signals_30d
    } else if (selectedPeriod === '180d') {
      return behavioralProfile?.signals_180d
    } else { // 365d
      return behavioralProfile?.signals_365d || behavioralProfile?.signals_180d
    }
  }

  const currentSignals = getSignalsForPeriod()
  const incomeSignals = currentSignals?.income
  const monthlyIncome = incomeSignals?.payment_variability?.mean_amount
  const incomeFrequency = incomeSignals?.payment_frequency?.frequency_type
  const isVariableIncome = incomeSignals?.variable_income_pattern?.is_variable_income
  const payrollDeposits = incomeSignals?.payroll_deposits || []
  const totalPayroll = payrollDeposits.reduce((sum, dep) => sum + dep.amount, 0)

  const getPeriodLabel = () => {
    if (selectedPeriod === '30d') return '30 Days'
    if (selectedPeriod === '180d') return '180 Days'
    return '365 Days'
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <button
          onClick={() => navigate('/')}
          className="mb-4 flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <FaArrowLeft className="h-4 w-4" />
          <span>Back to Dashboard</span>
        </button>

        <header className="mb-6 lg:mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="h-16 w-16 rounded-full bg-primary-100 flex items-center justify-center">
              <FaUser className="h-8 w-8 text-primary-600" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                {userProfile.name || 'N/A'}
              </h1>
              <p className="text-sm text-gray-600 mt-1">{userProfile.email || 'No email'}</p>
            </div>
          </div>
        </header>

        {/* User Info Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-500">Role</div>
            <div className="mt-1 flex items-center gap-2">
              <FaShieldAlt className="h-4 w-4 text-gray-400" />
              <span className="text-lg font-semibold text-gray-900 capitalize">{userProfile.role}</span>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-500">Consent</div>
            <div className="mt-1">
              {userProfile.consent_status ? (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <FaCheckCircle className="h-3 w-3" />
                  Granted
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  <FaTimesCircle className="h-3 w-3" />
                  Revoked
                </span>
              )}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-500">Accounts</div>
            <div className="mt-1 text-lg font-semibold text-gray-900">
              {accountsData?.total || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-500">Total Transactions</div>
            <div className="mt-1 text-lg font-semibold text-gray-900">
              {transactionsData?.total || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-500">Monthly Income</div>
            <div className="mt-1 flex items-center gap-2">
              <FaDollarSign className="h-4 w-4 text-gray-400" />
              <span className="text-lg font-semibold text-gray-900">
                {monthlyIncome ? formatCurrency(monthlyIncome) : 'N/A'}
              </span>
            </div>
            {incomeFrequency && (
              <div className="mt-1 text-xs text-gray-500 capitalize">{incomeFrequency}</div>
            )}
          </div>
        </div>

        {/* Time Period Selector */}
        {behavioralProfile && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Analysis Period</h2>
              <p className="text-sm text-gray-600">
                Select a time period to view behavioral signals and analysis
              </p>
            </div>
            <TimePeriodSelector
              selectedPeriod={selectedPeriod}
              onPeriodChange={setSelectedPeriod}
            />
          </div>
        )}

        {/* Current Persona */}
        {behavioralProfile && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Persona</h2>
            <PersonaBadge
              personaId={behavioralProfile.persona_id}
              personaName={behavioralProfile.persona_name}
            />
          </div>
        )}

        {/* Income Section */}
        {incomeSignals && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FaDollarSign className="h-5 w-5 text-primary-600" />
              Income Analysis ({getPeriodLabel()})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Monthly Income */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500">Estimated Monthly Income</div>
                <div className="mt-1 text-2xl font-bold text-gray-900">
                  {monthlyIncome ? formatCurrency(monthlyIncome) : 'N/A'}
                </div>
                {incomeSignals.payment_variability && (
                  <div className="mt-2 text-xs text-gray-500">
                    Range: {formatCurrency(incomeSignals.payment_variability.min_amount || 0)} - {formatCurrency(incomeSignals.payment_variability.max_amount || 0)}
                  </div>
                )}
              </div>

              {/* Payment Frequency */}
              {incomeSignals.payment_frequency && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Payment Frequency</div>
                  <div className="mt-1 text-xl font-semibold text-gray-900 capitalize">
                    {incomeFrequency || 'N/A'}
                  </div>
                  {incomeSignals.payment_frequency.deposit_count && (
                    <div className="mt-2 text-xs text-gray-500">
                      {incomeSignals.payment_frequency.deposit_count} deposits detected
                    </div>
                  )}
                  {incomeSignals.payment_frequency.median_gap_days && (
                    <div className="mt-1 text-xs text-gray-500">
                      Median gap: {incomeSignals.payment_frequency.median_gap_days} days
                    </div>
                  )}
                </div>
              )}

              {/* Income Variability */}
              {incomeSignals.payment_variability && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Income Stability</div>
                  <div className="mt-1 text-xl font-semibold text-gray-900 capitalize">
                    {incomeSignals.payment_variability.variability_level || 'N/A'}
                  </div>
                  {incomeSignals.payment_variability.coefficient_of_variation !== undefined &&
                   incomeSignals.payment_variability.coefficient_of_variation !== null && (
                    <div className="mt-2 text-xs text-gray-500">
                      Variability: {incomeSignals.payment_variability.coefficient_of_variation.toFixed(1)}%
                    </div>
                  )}
                  {isVariableIncome !== undefined && (
                    <div className="mt-1">
                      {isVariableIncome ? (
                        <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
                          Variable Income
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                          Stable Income
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Cash Flow Buffer */}
              {incomeSignals.cash_flow_buffer && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Cash Flow Buffer</div>
                  <div className="mt-1 text-2xl font-bold text-gray-900">
                    {incomeSignals.cash_flow_buffer.cash_flow_buffer_months != null
                      ? incomeSignals.cash_flow_buffer.cash_flow_buffer_months.toFixed(1)
                      : '0'} months
                  </div>
                  {incomeSignals.cash_flow_buffer.current_balance !== undefined && (
                    <div className="mt-2 text-xs text-gray-500">
                      Current balance: {formatCurrency(incomeSignals.cash_flow_buffer.current_balance)}
                    </div>
                  )}
                  {incomeSignals.cash_flow_buffer.average_monthly_expenses !== undefined && (
                    <div className="mt-1 text-xs text-gray-500">
                      Avg expenses: {formatCurrency(incomeSignals.cash_flow_buffer.average_monthly_expenses)}/mo
                    </div>
                  )}
                </div>
              )}

              {/* Total Payroll Deposits */}
              {payrollDeposits.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Payroll Deposits ({getPeriodLabel()})</div>
                  <div className="mt-1 text-xl font-semibold text-gray-900">
                    {payrollDeposits.length} deposits
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    Total: {formatCurrency(totalPayroll)}
                  </div>
                </div>
              )}
            </div>

            {/* Payroll Deposits Table */}
            {payrollDeposits.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Recent Payroll Deposits</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Merchant</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {payrollDeposits.slice(-10).reverse().map((deposit, idx) => (
                        <tr key={idx}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(deposit.date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatCurrency(deposit.amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {deposit.merchant_name || 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Accounts Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <FaCreditCard className="h-5 w-5 text-primary-600" />
            Accounts ({accountsData?.total || 0})
          </h2>
          {accountsError ? (
            <ErrorState title="Failed to load accounts" error={accountsError} />
          ) : accountsData && accountsData.items.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Balance</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Limit</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {accountsData.items.map((account: Account) => (
                    <tr key={account.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {account.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {account.type} / {account.subtype}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(account.balance_current)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {account.balance_limit ? formatCurrency(account.balance_limit) : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No accounts found</p>
          )}
        </div>

        {/* Spending Breakdown Section */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <button
            onClick={() => toggleSection('spendingBreakdown')}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FaChartPie className="h-5 w-5 text-primary-600" />
              Spending Breakdown
            </h2>
            {expandedSections.has('spendingBreakdown') ? (
              <FaChevronUp className="h-5 w-5 text-gray-400" />
            ) : (
              <FaChevronDown className="h-5 w-5 text-gray-400" />
            )}
          </button>
          {expandedSections.has('spendingBreakdown') && (
            <div className="px-6 pb-6">
              {spendingLoading ? (
                <div className="text-center py-8 text-gray-500">
                  <p>Loading spending data...</p>
                </div>
              ) : spendingError ? (
                <ErrorState title="Failed to load spending breakdown" error={spendingError} />
              ) : spendingData ? (
                <SpendingBreakdown
                  categories={spendingData.signals_30d.categories}
                  totalSpending={spendingData.signals_30d.total_spending}
                  period="30 days"
                />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No spending data available</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Transactions Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <FaList className="h-5 w-5 text-primary-600" />
            Recent Transactions ({transactionsData?.total || 0})
          </h2>
          {transactionsError ? (
            <ErrorState title="Failed to load transactions" error={transactionsError} />
          ) : transactionsData && transactionsData.items.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Merchant</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {transactionsData.items.map((transaction: Transaction) => (
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
              {transactionsData.total > transactionsLimit && (
                <div className="mt-4 flex items-center justify-between">
                  <button
                    onClick={() => setTransactionsPage((p) => Math.max(0, p - 1))}
                    disabled={transactionsPage === 0}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-gray-700">
                    Page {transactionsPage + 1} of {Math.ceil(transactionsData.total / transactionsLimit)}
                  </span>
                  <button
                    onClick={() => setTransactionsPage((p) => p + 1)}
                    disabled={(transactionsPage + 1) * transactionsLimit >= transactionsData.total}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500 text-center py-8">No transactions found</p>
          )}
        </div>

        {/* Liabilities Section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <FaFileInvoice className="h-5 w-5 text-primary-600" />
            Liabilities ({liabilitiesData?.total || 0})
          </h2>
          {liabilitiesError ? (
            <ErrorState title="Failed to load liabilities" error={liabilitiesError} />
          ) : liabilitiesData && liabilitiesData.items.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">APR</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Minimum Payment</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Payment</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Next Due</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {liabilitiesData.items.map((liability: Liability) => (
                    <tr key={liability.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {liability.apr_percentage ? `${liability.apr_percentage}%` : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {liability.minimum_payment_amount ? formatCurrency(liability.minimum_payment_amount) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {liability.last_payment_date ? formatDate(liability.last_payment_date) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {liability.next_payment_due_date ? formatDate(liability.next_payment_due_date) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {liability.is_overdue ? (
                          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                            Overdue
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                            Current
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No liabilities found</p>
          )}
        </div>

        {/* Recommendations Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FaLightbulb className="h-5 w-5 text-primary-600" />
              Recommendations ({recommendationsData?.total || 0})
            </h2>
            <button
              onClick={() => generateRecommendationsMutation.mutate()}
              disabled={generateRecommendationsMutation.isPending}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FaSync className={generateRecommendationsMutation.isPending ? 'animate-spin' : ''} />
              {generateRecommendationsMutation.isPending ? 'Generating...' : 'Generate Recommendations'}
            </button>
          </div>
          {generateRecommendationsMutation.isError && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">
                Failed to generate recommendations: {generateRecommendationsMutation.error instanceof Error ? generateRecommendationsMutation.error.message : 'Unknown error'}
              </p>
            </div>
          )}
          {generateRecommendationsMutation.isSuccess && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <p className="text-sm text-green-800">
                Successfully generated {generateRecommendationsMutation.data.recommendations_generated} recommendations
                ({generateRecommendationsMutation.data.education_count} education, {generateRecommendationsMutation.data.partner_offer_count} partner offers)
              </p>
            </div>
          )}
          {recommendationsError ? (
            <ErrorState title="Failed to load recommendations" error={recommendationsError} />
          ) : recommendationsData && recommendationsData.items.length > 0 ? (
            <div className="space-y-4">
              {recommendationsData.items.map((rec) => (
                <div key={rec.recommendation_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="text-base font-semibold text-gray-900">{rec.title}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          rec.type === 'education'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-purple-100 text-purple-800'
                        }`}>
                          {rec.type === 'education' ? 'Education' : 'Partner Offer'}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          rec.status === 'approved'
                            ? 'bg-green-100 text-green-800'
                            : rec.status === 'rejected'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {rec.status.charAt(0).toUpperCase() + rec.status.slice(1)}
                        </span>
                      </div>
                    </div>
                    <span className="text-xs text-gray-500">
                      {formatDate(rec.created_at)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    {formatMarkdownToReact(stripMarkdown(rec.content.substring(0, 200)))}
                    {rec.content.length > 200 && '...'}
                  </div>
                  {rec.rationale && (
                    <div className="mt-2 p-3 bg-gray-50 rounded">
                      <p className="text-xs font-medium text-gray-700 mb-1">Rationale:</p>
                      <div className="text-xs text-gray-600">
                        {formatMarkdownToReact(rec.rationale)}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No recommendations found</p>
          )}
        </div>

        {/* Persona History Timeline */}
        {personaHistoryData && personaHistoryData.items.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <PersonaHistoryTimeline history={personaHistoryData.items} />
          </div>
        )}
      </div>
    </div>
  )
}

export default UserDetail

