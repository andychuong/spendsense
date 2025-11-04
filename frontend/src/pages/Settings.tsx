import AccountLinking from '@/components/AccountLinking'

const Settings = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage your account settings and linked authentication methods.
          </p>
        </div>

        {/* Account Linking Section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <AccountLinking />
        </div>
      </div>
    </div>
  )
}

export default Settings

