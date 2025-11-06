import { RecommendationExplanation } from '@/services/recommendationsService'

interface ExplanationSectionProps {
  explanation: RecommendationExplanation
}

const ExplanationSection = ({ explanation }: ExplanationSectionProps) => {
  const hasData = explanation.data_citations && explanation.data_citations.length > 0
  const hasScenarios = explanation.similar_scenarios && explanation.similar_scenarios.length > 0

  if (!hasData && !hasScenarios) {
    return null
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">
        Why You Got This Recommendation
      </h3>

      {hasData && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">
            Based on Your Data:
          </h4>
          <ul className="space-y-1">
            {explanation.data_citations!.map((citation, index) => (
              <li key={index} className="text-sm text-gray-600 flex items-start">
                <span className="text-blue-600 mr-2 mt-0.5">•</span>
                <span>{citation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {hasScenarios && (
        <div className="space-y-2 pt-2 border-t border-blue-200">
          <h4 className="text-sm font-medium text-gray-700">
            What Others Achieved:
          </h4>
          <ul className="space-y-1">
            {explanation.similar_scenarios!.map((scenario, index) => (
              <li key={index} className="text-sm text-gray-600 flex items-start">
                <span className="text-green-600 mr-2 mt-0.5">✓</span>
                <span>{scenario}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {explanation.persona && (
        <div className="pt-2 border-t border-blue-200">
          <p className="text-xs text-gray-500">
            Profile Type: <span className="font-medium text-gray-700">{explanation.persona}</span>
          </p>
        </div>
      )}

      {explanation.confidence !== undefined && explanation.confidence > 0 && (
        <div className="pt-2">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Confidence Score</span>
            <span className="font-medium text-gray-700">
              {(explanation.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
            <div
              className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${explanation.confidence * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default ExplanationSection

