import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  recommendationsService,
  type Recommendation,
  type RecommendationsFilters,
} from '@/services/recommendationsService'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import EmptyState from '@/components/EmptyState'
import {
  FaFilter,
  FaSort,
  FaChevronDown,
  FaChevronUp,
  FaEye,
  FaTimes,
  FaBookmark,
  FaBookmark as FaBookmarkSolid,
  FaCheckCircle,
  FaTimesCircle,
  FaClock,
  FaInfoCircle,
  FaUpload,
} from 'react-icons/fa'

type SortOption = 'date' | 'relevance' | 'type'
type SortOrder = 'asc' | 'desc'
type FilterType = 'education' | 'partner_offer' | 'all'
type FilterStatus = 'approved' | 'pending' | 'rejected' | 'all'

const Recommendations = () => {
  const queryClient = useQueryClient()

  // Filter and sort state
  const [typeFilter, setTypeFilter] = useState<FilterType>('all')
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('approved')
  const [sortBy, setSortBy] = useState<SortOption>('date')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [showFilters, setShowFilters] = useState(false)

  // Build filters object
  const filters: RecommendationsFilters = {
    type: typeFilter !== 'all' ? typeFilter : undefined,
    status: statusFilter !== 'all' ? statusFilter : undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
    limit: 50,
  }

  // Fetch recommendations
  const {
    data: recommendationsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['recommendations', filters],
    queryFn: () => recommendationsService.getRecommendations(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Dismiss mutation
  const dismissMutation = useMutation({
    mutationFn: (recommendationId: string) =>
      recommendationsService.dismissRecommendation(recommendationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] })
    },
  })

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: (recommendationId: string) =>
      recommendationsService.saveRecommendation(recommendationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] })
    },
  })

  // Local state for saved/dismissed recommendations (until backend supports it)
  const [savedRecommendations, setSavedRecommendations] = useState<Set<string>>(new Set())
  const [dismissedRecommendations, setDismissedRecommendations] = useState<Set<string>>(
    new Set()
  )

  const handleDismiss = (recommendationId: string) => {
    dismissMutation.mutate(recommendationId)
    setDismissedRecommendations((prev) => new Set([...prev, recommendationId]))
  }

  const handleSave = (recommendationId: string) => {
    saveMutation.mutate(recommendationId)
    setSavedRecommendations((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(recommendationId)) {
        newSet.delete(recommendationId)
      } else {
        newSet.add(recommendationId)
      }
      return newSet
    })
  }

  // Sort recommendations locally (in case backend doesn't support sorting)
  const sortedRecommendations = recommendationsData?.items
    ? [...recommendationsData.items].sort((a, b) => {
        // Filter out dismissed recommendations
        if (dismissedRecommendations.has(a.recommendation_id)) return 1
        if (dismissedRecommendations.has(b.recommendation_id)) return -1

        switch (sortBy) {
          case 'date':
            return sortOrder === 'asc'
              ? new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
              : new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          case 'type':
            return sortOrder === 'asc'
              ? a.type.localeCompare(b.type)
              : b.type.localeCompare(a.type)
          case 'relevance':
            // For now, use status as relevance proxy (approved > pending > rejected)
            const statusOrder = { approved: 3, pending: 2, rejected: 1 }
            return sortOrder === 'asc'
              ? statusOrder[a.status] - statusOrder[b.status]
              : statusOrder[b.status] - statusOrder[a.status]
          default:
            return 0
        }
      })
    : []

  // Filter out dismissed recommendations
  const visibleRecommendations = sortedRecommendations.filter(
    (rec) => !dismissedRecommendations.has(rec.recommendation_id)
  )

  // Loading skeleton
  if (isLoading) {
    return <PageSkeleton sections={3} />
  }

  // Error state
  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorState
            title="Failed to load recommendations"
            error={error}
            onRetry={() => refetch()}
            retryLabel="Retry"
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-6 lg:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Recommendations</h1>
          <p className="mt-2 text-sm text-gray-600">
            Personalized financial education and partner offers tailored to your behavior
          </p>
        </header>

        {/* Filters and Sort */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="w-full flex items-center justify-between text-left font-medium text-gray-900 hover:text-primary-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            aria-expanded={showFilters}
            aria-controls="filters-content"
          >
            <div className="flex items-center gap-2">
              <FaFilter className="h-4 w-4" aria-hidden="true" />
              <span>Filters & Sort</span>
            </div>
            {showFilters ? (
              <FaChevronUp className="h-4 w-4" aria-hidden="true" />
            ) : (
              <FaChevronDown className="h-4 w-4" aria-hidden="true" />
            )}
          </button>

          {showFilters && (
            <div id="filters-content" className="mt-4 pt-4 border-t border-gray-200 space-y-4">
              {/* Type Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                <div className="flex flex-wrap gap-2">
                  {(['all', 'education', 'partner_offer'] as FilterType[]).map((type) => (
                    <button
                      key={type}
                      onClick={() => setTypeFilter(type)}
                      className={`px-3 py-1.5 text-sm rounded-lg transition-colors duration-200 ${
                        typeFilter === type
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {type === 'all'
                        ? 'All Types'
                        : type === 'education'
                          ? 'Education'
                          : 'Partner Offers'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <div className="flex flex-wrap gap-2">
                  {(['all', 'approved', 'pending', 'rejected'] as FilterStatus[]).map(
                    (status) => (
                      <button
                        key={status}
                        onClick={() => setStatusFilter(status)}
                        className={`px-3 py-1.5 text-sm rounded-lg transition-colors duration-200 ${
                          statusFilter === status
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {status === 'all'
                          ? 'All Statuses'
                          : status.charAt(0).toUpperCase() + status.slice(1)}
                      </button>
                    )
                  )}
                </div>
              </div>

              {/* Sort */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <FaSort className="inline h-3 w-3 mr-1" />
                  Sort By
                </label>
                <div className="flex flex-wrap gap-2">
                  {(['date', 'relevance', 'type'] as SortOption[]).map((option) => (
                    <button
                      key={option}
                      onClick={() => {
                        if (sortBy === option) {
                          setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
                        } else {
                          setSortBy(option)
                          setSortOrder('desc')
                        }
                      }}
                      className={`px-3 py-1.5 text-sm rounded-lg transition-colors duration-200 ${
                        sortBy === option
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                      {sortBy === option && (
                        <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results count */}
        {recommendationsData && (
          <div className="mb-4 text-sm text-gray-600">
            Showing {visibleRecommendations.length} of {recommendationsData.total} recommendations
          </div>
        )}

        {/* Empty state */}
        {visibleRecommendations.length === 0 ? (
          <EmptyState
            title="No recommendations found"
            description={
              recommendationsData?.total === 0
                ? "We don't have any recommendations for you yet. Upload your transaction data to get started!"
                : 'Try adjusting your filters to see more recommendations.'
            }
            action={
              recommendationsData?.total === 0
                ? {
                    label: 'Upload Transaction Data',
                    to: '/upload',
                    icon: <FaUpload className="h-5 w-5" aria-hidden="true" />,
                  }
                : undefined
            }
          />
        ) : (
          /* Recommendations List */
          <div className="space-y-4">
            {visibleRecommendations.map((rec) => (
              <RecommendationCard
                key={rec.recommendation_id}
                recommendation={rec}
                isSaved={savedRecommendations.has(rec.recommendation_id)}
                onDismiss={() => handleDismiss(rec.recommendation_id)}
                onSave={() => handleSave(rec.recommendation_id)}
                isDismissing={dismissMutation.isPending}
                isSaving={saveMutation.isPending}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

interface RecommendationCardProps {
  recommendation: Recommendation
  isSaved: boolean
  onDismiss: () => void
  onSave: () => void
  isDismissing: boolean
  isSaving: boolean
}

const RecommendationCard = ({
  recommendation,
  isSaved,
  onDismiss,
  onSave,
  isDismissing,
  isSaving,
}: RecommendationCardProps) => {
  const getStatusBadge = () => {
    switch (recommendation.status) {
      case 'approved':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-700">
            <FaCheckCircle className="h-3 w-3" />
            Approved
          </span>
        )
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded bg-yellow-100 text-yellow-700">
            <FaClock className="h-3 w-3" />
            Pending
          </span>
        )
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-700">
            <FaTimesCircle className="h-3 w-3" />
            Rejected
          </span>
        )
    }
  }

  const getTypeBadge = () => {
    return recommendation.type === 'education' ? (
      <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-700">
        Education
      </span>
    ) : (
      <span className="px-2 py-1 text-xs font-medium rounded bg-purple-100 text-purple-700">
        Partner Offer
      </span>
    )
  }

  const getEligibilityBadge = () => {
    if (recommendation.type !== 'partner_offer') return null

    const eligibility = recommendation.eligibility_status || 'pending'
    switch (eligibility) {
      case 'eligible':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-700">
            <FaCheckCircle className="h-3 w-3" />
            Eligible
          </span>
        )
      case 'ineligible':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-700">
            <FaTimesCircle className="h-3 w-3" />
            Not Eligible
          </span>
        )
      case 'pending':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded bg-yellow-100 text-yellow-700">
            <FaClock className="h-3 w-3" />
            Eligibility Pending
          </span>
        )
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            {getTypeBadge()}
            {getStatusBadge()}
            {getEligibilityBadge()}
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-1">{recommendation.title}</h3>
          {recommendation.partner_name && (
            <p className="text-sm text-gray-600 mb-2">From {recommendation.partner_name}</p>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="mb-4">
        <p className="text-gray-700 leading-relaxed">{recommendation.content}</p>
      </div>

      {/* "Because" Section */}
      {recommendation.rationale && (
        <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-400 rounded-r">
          <div className="flex items-start gap-2">
            <FaInfoCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-blue-900 mb-1">Because:</p>
              <p className="text-sm text-blue-800 leading-relaxed">{recommendation.rationale}</p>
            </div>
          </div>
        </div>
      )}

      {/* Eligibility Reason (for partner offers) */}
      {recommendation.type === 'partner_offer' &&
        recommendation.eligibility_reason &&
        recommendation.eligibility_status === 'ineligible' && (
          <div className="mb-4 p-4 bg-gray-50 border-l-4 border-gray-400 rounded-r">
            <p className="text-sm font-semibold text-gray-900 mb-1">Eligibility Note:</p>
            <p className="text-sm text-gray-700">{recommendation.eligibility_reason}</p>
          </div>
        )}

      {/* Actions */}
      <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-gray-200">
        <Link
          to={`/recommendations/${recommendation.recommendation_id}`}
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200 text-sm font-medium"
          aria-label={`View details for ${recommendation.title}`}
        >
          <FaEye className="h-4 w-4" aria-hidden="true" />
          View Details
        </Link>
        <button
          onClick={onSave}
          disabled={isSaving}
          className={`inline-flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors duration-200 text-sm font-medium ${
            isSaved
              ? 'bg-primary-50 border-primary-300 text-primary-700 hover:bg-primary-100'
              : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
          } disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
          aria-label={isSaved ? `Unsave ${recommendation.title}` : `Save ${recommendation.title}`}
        >
          {isSaved ? (
            <FaBookmarkSolid className="h-4 w-4" aria-hidden="true" />
          ) : (
            <FaBookmark className="h-4 w-4" aria-hidden="true" />
          )}
          {isSaved ? 'Saved' : 'Save'}
        </button>
        <button
          onClick={onDismiss}
          disabled={isDismissing}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label={`Dismiss ${recommendation.title}`}
        >
          <FaTimes className="h-4 w-4" aria-hidden="true" />
          Dismiss
        </button>
        <span className="text-xs text-gray-500 ml-auto">
          {new Date(recommendation.created_at).toLocaleDateString()}
        </span>
      </div>
    </div>
  )
}

export default Recommendations
