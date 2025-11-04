interface TimePeriodSelectorProps {
  selectedPeriod: '30d' | '180d'
  onPeriodChange: (period: '30d' | '180d') => void
}

const TimePeriodSelector = ({ selectedPeriod, onPeriodChange }: TimePeriodSelectorProps) => {
  return (
    <div className="flex gap-2 bg-gray-100 p-1 rounded-lg">
      <button
        type="button"
        onClick={() => onPeriodChange('30d')}
        className={`
          flex-1 py-2 px-4 rounded-md font-medium transition-all duration-200
          ${selectedPeriod === '30d'
            ? 'bg-white text-primary-600 shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
          }
        `}
      >
        30 Days
      </button>
      <button
        type="button"
        onClick={() => onPeriodChange('180d')}
        className={`
          flex-1 py-2 px-4 rounded-md font-medium transition-all duration-200
          ${selectedPeriod === '180d'
            ? 'bg-white text-primary-600 shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
          }
        `}
      >
        180 Days
      </button>
    </div>
  )
}

export default TimePeriodSelector

