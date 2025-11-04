import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { profileService, type ProfileData } from '@/services/profileService'
import PersonaBadge from '@/components/PersonaBadge'
import TimePeriodSelector from '@/components/TimePeriodSelector'
import ProfileBehavioralSignals from '@/components/ProfileBehavioralSignals'
import PersonaHistoryTimeline from '@/components/PersonaHistoryTimeline'
import SignalTrends from '@/components/SignalTrends'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import EmptyState from '@/components/EmptyState'
import { FaDownload, FaUpload } from 'react-icons/fa'

const Profile = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<'30d' | '180d' | '365d'>('30d')

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
    return <PageSkeleton sections={5} />
  }

  // Error state
  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorState
            title="Failed to load profile"
            error={error}
            onRetry={() => refetch()}
            retryLabel="Retry"
          />
        </div>
      </div>
    )
  }

  // Empty state for new users
  if (!profileData?.behavioralProfile) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <header className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile</h1>
          </header>

          <EmptyState
            title="No Profile Data Yet"
            description="Your behavioral profile will appear here once you upload transaction data and it's been processed."
            action={{
              label: 'Upload Transaction Data',
              to: '/upload',
              icon: <FaUpload className="h-5 w-5" aria-hidden="true" />,
            }}
          />
        </div>
      </div>
    )
  }

  const { behavioralProfile, personaHistory } = profileData

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-6 lg:mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Profile</h1>
            <p className="mt-2 text-sm text-gray-600">
              Your behavioral profile and financial insights
            </p>
          </div>
          <div className="flex gap-2 w-full sm:w-auto">
            <button
              onClick={() => handleExport('csv')}
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 text-sm font-medium touch-manipulation"
              aria-label="Export profile data as CSV"
            >
              <FaDownload className="h-4 w-4" aria-hidden="true" />
              <span className="sm:hidden">CSV</span>
              <span className="hidden sm:inline">Export CSV</span>
            </button>
            <button
              onClick={() => handleExport('pdf')}
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 text-sm font-medium touch-manipulation"
              aria-label="Export profile data as PDF"
            >
              <FaDownload className="h-4 w-4" aria-hidden="true" />
              <span className="sm:hidden">PDF</span>
              <span className="hidden sm:inline">Export PDF</span>
            </button>
          </div>
        </header>

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
              Behavioral Signals ({selectedPeriod === '30d' ? '30-Day' : selectedPeriod === '180d' ? '180-Day' : '365-Day'})
            </h2>
            <ProfileBehavioralSignals
              signals30d={behavioralProfile?.signals_30d}
              signals180d={behavioralProfile?.signals_180d}
              signals365d={behavioralProfile?.signals_365d}
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
