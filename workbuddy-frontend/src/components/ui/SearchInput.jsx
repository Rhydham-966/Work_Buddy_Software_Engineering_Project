import { Search } from 'lucide-react'

export function SearchInput({ value, onChange, placeholder = 'Search...', className = '' }) {
  return (
    <div className={`relative ${className}`}>
      <Search
        size={16}
        className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none"
      />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="input-field pl-10 pr-4"
      />
    </div>
  )
}
