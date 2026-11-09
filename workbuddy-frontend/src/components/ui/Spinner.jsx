import { Loader2 } from 'lucide-react'

export function Spinner({ size = 24, className = '' }) {
  return (
    <Loader2
      size={size}
      className={`animate-spin text-primary-500 ${className}`}
    />
  )
}

export function SpinnerOverlay({ text = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-surface-400">
      <Spinner size={36} />
      <p className="text-sm">{text}</p>
    </div>
  )
}
