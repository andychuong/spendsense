import { useState } from 'react'

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

interface ProfileBehavioralSignalsProps {
  signals30d?: Signals30d
  signals180d?: Signals30d
  selectedPeriod: '30d' | '180d'
}

const ProfileBehavioralSignals = ({
  signals30d,
  signals180d,
  selectedPeriod,
}: ProfileBehavioralSignalsProps) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['subscriptions']))

  const signals = selectedPeriod === '30d' ? signals30d : signals180d

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

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

  if (!signals || (!signals.subscriptions && !signals.savings && !signals.credit && !signals.income)) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500 text-sm">
          No behavioral signals available for {selectedPeriod === '30d' ? '30-day' : '180-day'}{' '}
          period. Upload your transaction data to see insights.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Subscriptions Section */}
      {signals.subscriptions && (
        <div className="bg-white border border-gray-200 rounded-lg">
          <button
            type="button"
            onClick={() => toggleSection('subscriptions')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <h3 className="text-base font-semibold text-gray-900">Subscriptions</h3>
            <span className="text-gray-500">
              {expandedSections.has('subscriptions') ? '▼' : '▶'}
            </span>
          </button>
          {expandedSections.has('subscriptions') && (
            <div className="px-4 pb-4 space-y-3">
              {signals.subscriptions.recurring_merchants !== undefined && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Recurring Merchants</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.subscriptions.recurring_merchants}
                  </span>
                </div>
              )}
              {signals.subscriptions.monthly_recurring_spend !== undefined && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Monthly Recurring Spend</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(signals.subscriptions.monthly_recurring_spend)}
                  </span>
                </div>
              )}
              {signals.subscriptions.subscription_share !== undefined && (
                <div className="flex justify-between py-2">
                  <span className="text-sm text-gray-600">Subscription Share of Total Spend</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatPercentage(signals.subscriptions.subscription_share)}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Savings Section */}
      {signals.savings && (
        <div className="bg-white border border-gray-200 rounded-lg">
          <button
            type="button"
            onClick={() => toggleSection('savings')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <h3 className="text-base font-semibold text-gray-900">Savings</h3>
            <span className="text-gray-500">{expandedSections.has('savings') ? '▼' : '▶'}</span>
          </button>
          {expandedSections.has('savings') && (
            <div className="px-4 pb-4 space-y-3">
              {signals.savings.net_inflow !== undefined && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Net Inflow</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(signals.savings.net_inflow)}
                  </span>
                </div>
              )}
              {signals.savings.growth_rate !== undefined && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Growth Rate</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatPercentage(signals.savings.growth_rate)}
                  </span>
                </div>
              )}
              {signals.savings.emergency_fund_coverage !== undefined && (
                <div className="flex justify-between py-2">
                  <span className="text-sm text-gray-600">Emergency Fund Coverage</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.savings.emergency_fund_coverage.toFixed(1)} months
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Credit Section */}
      {signals.credit && (
        <div className="bg-white border border-gray-200 rounded-lg">
          <button
            type="button"
            onClick={() => toggleSection('credit')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <h3 className="text-base font-semibold text-gray-900">Credit</h3>
            <span className="text-gray-500">{expandedSections.has('credit') ? '▼' : '▶'}</span>
          </button>
          {expandedSections.has('credit') && (
            <div className="px-4 pb-4 space-y-3">
              {signals.credit.utilization !== undefined && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Utilization</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatPercentage(signals.credit.utilization)}
                  </span>
                </div>
              )}
              {signals.credit.high_utilization_cards !== undefined && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">High Utilization Cards</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.credit.high_utilization_cards}
                  </span>
                </div>
              )}
              {signals.credit.interest_charges !== undefined && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Interest Charges</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(signals.credit.interest_charges)}
                  </span>
                </div>
              )}
              {signals.credit.overdue_accounts !== undefined && (
                <div className="flex justify-between py-2">
                  <span className="text-sm text-gray-600">Overdue Accounts</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.credit.overdue_accounts}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Income Section */}
      {signals.income && (
        <div className="bg-white border border-gray-200 rounded-lg">
          <button
            type="button"
            onClick={() => toggleSection('income')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <h3 className="text-base font-semibold text-gray-900">Income</h3>
            <span className="text-gray-500">{expandedSections.has('income') ? '▼' : '▶'}</span>
          </button>
          {expandedSections.has('income') && (
            <div className="px-4 pb-4 space-y-3">
              {signals.income.payment_frequency !== undefined && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Payment Frequency</span>
                  <span className="text-sm font-medium text-gray-900">
                    Every {signals.income.payment_frequency} days
                  </span>
                </div>
              )}
              {signals.income.cash_flow_buffer !== undefined && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Cash Flow Buffer</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.income.cash_flow_buffer.toFixed(1)} months
                  </span>
                </div>
              )}
              {signals.income.variable_income !== undefined && (
                <div className="flex justify-between py-2">
                  <span className="text-sm text-gray-600">Variable Income</span>
                  <span className="text-sm font-medium text-gray-900">
                    {signals.income.variable_income ? 'Yes' : 'No'}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ProfileBehavioralSignals

