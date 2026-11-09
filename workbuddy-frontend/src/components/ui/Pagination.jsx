import { ChevronLeft, ChevronRight } from 'lucide-react'

export function Pagination({ page, totalPages, onPrev, onNext, onGoTo }) {
  if (totalPages <= 1) return null

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1)

  return (
    <div className="flex items-center justify-center gap-1 mt-6">
      <button
        onClick={onPrev}
        disabled={page === 1}
        className="p-2 rounded-lg text-surface-500 hover:bg-surface-100 dark:hover:bg-surface-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        <ChevronLeft size={18} />
      </button>

      {pages.map(p => (
        <button
          key={p}
          onClick={() => onGoTo(p)}
          className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${
            p === page
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-surface-600 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-700'
          }`}
        >
          {p}
        </button>
      ))}

      <button
        onClick={onNext}
        disabled={page === totalPages}
        className="p-2 rounded-lg text-surface-500 hover:bg-surface-100 dark:hover:bg-surface-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        <ChevronRight size={18} />
      </button>
    </div>
  )
}
