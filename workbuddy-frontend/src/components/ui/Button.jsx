import { Loader2 } from 'lucide-react'

const variants = {
  primary:   'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 shadow-sm hover:shadow-glow disabled:bg-primary-300',
  secondary: 'bg-white text-primary-700 border border-primary-200 hover:bg-primary-50 active:bg-primary-100 dark:bg-surface-800 dark:text-primary-300 dark:border-primary-800 dark:hover:bg-primary-950',
  danger:    'bg-error text-white hover:bg-error-dark active:opacity-90 shadow-sm',
  ghost:     'bg-transparent text-surface-600 hover:bg-surface-100 hover:text-surface-900 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-100',
  success:   'bg-success text-white hover:bg-success-dark shadow-sm',
}

const sizes = {
  sm:  'px-3 py-1.5 text-xs rounded-lg gap-1.5',
  md:  'px-4 py-2.5 text-sm rounded-xl gap-2',
  lg:  'px-6 py-3 text-base rounded-xl gap-2.5',
  xl:  'px-8 py-4 text-lg rounded-2xl gap-3',
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  fullWidth = false,
  className = '',
  ...props
}) {
  return (
    <button
      className={`
        inline-flex items-center justify-center font-semibold transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]} ${sizes[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading ? (
        <Loader2 className="animate-spin" size={size === 'sm' ? 14 : 16} />
      ) : icon ? (
        <span className="flex-shrink-0">{icon}</span>
      ) : null}
      {children}
    </button>
  )
}
