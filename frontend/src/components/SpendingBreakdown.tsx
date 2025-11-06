import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface Category {
  category: string
  amount: number
  percentage: number
  transaction_count: number
  top_merchants?: Array<{ merchant: string; amount: number }>
}

interface SpendingBreakdownProps {
  categories: Category[]
  totalSpending: number
  period?: string
}

// Color palette for categories
const CATEGORY_COLORS: Record<string, string> = {
  'Food & Dining': '#ef4444',
  'Groceries': '#f97316',
  'Transportation': '#f59e0b',
  'Shopping': '#eab308',
  'Bills & Utilities': '#84cc16',
  'Entertainment': '#22c55e',
  'Healthcare': '#10b981',
  'Travel': '#14b8a6',
  'Personal Care': '#06b6d4',
  'Financial': '#0ea5e9',
  'Other': '#6b7280'
}

const SpendingBreakdown = ({ categories, totalSpending, period = '30 days' }: SpendingBreakdownProps) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  // Prepare data for pie chart
  const chartData = categories.map(cat => ({
    name: cat.category,
    value: cat.amount,
    percentage: cat.percentage
  }))

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{payload[0].name}</p>
          <p className="text-sm text-gray-600">
            {formatCurrency(payload[0].value)} ({payload[0].payload.percentage.toFixed(1)}%)
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div>
      <div className="flex items-center justify-end mb-6">
        <div className="text-right">
          <p className="text-sm text-gray-500">Total Spending</p>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalSpending)}</p>
        </div>
      </div>

      {categories.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No spending data available</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Pie Chart */}
          <div className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={90}
                  fill="#8884d8"
                  dataKey="value"
                  label={(entry) => `${entry.percentage.toFixed(0)}%`}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.name] || '#6b7280'} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Right: Top 3 + All Categories */}
          <div className="space-y-4">
            {/* Top 3 Categories - Condensed */}
            <div className="grid grid-cols-3 gap-2">
              {categories.slice(0, 3).map((category, idx) => (
                <div
                  key={category.category}
                  className="bg-gray-50 rounded p-2 border border-gray-200"
                >
                  <div className="flex items-center gap-1 mb-1">
                    <span className="text-sm font-bold text-gray-400">#{idx + 1}</span>
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: CATEGORY_COLORS[category.category] || '#6b7280' }}
                    />
                  </div>
                  <p className="text-xs font-medium text-gray-900 truncate">{category.category}</p>
                  <p className="text-sm font-bold text-gray-900">{formatCurrency(category.amount)}</p>
                  <p className="text-xs text-gray-500">{category.percentage.toFixed(1)}%</p>
                </div>
              ))}
            </div>

            {/* All Categories List */}
            <div className="bg-white rounded-lg border border-gray-200 p-3">
              <h4 className="text-xs font-semibold text-gray-700 mb-2">All Categories</h4>
              <div className="space-y-1.5 max-h-[140px] overflow-y-auto">
                {categories.map((category) => (
                  <div key={category.category} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <div
                        className="w-2 h-2 rounded-full flex-shrink-0"
                        style={{ backgroundColor: CATEGORY_COLORS[category.category] || '#6b7280' }}
                      />
                      <span className="text-gray-700 truncate">{category.category}</span>
                    </div>
                    <div className="flex items-center gap-2 ml-2">
                      <span className="font-semibold text-gray-900">{formatCurrency(category.amount)}</span>
                      <span className="text-gray-500 w-10 text-right">{category.percentage.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SpendingBreakdown

