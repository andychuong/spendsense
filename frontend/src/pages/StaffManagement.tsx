import { useState } from 'react'
import UsersList from '@/components/UsersList'
import StaffList from '@/components/StaffList'
import { FaUsers, FaShieldAlt } from 'react-icons/fa'

const StaffManagement = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'staff'>('users')

  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-6 lg:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
            User Management
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage users and staff members
          </p>
        </header>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('users')}
                className={`
                  flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm
                  ${
                    activeTab === 'users'
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <FaUsers className="h-4 w-4" />
                Users
              </button>
              <button
                onClick={() => setActiveTab('staff')}
                className={`
                  flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm
                  ${
                    activeTab === 'staff'
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <FaShieldAlt className="h-4 w-4" />
                Staff
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'users' && <UsersList limit={100} />}
          {activeTab === 'staff' && <StaffList limit={100} />}
        </div>
      </div>
    </div>
  )
}

export default StaffManagement


