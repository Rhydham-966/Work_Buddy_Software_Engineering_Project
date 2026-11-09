import { Card } from '../ui/Card'

export function StatsCard({ label, value, icon: Icon, color = 'primary', trend }) {
  const colors = {
    primary:  { bg: 'bg-primary-50 dark:bg-primary-950',  icon: 'text-primary-600 dark:text-primary-400',  val: 'text-primary-700 dark:text-primary-300' },
    success:  { bg: 'bg-emerald-50 dark:bg-emerald-950', icon: 'text-emerald-600 dark:text-emerald-400', val: 'text-emerald-700 dark:text-emerald-300' },
    warning:  { bg: 'bg-amber-50 dark:bg-amber-950',     icon: 'text-amber-600 dark:text-amber-400',     val: 'text-amber-700 dark:text-amber-300' },
    danger:   { bg: 'bg-red-50 dark:bg-red-950',         icon: 'text-red-600 dark:text-red-400',         val: 'text-red-700 dark:text-red-300' },
    info:     { bg: 'bg-blue-50 dark:bg-blue-950',       icon: 'text-blue-600 dark:text-blue-400',       val: 'text-blue-700 dark:text-blue-300' },
  }
  const c = colors[color] || colors.primary

  return (
    <Card hover className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-surface-500 dark:text-surface-400 font-medium mb-1">{label}</p>
          <p className={`text-3xl font-bold ${c.val}`}>{value ?? '—'}</p>
          {trend && <p className="text-xs text-surface-400 mt-1">{trend}</p>}
        </div>
        {Icon && (
          <div className={`w-11 h-11 rounded-2xl ${c.bg} flex items-center justify-center flex-shrink-0`}>
            <Icon size={22} className={c.icon} />
          </div>
        )}
      </div>
    </Card>
  )
}
