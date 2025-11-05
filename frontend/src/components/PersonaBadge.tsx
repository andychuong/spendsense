interface PersonaBadgeProps {
  personaId: number
  personaName: string
}

const personaColors: Record<number, { bg: string; text: string; border: string }> = {
  1: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  2: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  3: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  4: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
  5: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
}

const personaDescriptions: Record<number, string> = {
  1: 'High credit utilization detected',
  2: 'Variable income patterns identified',
  3: 'Multiple active subscriptions',
  4: 'Strong savings growth',
  5: 'Custom financial profile',
}

const PersonaBadge = ({ personaId, personaName }: PersonaBadgeProps) => {
  const colors = personaColors[personaId] || personaColors[5]
  const description = personaDescriptions[personaId] || personaDescriptions[5]

  return (
    <div className={`p-4 rounded-lg border-2 ${colors.bg} ${colors.border}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className={`text-lg font-semibold ${colors.text}`}>{personaName}</h3>
          <p className={`text-sm ${colors.text} opacity-80 mt-1`}>{description}</p>
        </div>
        <div className={`px-3 py-1 rounded-full ${colors.bg} border ${colors.border}`}>
          <span className={`text-xs font-medium ${colors.text}`}>Persona {personaId}</span>
        </div>
      </div>
    </div>
  )
}

export default PersonaBadge


