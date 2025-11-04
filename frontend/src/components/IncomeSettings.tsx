import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userService } from '@/services/userService'
import { FaDollarSign, FaSave, FaTimes } from 'react-icons/fa'

const IncomeSettings = () => {
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [incomeValue, setIncomeValue] = useState<string>('')

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => userService.getProfile(),
    staleTime: 5 * 60 * 1000,
  })

  const updateMutation = useMutation({
    mutationFn: (data: { monthly_income?: number }) => userService.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setIsEditing(false)
    },
  })

  const handleEdit = () => {
    if (profile?.monthly_income) {
      setIncomeValue(profile.monthly_income.toString())
    } else {
      setIncomeValue('')
    }
    setIsEditing(true)
  }

  const handleSave = () => {
    const income = incomeValue.trim() === '' ? undefined : parseFloat(incomeValue)
    if (income !== undefined && (isNaN(income) || income < 0)) {
      alert('Please enter a valid positive number for monthly income')
      return
    }
    updateMutation.mutate({ monthly_income: income })
  }

  const handleCancel = () => {
    setIsEditing(false)
    setIncomeValue('')
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FaDollarSign className="h-5 w-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Monthly Income</h2>
        </div>
        {!isEditing && (
          <button
            onClick={handleEdit}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Edit
          </button>
        )}
      </div>

      {isEditing ? (
        <div className="space-y-4">
          <div>
            <label htmlFor="monthly-income" className="block text-sm font-medium text-gray-700 mb-2">
              Monthly Income (USD)
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span className="text-gray-500 sm:text-sm">$</span>
              </div>
              <input
                id="monthly-income"
                type="number"
                min="0"
                step="0.01"
                value={incomeValue}
                onChange={(e) => setIncomeValue(e.target.value)}
                placeholder="Enter monthly income"
                className="block w-full pl-7 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            <p className="mt-2 text-sm text-gray-500">
              Leave blank to use calculated income from your transaction data
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={updateMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FaSave className="h-4 w-4" />
              {updateMutation.isPending ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={handleCancel}
              disabled={updateMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FaTimes className="h-4 w-4" />
              Cancel
            </button>
          </div>
          {updateMutation.isError && (
            <div className="text-sm text-red-600">
              Failed to update income. Please try again.
            </div>
          )}
        </div>
      ) : (
        <div>
          {profile?.monthly_income ? (
            <div className="text-2xl font-semibold text-gray-900">
              {formatCurrency(profile.monthly_income)}
            </div>
          ) : (
            <div className="text-gray-500 italic">
              Not set - will be calculated from transaction data
            </div>
          )}
          {profile?.monthly_income && (
            <p className="mt-2 text-sm text-gray-500">
              This value will be used for recommendations and analysis
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default IncomeSettings

