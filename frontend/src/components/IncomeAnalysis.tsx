interface IncomeSignals {
  payroll_deposits?: Array<{ date: string; amount: number; merchant_name: string }>
  payment_frequency?: {
    median_gap_days?: number
    frequency_type?: string
    deposit_count?: number
  }
  payment_variability?: {
    mean_amount?: number
    std_deviation?: number
    min_amount?: number
    max_amount?: number
    variability_level?: string
    coefficient_of_variation?: number
  }
  cash_flow_buffer?: {
    cash_flow_buffer_months?: number
    current_balance?: number
    minimum_balance?: number
    average_monthly_expenses?: number
  }
  variable_income_pattern?: {
    is_variable_income?: boolean
    confidence?: string
    reasons?: string[]
  }
}

interface IncomeAnalysisProps {
  signals: IncomeSignals
  period?: string
}

const IncomeAnalysis = ({ signals, period = '30 days' }: IncomeAnalysisProps) => {
  const formatCurrency = (value?: number) => {
    if (value === undefined || value === null) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const deposits = signals.payroll_deposits || []
  const frequency = signals.payment_frequency || {}
  const variability = signals.payment_variability || {}
  const cashFlow = signals.cash_flow_buffer || {}
  const variablePattern = signals.variable_income_pattern || {}

  const totalIncome = deposits.reduce((sum, dep) => sum + dep.amount, 0)
  const avgIncome = deposits.length > 0 ? totalIncome / deposits.length : 0

  // Determine income stability
  const isStable = !variablePattern.is_variable_income && 
                   variability.variability_level &&
                   ['low', 'stable'].includes(variability.variability_level.toLowerCase())

  const stabilityColor = isStable ? 'text-green-600' : 
                         variablePattern.is_variable_income ? 'text-orange-600' : 
                         'text-yellow-600'

  const stabilityBgColor = isStable ? 'bg-green-50 border-green-200' : 
                          variablePattern.is_variable_income ? 'bg-orange-50 border-orange-200' : 
                          'bg-yellow-50 border-yellow-200'

  return (
    <div>
      <div className="flex items-center justify-end mb-6">
        <div className={`px-3 py-1 rounded-full border ${stabilityBgColor}`}>
          <span className={`text-sm font-medium ${stabilityColor}`}>
            {isStable ? 'Stable' : variablePattern.is_variable_income ? 'Variable' : 'Moderate'}
          </span>
        </div>
      </div>

      {deposits.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No income data available</p>
          <p className="text-sm mt-2">We'll analyze your income patterns as transactions come in</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Income Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Total Income */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
              <p className="text-sm text-blue-700 font-medium mb-1">Total Income</p>
              <p className="text-2xl font-bold text-blue-900">{formatCurrency(totalIncome)}</p>
              <p className="text-xs text-blue-600 mt-1">{deposits.length} deposits</p>
            </div>

            {/* Average Payment */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
              <p className="text-sm text-purple-700 font-medium mb-1">Average Payment</p>
              <p className="text-2xl font-bold text-purple-900">{formatCurrency(avgIncome)}</p>
              <p className="text-xs text-purple-600 mt-1">
                {variability.mean_amount && Math.abs(avgIncome - variability.mean_amount) < 1 
                  ? 'Consistent' 
                  : 'Varies'}
              </p>
            </div>

            {/* Payment Frequency */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
              <p className="text-sm text-green-700 font-medium mb-1">Payment Frequency</p>
              <p className="text-lg font-bold text-green-900 capitalize">
                {frequency.frequency_type === 'insufficient_data' 
                  ? 'Analyzing...'
                  : frequency.frequency_type || 'Unknown'}
              </p>
              <p className="text-xs text-green-600 mt-1">
                {frequency.median_gap_days 
                  ? `Every ${frequency.median_gap_days} days`
                  : 'Calculating...'}
              </p>
            </div>
          </div>

          {/* Detailed Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Income Stability */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Income Stability</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Variability Level</span>
                  <span className={`text-sm font-medium capitalize ${stabilityColor}`}>
                    {variability.variability_level || 'Unknown'}
                  </span>
                </div>
                {variability.coefficient_of_variation !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Coefficient of Variation</span>
                    <span className="text-sm font-medium text-gray-900">
                      {variability.coefficient_of_variation.toFixed(1)}%
                    </span>
                  </div>
                )}
                {variability.min_amount !== undefined && variability.max_amount !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Range</span>
                    <span className="text-sm font-medium text-gray-900">
                      {formatCurrency(variability.min_amount)} - {formatCurrency(variability.max_amount)}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Cash Flow Buffer */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Cash Flow Buffer</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Buffer Coverage</span>
                  <span className="text-sm font-medium text-gray-900">
                    {cashFlow.cash_flow_buffer_months?.toFixed(1) || '0.0'} months
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Current Balance</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(cashFlow.current_balance)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Avg Monthly Expenses</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(cashFlow.average_monthly_expenses)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Variable Income Warning */}
          {variablePattern.is_variable_income && variablePattern.reasons && variablePattern.reasons.length > 0 && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="w-5 h-5 bg-orange-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-white text-xs font-bold">!</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-orange-900 mb-2">Variable Income Detected</p>
                  <ul className="space-y-1">
                    {variablePattern.reasons.map((reason, idx) => (
                      <li key={idx} className="text-sm text-orange-700">
                        • {reason}
                      </li>
                    ))}
                  </ul>
                  <p className="text-xs text-orange-600 mt-2">
                    Consider building a 3-6 month emergency fund to smooth income variations
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Recent Deposits */}
          {deposits.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Recent Income Deposits</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {deposits.slice(0, 10).map((deposit, idx) => (
                  <div key={idx} className="flex justify-between items-center text-sm py-2 border-b border-gray-100 last:border-0">
                    <div>
                      <p className="font-medium text-gray-900">{deposit.merchant_name || 'Income Deposit'}</p>
                      <p className="text-xs text-gray-500">{new Date(deposit.date).toLocaleDateString()}</p>
                    </div>
                    <p className="font-semibold text-green-600">{formatCurrency(deposit.amount)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default IncomeAnalysis

