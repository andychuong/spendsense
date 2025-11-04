import PersonaBadge from './PersonaBadge'

interface PersonaHistoryEntry {
  history_id: string
  user_id: string
  persona_id: number
  persona_name: string
  assigned_at: string
  signals?: Record<string, any>
}

interface PersonaHistoryTimelineProps {
  history: PersonaHistoryEntry[]
}

const PersonaHistoryTimeline = ({ history }: PersonaHistoryTimelineProps) => {
  if (history.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500 text-sm">
          No persona history available yet. Your persona will be assigned after data processing.
        </p>
      </div>
    )
  }

  // Sort by assigned_at descending (most recent first)
  const sortedHistory = [...history].sort(
    (a, b) => new Date(b.assigned_at).getTime() - new Date(a.assigned_at).getTime()
  )

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Persona History</h3>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        <div className="space-y-6">
          {sortedHistory.map((entry, index) => (
            <div key={entry.history_id} className="relative flex items-start gap-4">
              {/* Timeline dot */}
              <div className="relative z-10 flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-white border-2 border-primary-500 flex items-center justify-center">
                  <div className="h-3 w-3 rounded-full bg-primary-500"></div>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{formatDate(entry.assigned_at)}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {index === 0 ? 'Current Persona' : 'Previous Persona'}
                      </p>
                    </div>
                  </div>

                  <PersonaBadge
                    personaId={entry.persona_id}
                    personaName={entry.persona_name}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default PersonaHistoryTimeline

