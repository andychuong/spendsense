import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { operatorService, type ReviewQueueItem } from '@/services/operatorService'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import PersonaBadge from '@/components/PersonaBadge'
import { FaCheckCircle, FaTimesCircle, FaClock, FaEye } from 'react-icons/fa'

interface ReviewQueueProps {
  limit?: number
}

const ReviewQueue = ({ limit = 20 }: ReviewQueueProps) => {
  const {
    data: queueData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['operator', 'review-queue', limit],
    queryFn: () => operatorService.getReviewQueue({ limit, status: 'pending' }),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Auto-refresh every minute
  })

  if (isLoading) {
    return <PageSkeleton sections={1} />
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load review queue"
        error={error}
        onRetry={() => refetch()}
        retryLabel="Retry"
      />
    )
  }

  if (!queueData || queueData.items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="text-center py-8">
          <FaCheckCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Reviews</h3>
          <p className="text-sm text-gray-500">
            All recommendations have been reviewed. Great job!
          </p>
        </div>
      </div>
    )
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <FaClock className="h-3 w-3" />
            Pending
          </span>
        )
      case 'approved':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <FaCheckCircle className="h-3 w-3" />
            Approved
          </span>
        )
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <FaTimesCircle className="h-3 w-3" />
            Rejected
          </span>
        )
      default:
        return null
    }
  }

  const getTypeBadge = (type: string) => {
    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          type === 'education'
            ? 'bg-blue-100 text-blue-800'
            : 'bg-purple-100 text-purple-800'
        }`}
      >
        {type === 'education' ? 'Education' : 'Partner Offer'}
      </span>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Review Queue ({queueData.total})
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Recommendations pending review
          </p>
        </div>
        <Link
          to="/operator/review"
          className="text-sm font-medium text-primary-600 hover:text-primary-700"
        >
          View All →
        </Link>
      </div>
      <div className="divide-y divide-gray-200">
        {queueData.items.map((item: ReviewQueueItem) => (
          <Link
            key={item.recommendation_id}
            to={`/operator/review/${item.recommendation_id}`}
            className="block px-6 py-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  {getStatusBadge(item.status)}
                  {getTypeBadge(item.type)}
                  {item.persona_name && (
                    <PersonaBadge
                      personaId={item.persona_id!}
                      personaName={item.persona_name}
                    />
                  )}
                </div>
                <h4 className="text-sm font-medium text-gray-900 truncate mb-1">
                  {item.title}
                </h4>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  {item.user_name && (
                    <span className="truncate">{item.user_name}</span>
                  )}
                  {item.user_email && (
                    <span className="truncate">{item.user_email}</span>
                  )}
                  <span>
                    {new Date(item.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </span>
                </div>
              </div>
              <div className="ml-4 flex-shrink-0">
                <FaEye className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </Link>
        ))}
      </div>
      {queueData.total > limit && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <Link
            to="/operator/review"
            className="text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            View all {queueData.total} recommendations →
          </Link>
        </div>
      )}
    </div>
  )
}

export default ReviewQueue


