import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { adminService, type UserWithPersona } from '@/services/adminService'
import { PageSkeleton } from '@/components/LoadingSkeleton'
import ErrorState from '@/components/ErrorState'
import { FaUser, FaEnvelope, FaShieldAlt, FaCheckCircle, FaTimesCircle } from 'react-icons/fa'

interface StaffListProps {
  limit?: number
}

const StaffList = ({ limit = 100 }: StaffListProps) => {
  const navigate = useNavigate()
  const {
    data: usersData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['admin', 'users', limit],
    queryFn: () => adminService.getAllUsers(0, limit),
    staleTime: 1 * 60 * 1000, // 1 minute
  })

  const handleUserClick = (userId: string) => {
    navigate(`/admin/users/${userId}`)
  }

  if (isLoading) {
    return <PageSkeleton sections={1} />
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load staff"
        error={error}
        onRetry={() => refetch()}
        retryLabel="Retry"
      />
    )
  }

  // Filter to only show operators and admins
  const staff = usersData?.items.filter((user) => user.role === 'operator' || user.role === 'admin') || []
  const staffTotal = staff.length

  if (!usersData || staff.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <p className="text-gray-500 text-center">No staff members found</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Staff ({staffTotal})</h3>
        <p className="text-sm text-gray-500 mt-1">Operators and administrators</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Staff Member
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Consent
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {staff.map((user) => (
              <tr
                key={user.user_id}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => handleUserClick(user.user_id)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                      <FaShieldAlt className="h-5 w-5 text-primary-600" />
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {user.name || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-500 flex items-center gap-1">
                        <FaEnvelope className="h-3 w-3" />
                        {user.email || 'No email'}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.role === 'admin'
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    <FaShieldAlt className="h-3 w-3" />
                    {user.role === 'admin' ? 'Administrator' : 'Operator'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {user.consent_status ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <FaCheckCircle className="h-3 w-3" />
                      Granted
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      <FaTimesCircle className="h-3 w-3" />
                      Revoked
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.created_at
                    ? new Date(user.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })
                    : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {staffTotal > limit && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <p className="text-sm text-gray-500">
            Showing {staff.length} of {staffTotal} staff members
          </p>
        </div>
      )}
    </div>
  )
}

export default StaffList


