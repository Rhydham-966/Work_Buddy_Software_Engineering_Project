export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center animate-fade-in">
      {Icon && (
        <div className="w-20 h-20 rounded-3xl bg-surface-100 dark:bg-surface-800 flex items-center justify-center mb-5">
          <Icon size={36} className="text-surface-400" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-surface-700 dark:text-surface-300 mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-surface-500 dark:text-surface-500 max-w-sm mb-6">{description}</p>
      )}
      {action}
    </div>
  )
}
