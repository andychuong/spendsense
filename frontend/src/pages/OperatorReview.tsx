import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  operatorService,
  type RecommendationReviewDetail,
  type DecisionTrace,
  type GuardrailsInfo,
} from '@/services/operatorService'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import PersonaBadge from '@/components/PersonaBadge'
import ConfirmationDialog from '@/components/ConfirmationDialog'
import {
  FaArrowLeft,
  FaCheckCircle,
  FaTimesCircle,
  FaClock,
  FaChevronDown,
  FaChevronUp,
  FaCheck,
  FaBan,
  FaInfoCircle,
  FaShieldAlt,
  FaUser,
  FaCreditCard,
  FaPiggyBank,
  FaDollarSign,
  FaExclamationTriangle,
  FaSpinner,
  FaEdit,
  FaSave,
  FaTimes,
} from 'react-icons/fa'

const OperatorReview = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Expandable sections state
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['recommendation']))
  const [rejectReason, setRejectReason] = useState('')
  const [showRejectDialog, setShowRejectDialog] = useState(false)
  const [showApproveDialog, setShowApproveDialog] = useState(false)

  // Modify recommendation state
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState('')
  const [editedContent, setEditedContent] = useState('')
  const [editedRationale, setEditedRationale] = useState('')

  // Fetch recommendation detail
  const {
    data: recommendation,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<RecommendationReviewDetail>({
    queryKey: ['operator', 'recommendation-review', id],
    queryFn: () => operatorService.getRecommendationForReview(id!),
    enabled: !!id,
  })

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: () => operatorService.approveRecommendation(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'review-queue'] })
      queryClient.invalidateQueries({ queryKey: ['operator', 'recommendation-review', id] })
      navigate('/operator/review')
    },
  })

  // Reject mutation
  const rejectMutation = useMutation({
    mutationFn: (reason: string) => operatorService.rejectRecommendation(id!, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'review-queue'] })
      queryClient.invalidateQueries({ queryKey: ['operator', 'recommendation-review', id] })
      navigate('/operator/review')
    },
  })

  // Modify recommendation mutation
  const modifyMutation = useMutation({
    mutationFn: (updates: { title?: string; content?: string; rationale?: string }) =>
      operatorService.modifyRecommendation(id!, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'review-queue'] })
      queryClient.invalidateQueries({ queryKey: ['operator', 'recommendation-review', id] })
      setIsEditing(false)
    },
  })

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const handleApprove = () => {
    setShowApproveDialog(true)
  }

  const handleConfirmApprove = () => {
    approveMutation.mutate()
    setShowApproveDialog(false)
  }

  const handleReject = () => {
    if (!rejectReason.trim()) {
      return
    }
    rejectMutation.mutate(rejectReason)
    setShowRejectDialog(false)
    setRejectReason('')
  }

  const handleStartEdit = () => {
    if (recommendation) {
      setEditedTitle(recommendation.title)
      setEditedContent(recommendation.content)
      setEditedRationale(recommendation.rationale)
      setIsEditing(true)
    }
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setEditedTitle('')
    setEditedContent('')
    setEditedRationale('')
  }

  const handleSaveEdit = () => {
    if (!recommendation) return

    const updates: { title?: string; content?: string; rationale?: string } = {}
    if (editedTitle !== recommendation.title) updates.title = editedTitle
    if (editedContent !== recommendation.content) updates.content = editedContent
    if (editedRationale !== recommendation.rationale) updates.rationale = editedRationale

    if (Object.keys(updates).length > 0) {
      modifyMutation.mutate(updates)
    } else {
      setIsEditing(false)
    }
  }

  const hasChanges = recommendation && (
    editedTitle !== recommendation.title ||
    editedContent !== recommendation.content ||
    editedRationale !== recommendation.rationale
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
            <FaClock className="h-3 w-3" />
            Pending Review
          </span>
        )
      case 'approved':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <FaCheckCircle className="h-3 w-3" />
            Approved
          </span>
        )
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
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
        className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
          type === 'education'
            ? 'bg-blue-100 text-blue-800'
            : 'bg-purple-100 text-purple-800'
        }`}
      >
        {type === 'education' ? 'Education' : 'Partner Offer'}
      </span>
    )
  }

  const formatCurrency = (amount: number | undefined): string => {
    if (amount === undefined || amount === null) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  const formatPercent = (value: number | undefined): string => {
    if (value === undefined || value === null) return 'N/A'
    return `${value.toFixed(1)}%`
  }

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (isLoading) {
    return <PageSkeleton sections={3} />
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorState
            title="Failed to load recommendation"
            error={error}
            onRetry={() => refetch()}
            retryLabel="Retry"
          />
        </div>
      </div>
    )
  }

  if (!recommendation) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <p className="text-gray-500">Recommendation not found</p>
          </div>
        </div>
      </div>
    )
  }

  const decisionTrace = recommendation.decision_trace

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-6 lg:mb-8">
          <Link
            to="/operator/review"
            className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <FaArrowLeft className="h-4 w-4" />
            Back to Review Queue
          </Link>
          <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                Recommendation Review
              </h1>
              <div className="flex items-center gap-2 flex-wrap">
                {getStatusBadge(recommendation.status)}
                {getTypeBadge(recommendation.type)}
                {recommendation.persona_name && (
                  <PersonaBadge
                    personaId={recommendation.persona_id!}
                    personaName={recommendation.persona_name}
                  />
                )}
              </div>
            </div>
            {recommendation.status === 'pending' && (
              <div className="flex items-center gap-2 flex-wrap">
                {isEditing ? (
                  <>
                    <button
                      onClick={handleSaveEdit}
                      disabled={modifyMutation.isPending || !hasChanges}
                      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {modifyMutation.isPending ? (
                        <>
                          <FaSpinner className="h-4 w-4 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <FaSave className="h-4 w-4" />
                          Save Changes
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      disabled={modifyMutation.isPending}
                      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <FaTimes className="h-4 w-4" />
                      Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={handleStartEdit}
                      disabled={approveMutation.isPending || rejectMutation.isPending}
                      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-700 bg-primary-50 rounded-lg hover:bg-primary-100 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <FaEdit className="h-4 w-4" />
                      Modify
                    </button>
                    <button
                      onClick={handleApprove}
                      disabled={approveMutation.isPending}
                      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {approveMutation.isPending ? (
                        <>
                          <FaSpinner className="h-4 w-4 animate-spin" />
                          Approving...
                        </>
                      ) : (
                        <>
                          <FaCheck className="h-4 w-4" />
                          Approve
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => setShowRejectDialog(true)}
                      disabled={rejectMutation.isPending}
                      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <FaBan className="h-4 w-4" />
                      Reject
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        </header>

        {/* Approve Dialog */}
        <ConfirmationDialog
          isOpen={showApproveDialog}
          type="approve"
          title="Approve Recommendation"
          message="Are you sure you want to approve this recommendation? It will be delivered to the user."
          confirmLabel="Approve"
          cancelLabel="Cancel"
          onConfirm={handleConfirmApprove}
          onCancel={() => setShowApproveDialog(false)}
          isLoading={approveMutation.isPending}
        />

        {/* Reject Dialog */}
        <ConfirmationDialog
          isOpen={showRejectDialog}
          type="reject"
          title="Reject Recommendation"
          message="Please provide a reason for rejecting this recommendation:"
          confirmLabel="Reject"
          cancelLabel="Cancel"
          onConfirm={handleReject}
          onCancel={() => {
            setShowRejectDialog(false)
            setRejectReason('')
          }}
          isLoading={rejectMutation.isPending}
          requireTextInput={true}
          textInputValue={rejectReason}
          onTextInputChange={setRejectReason}
          textInputPlaceholder="Enter rejection reason..."
          textInputLabel="Rejection Reason"
          textInputRequired={true}
        />

        {/* User Info */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <FaUser className="h-5 w-5 text-gray-400" />
            User Information
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <span className="text-sm text-gray-500">User ID</span>
              <p className="text-sm font-medium text-gray-900 mt-1">{recommendation.user_id}</p>
            </div>
            {recommendation.user_name && (
              <div>
                <span className="text-sm text-gray-500">Name</span>
                <p className="text-sm font-medium text-gray-900 mt-1">{recommendation.user_name}</p>
              </div>
            )}
            {recommendation.user_email && (
              <div>
                <span className="text-sm text-gray-500">Email</span>
                <p className="text-sm font-medium text-gray-900 mt-1">{recommendation.user_email}</p>
              </div>
            )}
            <div>
              <span className="text-sm text-gray-500">Created At</span>
              <p className="text-sm font-medium text-gray-900 mt-1">{formatDate(recommendation.created_at)}</p>
            </div>
            {recommendation.approved_at && (
              <div>
                <span className="text-sm text-gray-500">Approved At</span>
                <p className="text-sm font-medium text-gray-900 mt-1">{formatDate(recommendation.approved_at)}</p>
              </div>
            )}
            {recommendation.rejected_at && (
              <div>
                <span className="text-sm text-gray-500">Rejected At</span>
                <p className="text-sm font-medium text-gray-900 mt-1">{formatDate(recommendation.rejected_at)}</p>
              </div>
            )}
            {recommendation.rejection_reason && (
              <div className="sm:col-span-2 lg:col-span-3">
                <span className="text-sm text-gray-500">Rejection Reason</span>
                <p className="text-sm font-medium text-red-600 mt-1">{recommendation.rejection_reason}</p>
              </div>
            )}
          </div>
        </div>

        {/* Recommendation Content */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <button
            onClick={() => toggleSection('recommendation')}
            className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <h2 className="text-lg font-semibold text-gray-900">Recommendation Content</h2>
            {expandedSections.has('recommendation') ? (
              <FaChevronUp className="h-5 w-5 text-gray-400" />
            ) : (
              <FaChevronDown className="h-5 w-5 text-gray-400" />
            )}
          </button>
          {expandedSections.has('recommendation') && (
            <div className="px-6 pb-6 border-t border-gray-200">
              <div className="pt-6">
                {isEditing ? (
                  <>
                    <div className="mb-4">
                      <label htmlFor="edit-title" className="block text-sm font-medium text-gray-700 mb-2">
                        Title
                      </label>
                      <input
                        id="edit-title"
                        type="text"
                        value={editedTitle}
                        onChange={(e) => setEditedTitle(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      />
                    </div>
                    <div className="mb-4">
                      <label htmlFor="edit-content" className="block text-sm font-medium text-gray-700 mb-2">
                        Content
                      </label>
                      <textarea
                        id="edit-content"
                        value={editedContent}
                        onChange={(e) => setEditedContent(e.target.value)}
                        rows={8}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                      />
                    </div>
                    <div className="mb-4">
                      <label htmlFor="edit-rationale" className="block text-sm font-medium text-gray-700 mb-2">
                        Rationale
                      </label>
                      <textarea
                        id="edit-rationale"
                        value={editedRationale}
                        onChange={(e) => setEditedRationale(e.target.value)}
                        rows={4}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                      />
                    </div>
                    {hasChanges && (
                      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
                        <div className="flex items-start gap-2">
                          <FaExclamationTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-yellow-800">
                            You have unsaved changes. Click "Save Changes" to apply your modifications.
                          </p>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    <h3 className="text-base font-semibold text-gray-900 mb-3">{recommendation.title}</h3>
                    <div className="prose max-w-none">
                      <div className="text-sm text-gray-700 whitespace-pre-wrap mb-6">{recommendation.content}</div>
                    </div>
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                      <div className="flex items-start gap-3">
                        <FaInfoCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <h4 className="text-sm font-semibold text-blue-900 mb-1">Rationale</h4>
                          <p className="text-sm text-blue-800 whitespace-pre-wrap">{recommendation.rationale}</p>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Persona Assignment */}
        {decisionTrace?.persona_assignment && (
          <div className="bg-white rounded-lg shadow-sm mb-6">
            <button
              onClick={() => toggleSection('persona')}
              className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
            >
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <FaUser className="h-5 w-5 text-gray-400" />
                Persona Assignment Logic
              </h2>
              {expandedSections.has('persona') ? (
                <FaChevronUp className="h-5 w-5 text-gray-400" />
              ) : (
                <FaChevronDown className="h-5 w-5 text-gray-400" />
              )}
            </button>
            {expandedSections.has('persona') && (
              <div className="px-6 pb-6 border-t border-gray-200">
                <div className="pt-6 space-y-4">
                  <div>
                    <span className="text-sm text-gray-500">Assigned Persona</span>
                    <p className="text-sm font-medium text-gray-900 mt-1">
                      {decisionTrace.persona_assignment.persona_name} (Priority: {decisionTrace.persona_assignment.priority})
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-500">Criteria Met</span>
                    <ul className="mt-2 space-y-1">
                      {decisionTrace.persona_assignment.criteria_met.map((criterion, index) => (
                        <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                          <FaCheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                          <span>{criterion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <span className="text-sm text-gray-500">Persona Assignment Rationale</span>
                    <p className="text-sm text-gray-700 mt-1 whitespace-pre-wrap">
                      {decisionTrace.persona_assignment.rationale}
                    </p>
                  </div>
                  {decisionTrace.persona_assignment.persona_changed && (
                    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                      <div className="flex items-start gap-2">
                        <FaExclamationTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                        <p className="text-sm text-yellow-800">Persona changed from previous assignment</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Detected Behavioral Signals */}
        {decisionTrace?.detected_signals && (
          <div className="bg-white rounded-lg shadow-sm mb-6">
            <button
              onClick={() => toggleSection('signals')}
              className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
            >
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <FaInfoCircle className="h-5 w-5 text-gray-400" />
                Detected Behavioral Signals
              </h2>
              {expandedSections.has('signals') ? (
                <FaChevronUp className="h-5 w-5 text-gray-400" />
              ) : (
                <FaChevronDown className="h-5 w-5 text-gray-400" />
              )}
            </button>
            {expandedSections.has('signals') && (
              <div className="px-6 pb-6 border-t border-gray-200">
                <div className="pt-6 space-y-6">
                  {/* Subscriptions */}
                  {(decisionTrace.detected_signals.subscriptions['30d'] ||
                    decisionTrace.detected_signals.subscriptions['180d']) && (
                    <div>
                      <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <FaCreditCard className="h-4 w-4 text-blue-500" />
                        Subscriptions
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <span className="text-xs text-gray-500">30-Day Window</span>
                          <div className="mt-2 space-y-1">
                            {decisionTrace.detected_signals.subscriptions['30d']?.subscription_count !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Count:</span>{' '}
                                {decisionTrace.detected_signals.subscriptions['30d'].subscription_count}
                              </p>
                            )}
                            {decisionTrace.detected_signals.subscriptions['30d']?.total_recurring_spend !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Monthly Recurring:</span>{' '}
                                {formatCurrency(decisionTrace.detected_signals.subscriptions['30d'].total_recurring_spend)}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <span className="text-xs text-gray-500">180-Day Window</span>
                          <div className="mt-2 space-y-1">
                            {decisionTrace.detected_signals.subscriptions['180d']?.subscription_count !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Count:</span>{' '}
                                {decisionTrace.detected_signals.subscriptions['180d'].subscription_count}
                              </p>
                            )}
                            {decisionTrace.detected_signals.subscriptions['180d']?.total_recurring_spend !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Monthly Recurring:</span>{' '}
                                {formatCurrency(
                                  decisionTrace.detected_signals.subscriptions['180d'].total_recurring_spend
                                )}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Savings */}
                  {(decisionTrace.detected_signals.savings['30d'] ||
                    decisionTrace.detected_signals.savings['180d']) && (
                    <div>
                      <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <FaPiggyBank className="h-4 w-4 text-green-500" />
                        Savings
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <span className="text-xs text-gray-500">30-Day Window</span>
                          <div className="mt-2 space-y-1">
                            {decisionTrace.detected_signals.savings['30d']?.savings_growth_rate_percent !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Growth Rate:</span>{' '}
                                {formatPercent(decisionTrace.detected_signals.savings['30d'].savings_growth_rate_percent)}
                              </p>
                            )}
                            {decisionTrace.detected_signals.savings['30d']?.net_inflow !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Net Inflow:</span>{' '}
                                {formatCurrency(decisionTrace.detected_signals.savings['30d'].net_inflow)}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <span className="text-xs text-gray-500">180-Day Window</span>
                          <div className="mt-2 space-y-1">
                            {decisionTrace.detected_signals.savings['180d']?.savings_growth_rate_percent !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Growth Rate:</span>{' '}
                                {formatPercent(
                                  decisionTrace.detected_signals.savings['180d'].savings_growth_rate_percent
                                )}
                              </p>
                            )}
                            {decisionTrace.detected_signals.savings['180d']?.net_inflow !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Net Inflow:</span>{' '}
                                {formatCurrency(decisionTrace.detected_signals.savings['180d'].net_inflow)}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Credit */}
                  {(decisionTrace.detected_signals.credit['30d'] ||
                    decisionTrace.detected_signals.credit['180d']) && (
                    <div>
                      <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <FaCreditCard className="h-4 w-4 text-red-500" />
                        Credit Utilization
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <span className="text-xs text-gray-500">30-Day Window</span>
                          <div className="mt-2 space-y-1">
                            {decisionTrace.detected_signals.credit['30d']?.critical_utilization_cards && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">High Utilization Cards:</span>{' '}
                                {Array.isArray(decisionTrace.detected_signals.credit['30d'].critical_utilization_cards)
                                  ? decisionTrace.detected_signals.credit['30d'].critical_utilization_cards.length
                                  : 0}
                              </p>
                            )}
                            {decisionTrace.detected_signals.credit['30d']?.cards_with_interest && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Cards with Interest:</span>{' '}
                                {Array.isArray(decisionTrace.detected_signals.credit['30d'].cards_with_interest)
                                  ? decisionTrace.detected_signals.credit['30d'].cards_with_interest.length
                                  : 0}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <span className="text-xs text-gray-500">180-Day Window</span>
                          <div className="mt-2 space-y-1">
                            {decisionTrace.detected_signals.credit['180d']?.critical_utilization_cards && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">High Utilization Cards:</span>{' '}
                                {Array.isArray(decisionTrace.detected_signals.credit['180d'].critical_utilization_cards)
                                  ? decisionTrace.detected_signals.credit['180d'].critical_utilization_cards.length
                                  : 0}
                              </p>
                            )}
                            {decisionTrace.detected_signals.credit['180d']?.cards_with_interest && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Cards with Interest:</span>{' '}
                                {Array.isArray(decisionTrace.detected_signals.credit['180d'].cards_with_interest)
                                  ? decisionTrace.detected_signals.credit['180d'].cards_with_interest.length
                                  : 0}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Income */}
                  {(decisionTrace.detected_signals.income['30d'] ||
                    decisionTrace.detected_signals.income['180d']) && (
                    <div>
                      <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <FaDollarSign className="h-4 w-4 text-yellow-500" />
                        Income Stability
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <span className="text-xs text-gray-500">30-Day Window</span>
                          <div className="mt-2 space-y-1">
                            {decisionTrace.detected_signals.income['30d']?.cash_flow_buffer_months !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Cash Flow Buffer:</span>{' '}
                                {decisionTrace.detected_signals.income['30d'].cash_flow_buffer_months.toFixed(1)} months
                              </p>
                            )}
                            {decisionTrace.detected_signals.income['30d']?.payment_frequency && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Payment Frequency:</span>{' '}
                                {decisionTrace.detected_signals.income['30d'].payment_frequency}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <span className="text-xs text-gray-500">180-Day Window</span>
                          <div className="mt-2 space-y-1">
                            {decisionTrace.detected_signals.income['180d']?.cash_flow_buffer_months !== undefined && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Cash Flow Buffer:</span>{' '}
                                {decisionTrace.detected_signals.income['180d'].cash_flow_buffer_months.toFixed(1)} months
                              </p>
                            )}
                            {decisionTrace.detected_signals.income['180d']?.payment_frequency && (
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Payment Frequency:</span>{' '}
                                {decisionTrace.detected_signals.income['180d'].payment_frequency}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Guardrails Checks */}
        {decisionTrace?.recommendation?.guardrails && (
          <div className="bg-white rounded-lg shadow-sm mb-6">
            <button
              onClick={() => toggleSection('guardrails')}
              className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
            >
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <FaShieldAlt className="h-5 w-5 text-gray-400" />
                Guardrails Checks
              </h2>
              {expandedSections.has('guardrails') ? (
                <FaChevronUp className="h-5 w-5 text-gray-400" />
              ) : (
                <FaChevronDown className="h-5 w-5 text-gray-400" />
              )}
            </button>
            {expandedSections.has('guardrails') && (
              <div className="px-6 pb-6 border-t border-gray-200">
                <div className="pt-6 space-y-4">
                  {/* Consent */}
                  {decisionTrace.recommendation.guardrails.consent && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        <FaCheckCircle
                          className={`h-4 w-4 ${
                            decisionTrace.recommendation.guardrails.consent.status === 'granted'
                              ? 'text-green-500'
                              : 'text-red-500'
                          }`}
                        />
                        Consent Check
                      </h3>
                      <p className="text-sm text-gray-700">
                        Status: <span className="font-medium">{decisionTrace.recommendation.guardrails.consent.status}</span>
                      </p>
                      {decisionTrace.recommendation.guardrails.consent.checked_at && (
                        <p className="text-xs text-gray-500 mt-1">
                          Checked at: {formatDate(decisionTrace.recommendation.guardrails.consent.checked_at)}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Eligibility */}
                  {decisionTrace.recommendation.guardrails.eligibility && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        <FaCheckCircle
                          className={`h-4 w-4 ${
                            decisionTrace.recommendation.guardrails.eligibility.status === 'eligible'
                              ? 'text-green-500'
                              : 'text-red-500'
                          }`}
                        />
                        Eligibility Check
                      </h3>
                      <p className="text-sm text-gray-700 mb-2">
                        Status: <span className="font-medium">{decisionTrace.recommendation.guardrails.eligibility.status}</span>
                      </p>
                      {decisionTrace.recommendation.guardrails.eligibility.explanation && (
                        <p className="text-sm text-gray-700 mb-2">
                          {decisionTrace.recommendation.guardrails.eligibility.explanation}
                        </p>
                      )}
                      {decisionTrace.recommendation.guardrails.eligibility.details && (
                        <div className="mt-2 space-y-1 text-xs text-gray-600">
                          {decisionTrace.recommendation.guardrails.eligibility.details.income !== undefined && (
                            <p>
                              Estimated Income: {formatCurrency(decisionTrace.recommendation.guardrails.eligibility.details.income)}
                            </p>
                          )}
                          {decisionTrace.recommendation.guardrails.eligibility.details.credit_score !== undefined && (
                            <p>Estimated Credit Score: {decisionTrace.recommendation.guardrails.eligibility.details.credit_score}</p>
                          )}
                          {decisionTrace.recommendation.guardrails.eligibility.details.existing_products &&
                            decisionTrace.recommendation.guardrails.eligibility.details.existing_products.length > 0 && (
                              <p>
                                Existing Products: {decisionTrace.recommendation.guardrails.eligibility.details.existing_products.join(', ')}
                              </p>
                            )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Tone */}
                  {decisionTrace.recommendation.guardrails.tone && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        <FaCheckCircle
                          className={`h-4 w-4 ${
                            decisionTrace.recommendation.guardrails.tone.status === 'approved'
                              ? 'text-green-500'
                              : 'text-red-500'
                          }`}
                        />
                        Tone Validation
                      </h3>
                      <p className="text-sm text-gray-700">
                        Status: <span className="font-medium">{decisionTrace.recommendation.guardrails.tone.status}</span>
                      </p>
                      {decisionTrace.recommendation.guardrails.tone.score !== undefined && (
                        <p className="text-sm text-gray-700 mt-1">
                          Tone Score: <span className="font-medium">{decisionTrace.recommendation.guardrails.tone.score}/10</span>
                        </p>
                      )}
                      {decisionTrace.recommendation.guardrails.tone.explanation && (
                        <p className="text-xs text-gray-600 mt-1">{decisionTrace.recommendation.guardrails.tone.explanation}</p>
                      )}
                    </div>
                  )}

                  {/* Disclaimer */}
                  {decisionTrace.recommendation.guardrails.disclaimer && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        <FaInfoCircle
                          className={`h-4 w-4 ${
                            decisionTrace.recommendation.guardrails.disclaimer.present ? 'text-green-500' : 'text-red-500'
                          }`}
                        />
                        Regulatory Disclaimer
                      </h3>
                      <p className="text-sm text-gray-700">
                        Present: <span className="font-medium">{decisionTrace.recommendation.guardrails.disclaimer.present ? 'Yes' : 'No'}</span>
                      </p>
                      {decisionTrace.recommendation.guardrails.disclaimer.text && (
                        <p className="text-xs text-gray-600 mt-1">{decisionTrace.recommendation.guardrails.disclaimer.text}</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Generation Performance */}
        {decisionTrace?.generation_time_ms !== undefined && (
          <div className="bg-white rounded-lg shadow-sm">
            <div className="px-6 py-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Generation Performance</h2>
              <p className="text-sm text-gray-700">
                Generation Time: <span className="font-medium">{decisionTrace.generation_time_ms.toFixed(2)}ms</span>
                {decisionTrace.generation_time_ms < 5000 && (
                  <span className="ml-2 text-green-600">✓ Within target (5s)</span>
                )}
              </p>
              {decisionTrace.timestamp && (
                <p className="text-xs text-gray-500 mt-1">Generated at: {formatDate(decisionTrace.timestamp)}</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default OperatorReview
