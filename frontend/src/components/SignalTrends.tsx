interface SignalTrendsProps {
  signals30d?: Record<string, any>
  signals180d?: Record<string, any>
}

const SignalTrends = ({ signals30d, signals180d }: SignalTrendsProps) => {
  // Simple trend visualization using progress bars
  // This is a placeholder - could be enhanced with a chart library later

  const getTrend = (value30d?: number, value180d?: number) => {
    if (value30d === undefined || value180d === undefined) return null
    if (value30d === value180d) return 'stable'
    if (value30d > value180d) return 'increasing'
    return 'decreasing'
  }

  const getTrendIcon = (trend: string | null) => {
    if (!trend) return null
    if (trend === 'increasing') return '↑'
    if (trend === 'decreasing') return '↓'
    return '→'
  }

  const getTrendColor = (trend: string | null) => {
    if (!trend) return 'text-gray-500'
    if (trend === 'increasing') return 'text-green-600'
    if (trend === 'decreasing') return 'text-red-600'
    return 'text-blue-600'
  }

  const formatValue = (value?: number, type: 'currency' | 'percentage' | 'number' = 'number') => {
    if (value === undefined || value === null) return 'N/A'

    // Ensure value is a number
    const numValue = typeof value === 'number' ? value : Number(value)
    if (isNaN(numValue)) return 'N/A'

    if (type === 'currency') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(numValue)
    }

    if (type === 'percentage') {
      return `${numValue.toFixed(1)}%`
    }

    return numValue.toString()
  }

  const renderTrendBar = (
    label: string,
    value30d?: number,
    value180d?: number,
    type: 'currency' | 'percentage' | 'number' = 'number',
    maxValue?: number
  ) => {
    const trend = getTrend(value30d, value180d)
    const displayValue = value30d !== undefined ? value30d : value180d
    const max = maxValue || (displayValue ? displayValue * 1.5 : 100)

    if (displayValue === undefined || displayValue === null) return null

    const percentage = Math.min((displayValue / max) * 100, 100)

    return (
      <div key={label} className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-900">{formatValue(displayValue, type)}</span>
            {trend && (
              <span className={`text-sm font-medium ${getTrendColor(trend)}`}>
                {getTrendIcon(trend)}
              </span>
            )}
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              trend === 'increasing'
                ? 'bg-green-500'
                : trend === 'decreasing'
                ? 'bg-red-500'
                : 'bg-blue-500'
            }`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        {trend && value30d !== undefined && value180d !== undefined && (
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>30d: {formatValue(value30d, type)}</span>
            <span>180d: {formatValue(value180d, type)}</span>
          </div>
        )}
      </div>
    )
  }

  if (!signals30d && !signals180d) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500 text-sm">No signal trends available yet.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Signal Trends</h3>

      {/* Subscriptions Trends */}
      {signals30d?.subscriptions && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-4">Subscriptions</h4>
          <div className="space-y-4">
            {renderTrendBar(
              'Monthly Recurring Spend',
              signals30d.subscriptions.total_recurring_spend,
              signals180d?.subscriptions?.total_recurring_spend,
              'currency',
              signals180d?.subscriptions?.total_recurring_spend
                ? Math.max(
                    signals30d.subscriptions.total_recurring_spend || 0,
                    signals180d.subscriptions.total_recurring_spend || 0
                  ) * 1.2
                : undefined
            )}
            {renderTrendBar(
              'Subscription Share',
              signals30d.subscriptions.subscription_share_percent,
              signals180d?.subscriptions?.subscription_share_percent,
              'percentage',
              100
            )}
          </div>
        </div>
      )}

      {/* Savings Trends */}
      {signals30d?.savings && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-4">Savings</h4>
          <div className="space-y-4">
            {renderTrendBar(
              'Net Inflow',
              signals30d.savings.net_inflow?.net_inflow,
              signals180d?.savings?.net_inflow?.net_inflow,
              'currency',
              signals180d?.savings?.net_inflow?.net_inflow
                ? Math.max(
                    signals30d.savings.net_inflow?.net_inflow || 0,
                    signals180d.savings.net_inflow?.net_inflow || 0
                  ) * 1.2
                : undefined
            )}
            {renderTrendBar(
              'Growth Rate',
              signals30d.savings.growth_rate?.growth_rate_percent,
              signals180d?.savings?.growth_rate?.growth_rate_percent,
              'percentage',
              50
            )}
          </div>
        </div>
      )}

      {/* Credit Trends */}
      {signals30d?.credit && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-4">Credit</h4>
          <div className="space-y-4">
            {renderTrendBar(
              'Utilization',
              signals30d.credit.total_utilization,
              signals180d?.credit?.total_utilization,
              'percentage',
              100
            )}
            {renderTrendBar(
              'Cards with Interest',
              signals30d.credit.cards_with_interest?.length,
              signals180d?.credit?.cards_with_interest?.length,
              'number',
              signals180d?.credit?.cards_with_interest?.length
                ? Math.max(
                    signals30d.credit.cards_with_interest?.length || 0,
                    signals180d.credit.cards_with_interest?.length || 0
                  ) * 1.2
                : undefined
            )}
          </div>
        </div>
      )}

      {/* Income Trends */}
      {signals30d?.income && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-4">Income</h4>
          <div className="space-y-4">
            {renderTrendBar(
              'Cash Flow Buffer',
              signals30d.income.cash_flow_buffer?.cash_flow_buffer_months,
              signals180d?.income?.cash_flow_buffer?.cash_flow_buffer_months,
              'number',
              12
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default SignalTrends

