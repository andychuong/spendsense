import { Link } from 'react-router-dom'
import { formatMarkdownToReact, stripMarkdown } from '@/utils/formatMarkdown'

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
  showHeader?: boolean
}

const RecommendationsList = ({ recommendations, showHeader = true }: RecommendationsListProps) => {
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
      {showHeader && (
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
          <Link
            to="/recommendations"
            className="text-sm text-primary-600 hover:text-primary-700 font-medium cursor-pointer"
          >
            View all
          </Link>
        </div>
      )}

      <div className="space-y-3">
        {recommendations.map((rec) => {
          // Extract first sentence or first 120 characters for summary
          const cleanContent = rec.content
            .replace(/\*\*Disclaimer\*\*:?\s*This is educational content.*?guidance\./gi, '')
            .replace(/This is educational content, not financial advice.*?guidance\./gi, '')
            .trim()
          
          const firstSentence = cleanContent.split(/[.!?]\s/)[0]
          const summary = firstSentence.length > 120 
            ? cleanContent.substring(0, 120) + '...'
            : firstSentence

          return (
            <div
              key={rec.recommendation_id}
              className="bg-gradient-to-br from-white to-gray-50 border border-gray-200 rounded-lg p-5 hover:shadow-lg hover:border-primary-200 transition-all duration-200"
            >
              <div className="flex items-start gap-4">
                {/* Icon/Badge */}
                <div className={`flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center ${
                  rec.type === 'education'
                    ? 'bg-blue-100'
                    : 'bg-green-100'
                }`}>
                  <span className={`text-2xl ${
                    rec.type === 'education' ? 'text-blue-600' : 'text-green-600'
                  }`}>
                    {rec.type === 'education' ? '📚' : '🎁'}
                  </span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                        rec.type === 'education'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-green-100 text-green-700'
                      }`}
                    >
                      {rec.type === 'education' ? 'Education' : 'Partner Offer'}
                    </span>
                  </div>
                  
                  <h4 className="text-lg font-bold text-gray-900 mb-2 line-clamp-1">
                    {rec.title}
                  </h4>
                  
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {summary}
                  </p>

                  {rec.rationale && (
                    <div className="mb-3 p-3 bg-blue-50 border-l-3 border-l-blue-400 rounded">
                      <p className="text-xs font-semibold text-blue-900 mb-1">Why this matters:</p>
                      <p className="text-xs text-blue-800 line-clamp-2">
                        {rec.rationale.substring(0, 150)}
                        {rec.rationale.length > 150 && '...'}
                      </p>
                    </div>
                  )}

                  <Link
                    to={`/recommendations/${rec.recommendation_id}`}
                    className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-semibold hover:gap-2 transition-all cursor-pointer"
                  >
                    View Details
                    <span>→</span>
                  </Link>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default RecommendationsList


