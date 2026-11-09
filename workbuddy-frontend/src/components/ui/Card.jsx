export function Card({ children, className = '', hover = true, ...props }) {
  return (
    <div
      className={`
        bg-white dark:bg-surface-800
        border border-surface-100 dark:border-surface-700
        rounded-2xl shadow-card transition-all duration-200
        ${hover ? 'hover:shadow-card-hover hover:-translate-y-0.5' : ''}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className = '' }) {
  return (
    <div className={`px-6 py-4 border-b border-surface-100 dark:border-surface-700 ${className}`}>
      {children}
    </div>
  )
}

export function CardBody({ children, className = '' }) {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>
}

export function CardFooter({ children, className = '' }) {
  return (
    <div className={`px-6 py-4 border-t border-surface-100 dark:border-surface-700 ${className}`}>
      {children}
    </div>
  )
}
