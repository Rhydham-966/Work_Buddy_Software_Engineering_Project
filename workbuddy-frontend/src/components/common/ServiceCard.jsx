import { useNavigate } from 'react-router-dom'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'
import { Clock, IndianRupee, ArrowRight } from 'lucide-react'

// Service icons by keyword
const SERVICE_ICONS = {
  plumb: '🔧', electric: '⚡', clean: '🧹', paint: '🎨',
  ac: '❄️', pest: '🐛', carpenter: '🪚', garden: '🌱',
  default: '🛠️',
}

function getIcon(name = '') {
  const lower = name.toLowerCase()
  for (const [key, icon] of Object.entries(SERVICE_ICONS)) {
    if (lower.includes(key)) return icon
  }
  return SERVICE_ICONS.default
}

export function ServiceCard({ service }) {
  const navigate = useNavigate()
  const icon = getIcon(service.name)

  return (
    <Card className="flex flex-col group cursor-pointer" hover>
      <div className="p-6 flex-1">
        {/* Icon */}
        <div className="w-14 h-14 rounded-2xl bg-primary-50 dark:bg-primary-950 flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform duration-200">
          {icon}
        </div>

        <h3 className="text-lg font-bold text-surface-900 dark:text-surface-100 mb-1.5 group-hover:text-primary-600 transition-colors">
          {service.name}
        </h3>
        <p className="text-sm text-surface-500 dark:text-surface-400 line-clamp-2 mb-4">
          {service.description || 'Professional service at your doorstep.'}
        </p>

        <div className="flex items-center gap-4 text-sm text-surface-500 dark:text-surface-400">
          <div className="flex items-center gap-1">
            <IndianRupee size={14} className="text-accent-500" />
            <span className="font-semibold text-surface-800 dark:text-surface-200">
              {service.base_price}
            </span>
            <span className="text-xs">base</span>
          </div>
          {service.estimated_time && (
            <div className="flex items-center gap-1">
              <Clock size={14} />
              <span>{service.estimated_time}</span>
            </div>
          )}
        </div>
      </div>

      <div className="px-6 pb-5">
        <Button
          fullWidth
          size="sm"
          icon={<ArrowRight size={14} />}
          onClick={() => navigate(`/customer/services/${service.id}`)}
        >
          Book Now
        </Button>
      </div>
    </Card>
  )
}
