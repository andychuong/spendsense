import { Link } from 'react-router-dom'

interface Recommendation {
  recommendation_id: string
  user_id: string
  type: 'education' | 'partner_offer'
  title: string
  content: string
  rationale: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  approved_at?: string
  decision_trace?: Record<string, any>
}

interface RecommendationsListProps {
  recommendations: Recommendation[]
}

const RecommendationsList = ({ recommendations }: RecommendationsListProps) => {
  if (recommendations.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500 text-sm mb-2">No recommendations available yet.</p>
        <p className="text-gray-400 text-xs">
          Recommendations will appear here once your data is processed.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
        <Link
          to="/recommendations"
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          View all
        </Link>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div
            key={rec.recommendation_id}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${
                      rec.type === 'education'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-green-100 text-green-700'
                    }`}
                  >
                    {rec.type === 'education' ? 'Education' : 'Partner Offer'}
                  </span>
                </div>
                <h4 className="text-base font-semibold text-gray-900 mb-1">{rec.title}</h4>
                <p className="text-sm text-gray-600 line-clamp-2 mb-2">{rec.content}</p>
              </div>
            </div>

            {rec.rationale && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-xs font-medium text-gray-500 mb-1">Because:</p>
                <p className="text-sm text-gray-700">{rec.rationale}</p>
              </div>
            )}

            <div className="mt-3 flex gap-2">
              <Link
                to={`/recommendations/${rec.recommendation_id}`}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                View Details
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default RecommendationsList

