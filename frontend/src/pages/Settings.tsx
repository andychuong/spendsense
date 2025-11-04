import AccountLinking from '@/components/AccountLinking'
import ConsentManagement from '@/components/ConsentManagement'
import IncomeSettings from '@/components/IncomeSettings'

const Settings = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-4 lg:py-8 pb-24 lg:pb-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6 lg:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Settings</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage your account settings, consent, and linked authentication methods.
          </p>
        </div>

        <div className="space-y-6">
          {/* Income Settings Section */}
          <IncomeSettings />

          {/* Consent Management Section */}
          <ConsentManagement />

          {/* Account Linking Section */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <AccountLinking />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings

