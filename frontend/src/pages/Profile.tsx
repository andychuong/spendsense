import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { profileService, type ProfileData } from '@/services/profileService'
import PersonaBadge from '@/components/PersonaBadge'
import TimePeriodSelector from '@/components/TimePeriodSelector'
import ProfileBehavioralSignals from '@/components/ProfileBehavioralSignals'
import PersonaHistoryTimeline from '@/components/PersonaHistoryTimeline'
import SignalTrends from '@/components/SignalTrends'
import { FaDownload, FaExclamationTriangle, FaSync } from 'react-icons/fa'

const Profile = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<'30d' | '180d'>('30d')

  const {
    data: profileData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<ProfileData>({
    queryKey: ['profile'],
    queryFn: () => profileService.getProfile(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const handleExport = async (format: 'pdf' | 'csv') => {
    try {
      // This will be implemented when the backend export endpoint is ready
      alert(`Export functionality will be available soon. Format: ${format.toUpperCase()}`)
    } catch (err) {
      console.error('Export error:', err)
      alert('Export failed. Please try again later.')
    }
  }

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-6">
            {/* Header skeleton */}
            <div className="h-8 bg-gray-200 rounded w-64 animate-pulse"></div>

            {/* Time period selector skeleton */}
            <div className="h-12 bg-gray-200 rounded-lg animate-pulse"></div>

            {/* Persona skeleton */}
            <div className="h-32 bg-gray-200 rounded-lg animate-pulse"></div>

            {/* Signals skeleton */}
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-48 bg-gray-200 rounded-lg animate-pulse"></div>
              ))}
            </div>

            {/* Timeline skeleton */}
            <div className="h-64 bg-gray-200 rounded-lg animate-pulse"></div>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <FaExclamationTriangle className="mx-auto h-12 w-12 text-red-600 mb-4" />
            <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to load profile</h3>
            <p className="text-sm text-red-700 mb-4">
              {error instanceof Error ? error.message : 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => refetch()}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
            >
              <FaSync className="h-4 w-4" />
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Empty state for new users
  if (!profileData?.behavioralProfile) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Profile</h1>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Your behavioral profile will appear here once you upload transaction data and it's
              been processed.
            </p>
            <a
              href="/upload"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200 font-medium"
            >
              Upload Transaction Data
            </a>
          </div>
        </div>
      </div>
    )
  }

  const { behavioralProfile, personaHistory } = profileData

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
            <p className="mt-2 text-sm text-gray-600">
              Your behavioral profile and financial insights
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleExport('csv')}
              className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 text-sm font-medium"
            >
              <FaDownload className="h-4 w-4" />
              Export CSV
            </button>
            <button
              onClick={() => handleExport('pdf')}
              className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 text-sm font-medium"
            >
              <FaDownload className="h-4 w-4" />
              Export PDF
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {/* Current Persona */}
          {behavioralProfile && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Current Persona</h2>
              <PersonaBadge
                personaId={behavioralProfile.persona_id}
                personaName={behavioralProfile.persona_name}
              />
            </div>
          )}

          {/* Time Period Selector */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Analysis Period</h2>
              <p className="text-sm text-gray-600">
                Select a time period to view behavioral signals and trends
              </p>
            </div>
            <TimePeriodSelector
              selectedPeriod={selectedPeriod}
              onPeriodChange={setSelectedPeriod}
            />
          </div>

          {/* Behavioral Signals */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Behavioral Signals ({selectedPeriod === '30d' ? '30-Day' : '180-Day'})
            </h2>
            <ProfileBehavioralSignals
              signals30d={behavioralProfile?.signals_30d}
              signals180d={behavioralProfile?.signals_180d}
              selectedPeriod={selectedPeriod}
            />
          </div>

          {/* Signal Trends */}
          {(behavioralProfile?.signals_30d || behavioralProfile?.signals_180d) && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <SignalTrends
                signals30d={behavioralProfile.signals_30d}
                signals180d={behavioralProfile.signals_180d}
              />
            </div>
          )}

          {/* Persona History Timeline */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <PersonaHistoryTimeline history={personaHistory} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
