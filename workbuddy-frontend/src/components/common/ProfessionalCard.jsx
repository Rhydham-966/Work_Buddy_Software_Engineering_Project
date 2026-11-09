import { Card } from '../ui/Card'
import { MapPin, Star, Briefcase, IndianRupee } from 'lucide-react'

export function ProfessionalCard({ professional, onSelect, selected }) {
  return (
    <Card
      className={`p-4 cursor-pointer transition-all duration-200 ${
        selected ? 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-950' : ''
      }`}
      hover
      onClick={() => onSelect?.(professional)}
    >
      <div className="flex items-center gap-3 mb-3">
        {/* Avatar */}
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-lg">
            {professional.name?.charAt(0)?.toUpperCase() || 'P'}
          </span>
        </div>
        <div>
          <h4 className="font-semibold text-surface-900 dark:text-surface-100">
            {professional.name || `Professional #${professional.id}`}
          </h4>
          <div className="flex items-center gap-1 text-xs text-amber-500">
            <Star size={12} fill="currentColor" />
            <span>{professional.rating || '4.5'}</span>
            <span className="text-surface-400 ml-1">({professional.experience || 0} yrs)</span>
          </div>
        </div>
      </div>
      <div className="flex flex-wrap gap-3 text-xs text-surface-500 dark:text-surface-400">
        {professional.area && (
          <div className="flex items-center gap-1">
            <MapPin size={12} className="text-primary-400" />
            <span>{professional.area}</span>
          </div>
        )}
        {professional.custom_price && (
          <div className="flex items-center gap-1">
            <IndianRupee size={12} className="text-accent-500" />
            <span className="font-semibold text-surface-700 dark:text-surface-300">₹{professional.custom_price}</span>
          </div>
        )}
      </div>
      {selected && (
        <div className="mt-3 text-xs text-primary-600 dark:text-primary-400 font-semibold">✓ Selected</div>
      )}
    </Card>
  )
}
