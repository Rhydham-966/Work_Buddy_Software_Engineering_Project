import { useState, useEffect } from 'react'
import { Calendar, History, X } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { BookingCard }  from '../../components/common/BookingCard'
import { Button }       from '../../components/ui/Button'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { EmptyState }   from '../../components/ui/EmptyState'
import { getCustomerBookings, getCustomerHistory, cancelBooking } from '../../services/customerService'
import toast from 'react-hot-toast'

const TABS = [
  { key: 'active',  label: 'Active Bookings', icon: Calendar },
  { key: 'history', label: 'History',          icon: History  },
]

export default function BookingsPage() {
  const [tab, setTab]           = useState('active')
  const [bookings, setBookings] = useState([])
  const [history, setHistory]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [cancelling, setCancelling] = useState(null)

  const fetchData = () => {
    setLoading(true)
    Promise.all([getCustomerBookings(), getCustomerHistory()])
      .then(([bRes, hRes]) => {
        setBookings(bRes.data.bookings || [])
        setHistory(hRes.data.bookings  || [])
      })
      .catch(() => toast.error('Failed to load bookings'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const handleCancel = async (bookingId) => {
    setCancelling(bookingId)
    try {
      const res = await cancelBooking(bookingId)
      if (res.data.success) {
        toast.success('Booking cancelled')
        fetchData()
      } else {
        toast.error(res.data.message || 'Could not cancel')
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error cancelling booking')
    } finally {
      setCancelling(null)
    }
  }

  const displayed = tab === 'active' ? bookings : history

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="page-title mb-1">My Bookings</h1>
        <p className="text-surface-500 text-sm">Track your service bookings</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-surface-100 dark:bg-surface-800 rounded-xl w-fit mb-6">
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.key
                ? 'bg-white dark:bg-surface-700 text-primary-700 dark:text-primary-300 shadow-sm'
                : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
            }`}
          >
            <t.icon size={15} />
            {t.label}
            <span className="ml-1 text-xs rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 px-1.5">
              {tab === t.key ? displayed.length : (t.key === 'active' ? bookings.length : history.length)}
            </span>
          </button>
        ))}
      </div>

      {loading ? (
        <SpinnerOverlay text="Loading bookings..." />
      ) : displayed.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title={tab === 'active' ? 'No active bookings' : 'No booking history'}
          description={tab === 'active' ? 'Book a service to see it here.' : 'Completed bookings will appear here.'}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {displayed.map(b => (
            <BookingCard
              key={b.id}
              booking={b}
              actions={
                tab === 'active' && ['pending', 'accepted'].includes(b.status) ? (
                  <Button
                    variant="danger"
                    size="sm"
                    icon={<X size={14} />}
                    loading={cancelling === b.id}
                    onClick={() => handleCancel(b.id)}
                  >
                    Cancel
                  </Button>
                ) : null
              }
            />
          ))}
        </div>
      )}
    </DashboardLayout>
  )
}
