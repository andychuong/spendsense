import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { operatorService, type SystemAnalytics } from '@/services/operatorService'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import {
  FaChartBar,
  FaUsers,
  FaCheckCircle,
  FaClock,
  FaArrowLeft,
  FaDownload,
  FaChartLine,
  FaChartPie,
  FaTachometerAlt,
  FaFileAlt,
} from 'react-icons/fa'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const OperatorAnalytics = () => {
  // State hooks must be called unconditionally at the top
  const [isExporting, setIsExporting] = useState<{ json?: boolean; csv?: boolean; summary?: boolean }>({})

  // Fetch analytics
  const {
    data: analytics,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<SystemAnalytics>({
    queryKey: ['operator', 'analytics'],
    queryFn: () => operatorService.getAnalytics(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Loading state
  if (isLoading) {
    return <PageSkeleton sections={4} />
  }

  // Error state
  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorState
            title="Failed to load analytics"
            error={error}
            onRetry={() => refetch()}
            retryLabel="Retry"
          />
        </div>
      </div>
    )
  }

  const stats = analytics || {
    coverage: {
      users_with_persona: 0,
      users_with_persona_percent: 0,
      users_with_behaviors: 0,
      users_with_behaviors_percent: 0,
      users_with_both: 0,
      users_with_both_percent: 0,
    },
    explainability: {
      recommendations_with_rationales: 0,
      recommendations_with_rationales_percent: 0,
      rationales_with_data_points: 0,
      rationales_with_data_points_percent: 0,
      rationale_quality_score: 0,
    },
    performance: {
      p50_latency_ms: 0,
      p95_latency_ms: 0,
      p99_latency_ms: 0,
      mean_latency_ms: 0,
      min_latency_ms: 0,
      max_latency_ms: 0,
      recommendations_within_target: 0,
      recommendations_within_target_percent: 0,
    },
    engagement: {
      total_users: 0,
      active_users: 0,
      recommendations_sent: 0,
      recommendations_viewed: 0,
      recommendations_actioned: 0,
    },
    fairness: {
      persona_balance_score: 0,
      persona_distribution: {},
      signal_detection_by_persona: {},
    },
  }

  // Prepare data for charts
  const coverageData = [
    {
      name: 'With Persona',
      value: stats.coverage?.users_with_persona_percent || 0,
      count: stats.coverage?.users_with_persona || 0,
    },
    {
      name: 'With Behaviors',
      value: stats.coverage?.users_with_behaviors_percent || 0,
      count: stats.coverage?.users_with_behaviors || 0,
    },
    {
      name: 'With Both',
      value: stats.coverage?.users_with_both_percent || 0,
      count: stats.coverage?.users_with_both || 0,
    },
  ]

  const explainabilityData = [
    {
      name: 'With Rationales',
      value: stats.explainability?.recommendations_with_rationales_percent || 0,
      count: stats.explainability?.recommendations_with_rationales || 0,
    },
    {
      name: 'With Data Points',
      value: stats.explainability?.rationales_with_data_points_percent || 0,
      count: stats.explainability?.rationales_with_data_points || 0,
    },
  ]

  const performanceData = [
    {
      name: 'p50',
      latency: (stats.performance?.p50_latency_ms || 0) / 1000, // Convert to seconds
    },
    {
      name: 'p95',
      latency: (stats.performance?.p95_latency_ms || 0) / 1000,
    },
    {
      name: 'p99',
      latency: (stats.performance?.p99_latency_ms || 0) / 1000,
    },
    {
      name: 'Mean',
      latency: (stats.performance?.mean_latency_ms || 0) / 1000,
    },
  ]

  const engagementData = [
    {
      name: 'Sent',
      value: stats.engagement?.recommendations_sent || 0,
    },
    {
      name: 'Viewed',
      value: stats.engagement?.recommendations_viewed || 0,
    },
    {
      name: 'Actioned',
      value: stats.engagement?.recommendations_actioned || 0,
    },
  ]

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      setIsExporting({ [format]: true })

      let blob: Blob
      let filename: string

      if (format === 'json') {
        blob = await operatorService.exportMetricsJSON()
        filename = `metrics_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.json`
      } else {
        blob = await operatorService.exportMetricsCSV()
        filename = `metrics_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.csv`
      }

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error(`Failed to export ${format}:`, error)
      alert(`Failed to export ${format.toUpperCase()}. Please try again.`)
    } finally {
      setIsExporting({ [format]: false })
    }
  }

  const handleExportSummary = async () => {
    try {
      setIsExporting({ summary: true })

      const blob = await operatorService.exportSummaryReport()
      const filename = `summary_report_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.md`

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export summary report:', error)
      alert('Failed to export summary report. Please try again.')
    } finally {
      setIsExporting({ summary: false })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-6 lg:mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Link
                to="/operator"
                className="text-gray-600 hover:text-gray-900 transition-colors"
                aria-label="Back to dashboard"
              >
                <FaArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                  Analytics Dashboard
                </h1>
                <p className="mt-2 text-sm text-gray-600">
                  System-wide metrics and performance analytics
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleExport('json')}
                disabled={isExporting.json}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FaDownload className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {isExporting.json ? 'Exporting...' : 'Export JSON'}
                </span>
                <span className="sm:hidden">JSON</span>
              </button>
              <button
                onClick={() => handleExport('csv')}
                disabled={isExporting.csv}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FaDownload className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {isExporting.csv ? 'Exporting...' : 'Export CSV'}
                </span>
                <span className="sm:hidden">CSV</span>
              </button>
              <button
                onClick={handleExportSummary}
                disabled={isExporting.summary}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FaFileAlt className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {isExporting.summary ? 'Generating...' : 'Summary Report'}
                </span>
                <span className="sm:hidden">Report</span>
              </button>
            </div>
          </div>
        </header>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Coverage Card */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Coverage</h3>
              <FaChartBar className="h-5 w-5 text-blue-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {(stats.coverage?.users_with_persona_percent || 0).toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {stats.coverage?.users_with_persona || 0} users with persona
            </p>
          </div>

          {/* Explainability Card */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Explainability</h3>
              <FaCheckCircle className="h-5 w-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {(stats.explainability?.recommendations_with_rationales_percent || 0).toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {stats.explainability?.recommendations_with_rationales || 0} with rationales
            </p>
          </div>

          {/* Performance Card */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Performance</h3>
              <FaTachometerAlt className="h-5 w-5 text-purple-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {((stats.performance?.p95_latency_ms || 0) / 1000).toFixed(2)}s
            </p>
            <p className="text-xs text-gray-500 mt-1">p95 latency</p>
          </div>

          {/* Engagement Card */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Engagement</h3>
              <FaUsers className="h-5 w-5 text-orange-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {(stats.engagement?.active_users || 0).toLocaleString()}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {stats.engagement?.total_users || 0} total users
            </p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Coverage Metrics Chart */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FaChartBar className="h-5 w-5 text-blue-600" />
              Coverage Metrics
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={coverageData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  formatter={(value: number, name: string) => {
                    if (name === 'value') {
                      return [`${value.toFixed(1)}%`, 'Percentage']
                    }
                    return [value, 'Count']
                  }}
                />
                <Legend />
                <Bar dataKey="value" fill="#3b82f6" name="Percentage (%)" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-3 gap-4 text-center">
              {coverageData.map((item) => (
                <div key={item.name}>
                  <p className="text-xs text-gray-600">{item.name}</p>
                  <p className="text-sm font-semibold text-gray-900">{item.count}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Explainability Metrics Chart */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FaCheckCircle className="h-5 w-5 text-green-600" />
              Explainability Metrics
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={explainabilityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  formatter={(value: number, name: string) => {
                    if (name === 'value') {
                      return [`${value.toFixed(1)}%`, 'Percentage']
                    }
                    return [value, 'Count']
                  }}
                />
                <Legend />
                <Bar dataKey="value" fill="#10b981" name="Percentage (%)" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Quality Score</span>
                <span className="text-lg font-semibold text-gray-900">
                  {(stats.explainability?.rationale_quality_score || 0).toFixed(1)}/10
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all"
                  style={{
                    width: `${Math.min(Math.max(((stats.explainability?.rationale_quality_score || 0) / 10) * 100, 0), 100)}%`,
                  }}
                />
              </div>
            </div>
          </div>

          {/* Performance Metrics Chart */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FaTachometerAlt className="h-5 w-5 text-purple-600" />
              Performance Metrics
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  formatter={(value: number) => [`${value.toFixed(2)}s`, 'Latency']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="latency"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  name="Latency (seconds)"
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-600">Within Target</p>
                <p className="text-sm font-semibold text-gray-900">
                  {(stats.performance?.recommendations_within_target_percent || 0).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Target: &lt;5s</p>
                <p className="text-sm font-semibold text-gray-900">
                  {stats.performance?.recommendations_within_target || 0} /{' '}
                  {(stats.performance?.recommendations_within_target_percent || 0) > 0
                    ? Math.round(
                        ((stats.performance?.recommendations_within_target || 0) /
                          (stats.performance?.recommendations_within_target_percent || 1)) *
                          100
                      )
                    : 0}
                </p>
              </div>
            </div>
          </div>

          {/* Engagement Metrics Chart */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FaUsers className="h-5 w-5 text-orange-600" />
              Engagement Metrics
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={engagementData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value: number) => [value.toLocaleString(), 'Count']} />
                <Legend />
                <Bar dataKey="value" fill="#f59e0b" name="Count" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-3 gap-4 text-center">
              {engagementData.map((item) => (
                <div key={item.name}>
                  <p className="text-xs text-gray-600">{item.name}</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {item.value.toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Fairness Metrics Chart */}
          {stats.fairness && stats.fairness.persona_balance_score !== undefined && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <FaChartPie className="h-5 w-5 text-purple-600" />
                Fairness Metrics
              </h2>
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Persona Balance Score</span>
                  <span className="text-lg font-semibold text-gray-900">
                    {stats.fairness.persona_balance_score.toFixed(3)}/1.0
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all"
                    style={{
                      width: `${Math.min(Math.max(stats.fairness.persona_balance_score * 100, 0), 100)}%`,
                    }}
                  />
                </div>
              </div>
              {stats.fairness.persona_distribution &&
                Object.keys(stats.fairness.persona_distribution).length > 0 && (
                  <div className="mt-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Persona Distribution</h3>
                    <div className="space-y-2">
                      {Object.entries(stats.fairness.persona_distribution)
                        .sort(([a], [b]) => parseInt(a) - parseInt(b))
                        .map(([personaId, dist]: [string, any]) => (
                          <div
                            key={personaId}
                            className="flex items-center justify-between py-2 border-b border-gray-200 last:border-0"
                          >
                            <span className="text-sm text-gray-600">Persona {personaId}</span>
                            <div className="flex gap-4 text-xs">
                              <span className="text-gray-600">
                                {dist?.recommendations_count || 0} recs (
                                {(dist?.recommendations_percent || 0).toFixed(1)}%)
                              </span>
                              <span className="text-gray-600">
                                {dist?.users_count || 0} users ({(dist?.users_percent || 0).toFixed(1)}%)
                              </span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
            </div>
          )}
        </div>

        {/* Detailed Metrics Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Details */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FaClock className="h-5 w-5 text-gray-600" />
              Performance Details
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">p50 Latency</span>
                <span className="text-sm font-semibold text-gray-900">
                  {((stats.performance?.p50_latency_ms || 0) / 1000).toFixed(2)}s
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">p95 Latency</span>
                <span className="text-sm font-semibold text-gray-900">
                  {((stats.performance?.p95_latency_ms || 0) / 1000).toFixed(2)}s
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">p99 Latency</span>
                <span className="text-sm font-semibold text-gray-900">
                  {((stats.performance?.p99_latency_ms || 0) / 1000).toFixed(2)}s
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">Mean Latency</span>
                <span className="text-sm font-semibold text-gray-900">
                  {((stats.performance?.mean_latency_ms || 0) / 1000).toFixed(2)}s
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">Min Latency</span>
                <span className="text-sm font-semibold text-gray-900">
                  {((stats.performance?.min_latency_ms || 0) / 1000).toFixed(2)}s
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-gray-600">Max Latency</span>
                <span className="text-sm font-semibold text-gray-900">
                  {((stats.performance?.max_latency_ms || 0) / 1000).toFixed(2)}s
                </span>
              </div>
            </div>
          </div>

          {/* Engagement Details */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FaUsers className="h-5 w-5 text-gray-600" />
              Engagement Details
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">Total Users</span>
                <span className="text-sm font-semibold text-gray-900">
                  {(stats.engagement?.total_users || 0).toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">Active Users</span>
                <span className="text-sm font-semibold text-gray-900">
                  {(stats.engagement?.active_users || 0).toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">Recommendations Sent</span>
                <span className="text-sm font-semibold text-gray-900">
                  {(stats.engagement?.recommendations_sent || 0).toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">Recommendations Viewed</span>
                <span className="text-sm font-semibold text-gray-900">
                  {(stats.engagement?.recommendations_viewed || 0).toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-gray-600">Recommendations Actioned</span>
                <span className="text-sm font-semibold text-gray-900">
                  {(stats.engagement?.recommendations_actioned || 0).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OperatorAnalytics
