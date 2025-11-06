import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  recommendationsService,
  type Recommendation,
} from '@/services/recommendationsService'
import {
  FaArrowLeft,
  FaExclamationTriangle,
  FaCheckCircle,
  FaTimesCircle,
  FaClock,
  FaInfoCircle,
  FaBookmark,
  FaBookmark as FaBookmarkSolid,
  FaTimes,
  FaShare,
  FaSpinner,
} from 'react-icons/fa'
import ExplanationSection from '@/components/ExplanationSection'
import { formatContent } from '@/utils/formatMarkdown'

/**
 * Financial advice disclaimer text
 * This disclaimer is prominently displayed on every recommendation detail page.
 */
const FINANCIAL_ADVICE_DISCLAIMER = `This is educational content, not financial advice. Consult a licensed advisor for personalized guidance.`

interface FeedbackFormData {
  rating: number | null
  helpful: boolean | null
  comment: string
}

const RecommendationDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Feedback form state
  const [feedbackForm, setFeedbackForm] = useState<FeedbackFormData>({
    rating: null,
    helpful: null,
    comment: '',
  })
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)

  // Fetch recommendation detail
  const {
    data: recommendation,
    isLoading,
    isError,
    error,
  } = useQuery<Recommendation>({
    queryKey: ['recommendation', id],
    queryFn: () => recommendationsService.getRecommendationDetail(id!),
    enabled: !!id,
  })

  // Fetch related recommendations (same type, different ID)
  const { data: relatedRecommendations } = useQuery({
    queryKey: ['recommendations', { type: recommendation?.type, limit: 3 }],
    queryFn: () =>
      recommendationsService.getRecommendations({
        type: recommendation?.type,
        status: 'approved',
        limit: 4, // Get 4 to show 3 after filtering current one
      }),
    enabled: !!recommendation?.type,
  })

  // Submit feedback mutation
  const submitFeedbackMutation = useMutation({
    mutationFn: (feedback: { rating?: number; helpful?: boolean; comment?: string }) =>
      recommendationsService.submitFeedback(id!, feedback),
    onSuccess: () => {
      setFeedbackSubmitted(true)
      setShowFeedbackForm(false)
      // Reset form after 3 seconds
      setTimeout(() => {
        setFeedbackForm({ rating: null, helpful: null, comment: '' })
        setFeedbackSubmitted(false)
      }, 3000)
    },
  })

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: () => recommendationsService.saveRecommendation(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] })
    },
  })

  // Dismiss mutation
  const dismissMutation = useMutation({
    mutationFn: () => recommendationsService.dismissRecommendation(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] })
      navigate('/recommendations')
    },
  })

  // Local state for saved status (until backend supports it)
  const [isSaved, setIsSaved] = useState(false)

  const handleSave = () => {
    saveMutation.mutate()
    setIsSaved(!isSaved)
  }

  const handleDismiss = () => {
    if (confirm('Are you sure you want to dismiss this recommendation?')) {
      dismissMutation.mutate()
    }
  }

  const handleSubmitFeedback = () => {
    if (feedbackForm.rating || feedbackForm.helpful !== null || feedbackForm.comment.trim()) {
      submitFeedbackMutation.mutate({
        rating: feedbackForm.rating || undefined,
        helpful: feedbackForm.helpful !== null ? feedbackForm.helpful : undefined,
        comment: feedbackForm.comment.trim() || undefined,
      })
    }
  }

  const handleShare = async () => {
    if (navigator.share && recommendation) {
      try {
        await navigator.share({
          title: recommendation.title,
          text: recommendation.content.substring(0, 200) + '...',
          url: window.location.href,
        })
      } catch (err) {
        // User cancelled or error occurred
        console.log('Share cancelled or failed')
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href)
      alert('Link copied to clipboard!')
    }
  }


  // Extract cited data points from decision trace or rationale
  const extractDataPoints = (): string[] => {
    if (!recommendation) return []

    const dataPoints: string[] = []
    const decisionTrace = recommendation.decision_trace

    if (decisionTrace) {
      // Extract account information
      if (decisionTrace.detected_signals) {
        const signals = decisionTrace.detected_signals

        // Subscription signals
        if (signals.subscriptions?.merchants) {
          signals.subscriptions.merchants.forEach((m: any) => {
            if (m.merchant_name) {
              dataPoints.push(`Subscription: ${m.merchant_name} (${m.cadence || 'monthly'})`)
            }
            if (m.monthly_recurring_spend) {
              dataPoints.push(
                `Monthly recurring spend: $${m.monthly_recurring_spend?.toFixed(2) || '0.00'}`
              )
            }
          })
        }

        // Credit signals
        if (signals.credit?.cards) {
          signals.credit.cards.forEach((c: any) => {
            if (c.account_name && c.utilization) {
              dataPoints.push(
                `Credit utilization: ${c.account_name} at ${(c.utilization * 100).toFixed(1)}%`
              )
            }
          })
        }

        // Savings signals
        if (signals.savings) {
          if (signals.savings.net_inflow) {
            dataPoints.push(
              `Net savings inflow: $${signals.savings.net_inflow?.toFixed(2) || '0.00'}`
            )
          }
          if (signals.savings.emergency_fund_coverage) {
            dataPoints.push(
              `Emergency fund coverage: ${signals.savings.emergency_fund_coverage?.toFixed(1) || '0'} months`
            )
          }
        }

        // Income signals
        if (signals.income) {
          if (signals.income.average_monthly_income) {
            dataPoints.push(
              `Average monthly income: $${signals.income.average_monthly_income?.toFixed(2) || '0.00'}`
            )
          }
          if (signals.income.cash_flow_buffer) {
            dataPoints.push(
              `Cash flow buffer: ${signals.income.cash_flow_buffer?.toFixed(1) || '0'} months`
            )
          }
        }
      }

      // Extract eligibility information
      if (decisionTrace.guardrails?.eligibility) {
        const eligibility = decisionTrace.guardrails.eligibility
        if (eligibility.estimated_income) {
          dataPoints.push(`Estimated income: $${eligibility.estimated_income?.toFixed(2) || '0.00'}`)
        }
        if (eligibility.estimated_credit_score) {
          dataPoints.push(`Estimated credit score: ${eligibility.estimated_credit_score}`)
        }
      }
    }

    return dataPoints
  }

  // Get status badge
  const getStatusBadge = () => {
    if (!recommendation) return null

    switch (recommendation.status) {
      case 'approved':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 text-sm font-medium rounded-full bg-green-100 text-green-700">
            <FaCheckCircle className="h-4 w-4" />
            Approved
          </span>
        )
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 text-sm font-medium rounded-full bg-yellow-100 text-yellow-700">
            <FaClock className="h-4 w-4" />
            Pending Review
          </span>
        )
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 text-sm font-medium rounded-full bg-red-100 text-red-700">
            <FaTimesCircle className="h-4 w-4" />
            Rejected
          </span>
        )
    }
  }

  // Get type badge
  const getTypeBadge = () => {
    if (!recommendation) return null

    return recommendation.type === 'education' ? (
      <span className="px-3 py-1 text-sm font-medium rounded-full bg-blue-100 text-blue-700">
        Education
      </span>
    ) : (
      <span className="px-3 py-1 text-sm font-medium rounded-full bg-purple-100 text-purple-700">
        Partner Offer
      </span>
    )
  }

  // Get eligibility badge
  const getEligibilityBadge = () => {
    if (!recommendation || recommendation.type !== 'partner_offer') return null

    const eligibility = recommendation.eligibility_status || 'pending'
    switch (eligibility) {
      case 'eligible':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 text-sm font-medium rounded-full bg-green-100 text-green-700">
            <FaCheckCircle className="h-4 w-4" />
            Eligible
          </span>
        )
      case 'ineligible':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 text-sm font-medium rounded-full bg-gray-100 text-gray-700">
            <FaTimesCircle className="h-4 w-4" />
            Not Eligible
          </span>
        )
      case 'pending':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 text-sm font-medium rounded-full bg-yellow-100 text-yellow-700">
            <FaClock className="h-4 w-4" />
            Eligibility Pending
          </span>
        )
    }
  }

  // Filter related recommendations (exclude current one)
  const filteredRelated = relatedRecommendations?.items.filter(
    (rec) => rec.recommendation_id !== recommendation?.recommendation_id
  ).slice(0, 3) || []

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-6">
            {/* Header skeleton */}
            <div className="h-8 bg-gray-200 rounded w-32 animate-pulse"></div>

            {/* Content skeleton */}
            <div className="bg-white rounded-lg shadow-sm p-8">
              <div className="space-y-4">
                <div className="h-8 bg-gray-200 rounded w-3/4 animate-pulse"></div>
                <div className="h-4 bg-gray-200 rounded w-full animate-pulse"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse"></div>
                <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (isError || !recommendation) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <FaExclamationTriangle className="mx-auto h-12 w-12 text-red-600 mb-4" />
            <h3 className="text-lg font-semibold text-red-900 mb-2">
              Failed to load recommendation
            </h3>
            <p className="text-sm text-red-700 mb-4">
              {error instanceof Error ? error.message : 'Recommendation not found'}
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => navigate('/recommendations')}
                className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
              >
                <FaArrowLeft className="h-4 w-4" />
                Back to Recommendations
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const dataPoints = extractDataPoints()

  return (
    <div className="min-h-screen bg-gray-50 pt-2 pb-6">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Navigation */}
        <button
          onClick={() => navigate('/recommendations')}
          className="mb-2 inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
        >
          <FaArrowLeft className="h-4 w-4" />
          <span className="text-sm font-medium">Back to Recommendations</span>
        </button>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-50 to-primary-100 px-8 py-4 border-b border-primary-200">
            <div className="flex flex-wrap items-center gap-3 mb-3">
              {getTypeBadge()}
              {getStatusBadge()}
              {getEligibilityBadge()}
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1">{recommendation.title}</h1>
            {recommendation.partner_name && (
              <p className="text-lg text-gray-700">From {recommendation.partner_name}</p>
            )}
            <p className="text-sm text-gray-500 mt-1">
              Created {new Date(recommendation.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>

          {/* Regulatory Disclaimer - Compact */}
          <div className="px-8 py-2 bg-gray-50 border-t border-gray-200">
            <p className="text-xs text-gray-700 leading-relaxed">
              <span className="font-semibold">Disclaimer:</span> {FINANCIAL_ADVICE_DISCLAIMER}
            </p>
          </div>

          {/* Content */}
          <div className="px-8 py-4">
            <div className="max-w-none mb-6">
              {formatContent(recommendation.content)}
            </div>

            {/* Explanation Section - RAG Context */}
            {recommendation.explanation && (
              <div className="mb-6">
                <ExplanationSection explanation={recommendation.explanation} />
              </div>
            )}

            {/* Detailed Rationale */}
            {recommendation.rationale && (
              <div className="mb-6 p-5 bg-blue-50 border-l-4 border-blue-400 rounded-r-lg">
                <div className="flex items-start gap-3">
                  <FaInfoCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h2 className="text-lg font-semibold text-blue-900 mb-2">Why This Matters</h2>
                    <p className="text-blue-800 leading-relaxed mb-3">
                      {recommendation.rationale
                        .replace(/\*\*Disclaimer\*\*:?\s*This is educational content.*?guidance\./gi, '')
                        .replace(/This is educational content, not financial advice.*?guidance\./gi, '')
                        .trim()}
                    </p>

                    {/* Cited Data Points */}
                    {dataPoints.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-blue-200">
                        <p className="text-sm font-semibold text-blue-900 mb-1">
                          Based on Your Data:
                        </p>
                        <ul className="space-y-1">
                          {dataPoints.map((point, index) => (
                            <li key={index} className="text-sm text-blue-800 flex items-start gap-2">
                              <span className="text-blue-600 mt-1">•</span>
                              <span>{point}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Eligibility Explanation (Partner Offers) */}
            {recommendation.type === 'partner_offer' && recommendation.eligibility_reason && (
              <div className="mb-6 p-5 bg-gray-50 border-l-4 border-gray-400 rounded-r-lg">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Eligibility Status</h2>
                <p className="text-gray-700 leading-relaxed">{recommendation.eligibility_reason}</p>
              </div>
            )}

            {/* Partner Offer Details */}
            {recommendation.type === 'partner_offer' && recommendation.offer_details && (
              <div className="mb-6 p-5 bg-purple-50 border border-purple-200 rounded-lg">
                <h2 className="text-lg font-semibold text-purple-900 mb-2">Offer Details</h2>
                <div className="space-y-2 text-sm text-purple-800">
                  {Object.entries(recommendation.offer_details).map(([key, value]) => (
                    <div key={key} className="flex">
                      <span className="font-medium capitalize w-32">{key.replace(/_/g, ' ')}:</span>
                      <span>{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-gray-200">
              <button
                onClick={handleSave}
                disabled={saveMutation.isPending}
                className={`inline-flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors duration-200 text-sm font-medium ${
                  isSaved
                    ? 'bg-primary-50 border-primary-300 text-primary-700 hover:bg-primary-100'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {saveMutation.isPending ? (
                  <FaSpinner className="h-4 w-4 animate-spin" />
                ) : isSaved ? (
                  <FaBookmarkSolid className="h-4 w-4" />
                ) : (
                  <FaBookmark className="h-4 w-4" />
                )}
                {isSaved ? 'Saved' : 'Save'}
              </button>
              <button
                onClick={handleShare}
                className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 text-sm font-medium"
              >
                <FaShare className="h-4 w-4" />
                Share
              </button>
              <button
                onClick={handleDismiss}
                disabled={dismissMutation.isPending}
                className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {dismissMutation.isPending ? (
                  <FaSpinner className="h-4 w-4 animate-spin" />
                ) : (
                  <FaTimes className="h-4 w-4" />
                )}
                Dismiss
              </button>
              <button
                onClick={() => setShowFeedbackForm(!showFeedbackForm)}
                className="ml-auto inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200 text-sm font-medium"
              >
                {feedbackSubmitted ? '✓ Feedback Submitted' : 'Provide Feedback'}
              </button>
            </div>

            {/* Feedback Form */}
            {showFeedbackForm && !feedbackSubmitted && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Your Feedback</h3>
                <div className="space-y-4">
                  {/* Rating */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      How helpful was this recommendation?
                    </label>
                    <div className="flex gap-2">
                      {[1, 2, 3, 4, 5].map((rating) => (
                        <button
                          key={rating}
                          onClick={() => setFeedbackForm({ ...feedbackForm, rating })}
                          className={`px-4 py-2 border rounded-lg transition-colors duration-200 ${
                            feedbackForm.rating === rating
                              ? 'bg-primary-600 text-white border-primary-600'
                              : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          {rating}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Helpful */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Was this recommendation helpful?
                    </label>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setFeedbackForm({ ...feedbackForm, helpful: true })}
                        className={`px-4 py-2 border rounded-lg transition-colors duration-200 ${
                          feedbackForm.helpful === true
                            ? 'bg-green-600 text-white border-green-600'
                            : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        Yes
                      </button>
                      <button
                        onClick={() => setFeedbackForm({ ...feedbackForm, helpful: false })}
                        className={`px-4 py-2 border rounded-lg transition-colors duration-200 ${
                          feedbackForm.helpful === false
                            ? 'bg-red-600 text-white border-red-600'
                            : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        No
                      </button>
                    </div>
                  </div>

                  {/* Comment */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Comments (Optional)
                    </label>
                    <textarea
                      value={feedbackForm.comment}
                      onChange={(e) =>
                        setFeedbackForm({ ...feedbackForm, comment: e.target.value })
                      }
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Share your thoughts..."
                    />
                  </div>

                  {/* Submit Button */}
                  <div className="flex gap-3">
                    <button
                      onClick={handleSubmitFeedback}
                      disabled={submitFeedbackMutation.isPending}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {submitFeedbackMutation.isPending ? (
                        <span className="flex items-center gap-2">
                          <FaSpinner className="h-4 w-4 animate-spin" />
                          Submitting...
                        </span>
                      ) : (
                        'Submit Feedback'
                      )}
                    </button>
                    <button
                      onClick={() => {
                        setShowFeedbackForm(false)
                        setFeedbackForm({ rating: null, helpful: null, comment: '' })
                      }}
                      className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Feedback Submitted Success */}
            {feedbackSubmitted && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  ✓ Thank you for your feedback! Your input helps us improve our recommendations.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Related Recommendations */}
        {filteredRelated.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Related Recommendations</h2>
            <div className="space-y-4">
              {filteredRelated.map((rec) => (
                <Link
                  key={rec.recommendation_id}
                  to={`/recommendations/${rec.recommendation_id}`}
                  className="block bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">{rec.title}</h3>
                      <p className="text-sm text-gray-600 line-clamp-2">{rec.content}</p>
                      {rec.rationale && (
                        <p className="text-xs text-gray-500 mt-2 line-clamp-1">
                          {rec.rationale}
                        </p>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default RecommendationDetail
