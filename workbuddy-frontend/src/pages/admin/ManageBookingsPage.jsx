import { useState, useEffect } from 'react'
import { Calendar } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { BookingCard }  from '../../components/common/BookingCard'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { EmptyState }   from '../../components/ui/EmptyState'
import { SearchInput }  from '../../components/ui/SearchInput'
import { Pagination }   from '../../components/ui/Pagination'
import { getCustomerBookings } from '../../services/customerService'
import { useDebounce }  from '../../hooks/useDebounce'
import { usePagination } from '../../hooks/usePagination'
import toast from 'react-hot-toast'

const STATUS_FILTERS = ['all', 'pending', 'accepted', 'completed', 'cancelled', 'rejected']

export default function ManageBookingsPage() {
  const [bookings, setBookings] = useState([])
  const [loading, setLoading]   = useState(true)
  const [search, setSearch]     = useState('')
  const [statusFilter, setStatus] = useState('all')

  const debounced = useDebounce(search, 300)

  useEffect(() => {
    getCustomerBookings()
      .then(r => setBookings(r.data.bookings || []))
      .catch(() => toast.error('Failed to load bookings'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = bookings.filter(b => {
    const matchStatus = statusFilter === 'all' || b.status === statusFilter
    const matchSearch = !debounced || JSON.stringify(b).toLowerCase().includes(debounced.toLowerCase())
    return matchStatus && matchSearch
  })

  const { paged, page, totalPages, next, prev, goTo } = usePagination(filtered, 12)

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="page-title mb-1">Manage Bookings</h1>
        <p className="text-surface-500 text-sm">Overview of all platform bookings</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <SearchInput value={search} onChange={setSearch} placeholder="Search bookings..." className="max-w-xs" />
        <div className="flex gap-2 flex-wrap">
          {STATUS_FILTERS.map(s => (
            <button key={s} onClick={() => setStatus(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors ${
                statusFilter === s
                  ? 'bg-primary-600 text-white'
                  : 'bg-surface-100 dark:bg-surface-800 text-surface-600 dark:text-surface-400 hover:bg-surface-200 dark:hover:bg-surface-700'
              }`}>{s}</button>
          ))}
        </div>
      </div>

      {loading ? <SpinnerOverlay /> :
       paged.length === 0 ? (
        <EmptyState icon={Calendar} title="No bookings found"
          description={debounced ? `No bookings match "${debounced}"` : 'No bookings match the current filter.'} />
       ) : (
        <>
          <p className="text-sm text-surface-500 mb-4">{filtered.length} booking{filtered.length !== 1 ? 's' : ''}</p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {paged.map(b => <BookingCard key={b.id} booking={b} />)}
          </div>
          <Pagination page={page} totalPages={totalPages} onPrev={prev} onNext={next} onGoTo={goTo} />
        </>
       )
      }
    </DashboardLayout>
  )
}
