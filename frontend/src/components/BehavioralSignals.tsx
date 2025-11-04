interface Signals30d {
  subscriptions?: {
    recurring_merchants?: number
    monthly_recurring_spend?: number
    subscription_share?: number
  }
  savings?: {
    net_inflow?: number
    growth_rate?: number
    emergency_fund_coverage?: number
  }
  credit?: {
    utilization?: number
    high_utilization_cards?: number
    interest_charges?: number
    overdue_accounts?: number
  }
  income?: {
    payment_frequency?: number
    cash_flow_buffer?: number
    variable_income?: boolean
  }
}

interface BehavioralSignalsProps {
  signals30d?: Signals30d
  signals180d?: Signals30d
}

const BehavioralSignals = ({ signals30d }: BehavioralSignalsProps) => {
  const signals = signals30d || {}

  const formatCurrency = (value?: number) => {
    if (value === undefined || value === null) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatPercentage = (value?: number) => {
    if (value === undefined || value === null) return 'N/A'
    return `${value.toFixed(1)}%`
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Behavioral Signals (30 days)</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Subscriptions */}
        {signals.subscriptions && (
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Subscriptions</h4>
            <div className="space-y-2">
              {signals.subscriptions.recurring_merchants !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Recurring Merchants</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.subscriptions.recurring_merchants}
                  </span>
                </div>
              )}
              {signals.subscriptions.monthly_recurring_spend !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Monthly Recurring Spend</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(signals.subscriptions.monthly_recurring_spend)}
                  </span>
                </div>
              )}
              {signals.subscriptions.subscription_share !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Subscription Share</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatPercentage(signals.subscriptions.subscription_share)}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Savings */}
        {signals.savings && (
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Savings</h4>
            <div className="space-y-2">
              {signals.savings.net_inflow !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Net Inflow</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(signals.savings.net_inflow)}
                  </span>
                </div>
              )}
              {signals.savings.growth_rate !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Growth Rate</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatPercentage(signals.savings.growth_rate)}
                  </span>
                </div>
              )}
              {signals.savings.emergency_fund_coverage !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Emergency Fund Coverage</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.savings.emergency_fund_coverage.toFixed(1)} months
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Credit */}
        {signals.credit && (
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Credit</h4>
            <div className="space-y-2">
              {signals.credit.utilization !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Utilization</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatPercentage(signals.credit.utilization)}
                  </span>
                </div>
              )}
              {signals.credit.high_utilization_cards !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">High Utilization Cards</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.credit.high_utilization_cards}
                  </span>
                </div>
              )}
              {signals.credit.interest_charges !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Interest Charges</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(signals.credit.interest_charges)}
                  </span>
                </div>
              )}
              {signals.credit.overdue_accounts !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Overdue Accounts</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.credit.overdue_accounts}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Income */}
        {signals.income && (
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Income</h4>
            <div className="space-y-2">
              {signals.income.payment_frequency !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Payment Frequency</span>
                  <span className="text-sm font-medium text-gray-900">
                    Every {signals.income.payment_frequency} days
                  </span>
                </div>
              )}
              {signals.income.cash_flow_buffer !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Cash Flow Buffer</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.income.cash_flow_buffer.toFixed(1)} months
                  </span>
                </div>
              )}
              {signals.income.variable_income !== undefined && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Variable Income</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.income.variable_income ? 'Yes' : 'No'}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {!signals.subscriptions && !signals.savings && !signals.credit && !signals.income && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-500 text-sm">
            No behavioral signals available yet. Upload your transaction data to see insights.
          </p>
        </div>
      )}
    </div>
  )
}

export default BehavioralSignals

