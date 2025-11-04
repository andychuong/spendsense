import { Link } from 'react-router-dom'

interface ConsentStatusBadgeProps {
  consentStatus: boolean
}

const ConsentStatusBadge = ({ consentStatus }: ConsentStatusBadgeProps) => {
  return (
    <div
      className={`p-4 rounded-lg border-2 ${
        consentStatus
          ? 'bg-green-50 border-green-200'
          : 'bg-yellow-50 border-yellow-200'
      }`}
    >
      <div className="flex items-center justify-between">
        <div>
          <h3
            className={`text-lg font-semibold ${
              consentStatus ? 'text-green-700' : 'text-yellow-700'
            }`}
          >
            Consent Status
          </h3>
          <p
            className={`text-sm ${
              consentStatus ? 'text-green-600' : 'text-yellow-600'
            } mt-1`}
          >
            {consentStatus
              ? 'You have granted consent for data processing. Your personalized recommendations are active.'
              : 'Consent is required to process your data and generate personalized recommendations.'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              consentStatus
                ? 'bg-green-100 text-green-700 border border-green-200'
                : 'bg-yellow-100 text-yellow-700 border border-yellow-200'
            }`}
          >
            {consentStatus ? 'Granted' : 'Not Granted'}
          </span>
          <Link
            to="/settings"
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Manage
          </Link>
        </div>
      </div>
    </div>
  )
}

export default ConsentStatusBadge

