import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { operatorService, type ReviewQueueFilters, type ReviewQueueItem } from '@/services/operatorService'
import { adminService } from '@/services/adminService'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import PersonaBadge from '@/components/PersonaBadge'
import { FaCheckCircle, FaTimesCircle, FaClock, FaEye, FaFilter, FaSearch, FaSort, FaCheck, FaBan } from 'react-icons/fa'

type SortField = 'priority' | 'date' | 'user'
type SortOrder = 'asc' | 'desc'

const ReviewQueueList = () => {
  const queryClient = useQueryClient()
  const [filters, setFilters] = useState<ReviewQueueFilters>({
    status: 'pending',
    type: 'all',
    skip: 0,
    limit: 50,
    sort_by: 'date',
    sort_order: 'desc',
  })
  const [showFilters, setShowFilters] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [sortField, setSortField] = useState<SortField>('date')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  // Fetch users for user filter (if needed)
  const { data: usersData } = useQuery({
    queryKey: ['admin', 'users', 'for-filter'],
    queryFn: () => adminService.getAllUsers(0, 1000),
    enabled: showFilters,
  })

  const {
    data: queueData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['operator', 'review-queue', filters],
    queryFn: () => operatorService.getReviewQueue(filters),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Auto-refresh every minute
  })

  // Bulk approve mutation
  const bulkApproveMutation = useMutation({
    mutationFn: (ids: string[]) => operatorService.bulkApproveRecommendations(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'review-queue'] })
      setSelectedItems(new Set())
    },
  })

  // Bulk reject mutation
  const bulkRejectMutation = useMutation({
    mutationFn: ({ ids, reason }: { ids: string[]; reason: string }) =>
      operatorService.bulkRejectRecommendations(ids, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'review-queue'] })
      setSelectedItems(new Set())
    },
  })

  // Client-side filtering and sorting
  const filteredAndSortedItems = useMemo(() => {
    if (!queueData?.items) return []

    let items = [...queueData.items]

    // Client-side search (if backend doesn't support it)
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      items = items.filter(
        (item) =>
          item.title.toLowerCase().includes(query) ||
          item.user_name?.toLowerCase().includes(query) ||
          item.user_email?.toLowerCase().includes(query)
      )
    }

    // Client-side date filtering
    if (dateFrom) {
      const fromDate = new Date(dateFrom)
      items = items.filter((item) => new Date(item.created_at) >= fromDate)
    }
    if (dateTo) {
      const toDate = new Date(dateTo)
      toDate.setHours(23, 59, 59, 999) // Include entire day
      items = items.filter((item) => new Date(item.created_at) <= toDate)
    }

    // Client-side sorting
    items.sort((a, b) => {
      let comparison = 0

      switch (sortField) {
        case 'date':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          break
        case 'user':
          const nameA = (a.user_name || a.user_email || '').toLowerCase()
          const nameB = (b.user_name || b.user_email || '').toLowerCase()
          comparison = nameA.localeCompare(nameB)
          break
        case 'priority':
          // Priority: pending > approved > rejected
          const priorityMap: Record<string, number> = { pending: 3, approved: 2, rejected: 1 }
          comparison = priorityMap[b.status] - priorityMap[a.status]
          break
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return items
  }, [queueData?.items, searchQuery, sortField, sortOrder, dateFrom, dateTo])

  const handleStatusChange = (status: 'pending' | 'approved' | 'rejected' | 'all') => {
    setFilters({ ...filters, status, skip: 0 })
  }

  const handleTypeChange = (type: 'education' | 'partner_offer' | 'all') => {
    setFilters({ ...filters, type, skip: 0 })
  }

  const handleSortChange = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedItems(new Set(filteredAndSortedItems.map((item) => item.recommendation_id)))
    } else {
      setSelectedItems(new Set())
    }
  }

  const handleSelectItem = (id: string, checked: boolean) => {
    const newSelected = new Set(selectedItems)
    if (checked) {
      newSelected.add(id)
    } else {
      newSelected.delete(id)
    }
    setSelectedItems(newSelected)
  }

  const handleBulkApprove = () => {
    if (selectedItems.size === 0) return
    if (window.confirm(`Approve ${selectedItems.size} recommendation(s)?`)) {
      bulkApproveMutation.mutate(Array.from(selectedItems))
    }
  }

  const handleBulkReject = () => {
    if (selectedItems.size === 0) return
    const reason = window.prompt(`Reject ${selectedItems.size} recommendation(s). Please provide a reason:`)
    if (reason) {
      bulkRejectMutation.mutate({ ids: Array.from(selectedItems), reason })
    }
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

  if (isLoading) {
    return <PageSkeleton sections={1} />
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorState
            title="Failed to load review queue"
            error={error}
            onRetry={() => refetch()}
            retryLabel="Retry"
          />
        </div>
      </div>
    )
  }

  const hasSelectedItems = selectedItems.size > 0
  const allSelected = filteredAndSortedItems.length > 0 && selectedItems.size === filteredAndSortedItems.length

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-6 lg:mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                Review Queue
              </h1>
              <p className="mt-2 text-sm text-gray-600">
                Review and approve recommendations for delivery
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <FaFilter className="h-4 w-4" />
                Filters
              </button>
            </div>
          </div>
        </header>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="relative">
            <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Search by title, user name, or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        {/* Bulk Actions Bar */}
        {hasSelectedItems && (
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-900">
                  {selectedItems.size} item{selectedItems.size !== 1 ? 's' : ''} selected
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleBulkApprove}
                  disabled={bulkApproveMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <FaCheck className="h-4 w-4" />
                  Approve Selected
                </button>
                <button
                  onClick={handleBulkReject}
                  disabled={bulkRejectMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <FaBan className="h-4 w-4" />
                  Reject Selected
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        {showFilters && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <div className="flex gap-2 flex-wrap">
                  {(['all', 'pending', 'approved', 'rejected'] as const).map((status) => (
                    <button
                      key={status}
                      onClick={() => handleStatusChange(status)}
                      className={`px-3 py-1 text-sm rounded-lg ${
                        filters.status === status
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {status.charAt(0).toUpperCase() + status.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type
                </label>
                <div className="flex gap-2 flex-wrap">
                  {(['all', 'education', 'partner_offer'] as const).map((type) => (
                    <button
                      key={type}
                      onClick={() => handleTypeChange(type)}
                      className={`px-3 py-1 text-sm rounded-lg ${
                        filters.type === type
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {type === 'partner_offer' ? 'Partner Offer' : type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  User
                </label>
                <select
                  value={filters.user_id || ''}
                  onChange={(e) => setFilters({ ...filters, user_id: e.target.value || undefined, skip: 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">All Users</option>
                  {usersData?.items.map((user) => (
                    <option key={user.user_id} value={user.user_id}>
                      {user.name || user.email || user.user_id}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Persona
                </label>
                <select
                  value={filters.persona_id || ''}
                  onChange={(e) => setFilters({ ...filters, persona_id: e.target.value ? Number(e.target.value) : undefined, skip: 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">All Personas</option>
                  <option value="1">Persona 1: High Utilization</option>
                  <option value="2">Persona 2: Variable Income Budgeter</option>
                  <option value="3">Persona 3: Subscription-Heavy</option>
                  <option value="4">Persona 4: Savings Builder</option>
                  <option value="5">Persona 5: Custom</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date From
                </label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date To
                </label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
            {(dateFrom || dateTo || filters.persona_id) && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setDateFrom('')
                    setDateTo('')
                    setFilters({ ...filters, persona_id: undefined })
                  }}
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Clear date and persona filters
                </button>
              </div>
            )}
          </div>
        )}

        {/* Review Queue List */}
        {!queueData || filteredAndSortedItems.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="text-center py-12">
              <FaCheckCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Recommendations Found</h3>
              <p className="text-sm text-gray-500">
                {filters.status === 'pending' && !searchQuery
                  ? 'All recommendations have been reviewed. Great job!'
                  : 'No recommendations match your filters or search query.'}
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  {filteredAndSortedItems.length} Recommendation{filteredAndSortedItems.length !== 1 ? 's' : ''}
                  {searchQuery && ` (filtered from ${queueData.total})`}
                </h2>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Sort by:</span>
                  <div className="flex gap-1">
                    {(['priority', 'date', 'user'] as SortField[]).map((field) => (
                      <button
                        key={field}
                        onClick={() => handleSortChange(field)}
                        className={`flex items-center gap-1 px-3 py-1 text-sm rounded-lg ${
                          sortField === field
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <FaSort className="h-3 w-3" />
                        {field.charAt(0).toUpperCase() + field.slice(1)}
                        {sortField === field && (
                          <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div className="divide-y divide-gray-200">
              {/* Select All Checkbox */}
              <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm font-medium text-gray-700">Select All</span>
                </label>
              </div>
              {filteredAndSortedItems.map((item) => {
                const isSelected = selectedItems.has(item.recommendation_id)
                return (
                  <div
                    key={item.recommendation_id}
                    className={`px-6 py-4 hover:bg-gray-50 transition-colors ${
                      isSelected ? 'bg-primary-50' : ''
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => handleSelectItem(item.recommendation_id, e.target.checked)}
                        onClick={(e) => e.stopPropagation()}
                        className="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <Link
                        to={`/operator/review/${item.recommendation_id}`}
                        className="flex-1 min-w-0"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                              {getStatusBadge(item.status)}
                              {getTypeBadge(item.type)}
                              {item.persona_name && (
                                <PersonaBadge
                                  personaId={item.persona_id!}
                                  personaName={item.persona_name}
                                />
                              )}
                            </div>
                            <h3 className="text-base font-medium text-gray-900 mb-2">
                              {item.title}
                            </h3>
                            <div className="flex items-center gap-4 text-sm text-gray-500 flex-wrap">
                              {item.user_name && (
                                <span className="truncate">
                                  <span className="font-medium">User:</span> {item.user_name}
                                </span>
                              )}
                              {item.user_email && (
                                <span className="truncate">
                                  <span className="font-medium">Email:</span> {item.user_email}
                                </span>
                              )}
                              <span>
                                Created: {new Date(item.created_at).toLocaleDateString('en-US', {
                                  month: 'short',
                                  day: 'numeric',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4 flex-shrink-0">
                            <FaEye className="h-5 w-5 text-gray-400" />
                          </div>
                        </div>
                      </Link>
                    </div>
                  </div>
                )
              })}
            </div>
            {queueData.total > (filters.limit || 50) && (
              <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
                <p className="text-sm text-gray-500">
                  Showing {queueData.items.length} of {queueData.total} recommendations
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ReviewQueueList
