import { useState, useEffect } from 'react'
import { ClipboardList, History } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { BookingCard }  from '../../components/common/BookingCard'
import { Button }       from '../../components/ui/Button'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { EmptyState }   from '../../components/ui/EmptyState'
import {
  getProfessionalBookings, getProfessionalHistory,
  acceptBooking, rejectBooking, completeBooking
} from '../../services/professionalService'
import toast from 'react-hot-toast'

const TABS = [
  { key: 'requests', label: 'Requests',  icon: ClipboardList },
  { key: 'history',  label: 'History',   icon: History },
]

export default function BookingRequestsPage() {
  const [tab, setTab]     = useState('requests')
  const [requests, setRequests] = useState([])
  const [history, setHistory]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [acting, setActing]     = useState(null)

  const fetchData = () => {
    setLoading(true)
    Promise.all([getProfessionalBookings(), getProfessionalHistory()])
      .then(([bRes, hRes]) => {
        setRequests(bRes.data.bookings || [])
        setHistory(hRes.data.bookings  || [])
      })
      .catch(() => toast.error('Failed to load bookings'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const doAction = async (fn, id, label) => {
    setActing(id)
    try {
      const res = await fn(id)
      if (res.data.success) { toast.success(label); fetchData() }
      else toast.error(res.data.message)
    } catch (err) { toast.error(err.response?.data?.message || 'Action failed') }
    finally { setActing(null) }
  }

  const displayed = tab === 'requests' ? requests : history

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="page-title mb-1">Booking Requests</h1>
        <p className="text-surface-500 text-sm">Manage incoming service requests</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-surface-100 dark:bg-surface-800 rounded-xl w-fit mb-6">
        {TABS.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.key
                ? 'bg-white dark:bg-surface-700 text-primary-700 dark:text-primary-300 shadow-sm'
                : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
            }`}>
            <t.icon size={15} /> {t.label}
            <span className="text-xs rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 px-1.5">
              {t.key === 'requests' ? requests.length : history.length}
            </span>
          </button>
        ))}
      </div>

      {loading ? <SpinnerOverlay text="Loading..." /> :
       displayed.length === 0 ? (
        <EmptyState icon={ClipboardList} title="No bookings here" description="They will appear when customers book you." />
       ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {displayed.map(b => (
            <BookingCard key={b.id} booking={b} actions={
              tab === 'requests' ? (
                b.status === 'pending' ? (
                  <>
                    <Button size="sm" variant="success" loading={acting === b.id}
                      onClick={() => doAction(acceptBooking, b.id, 'Booking accepted!')}>Accept</Button>
                    <Button size="sm" variant="danger" loading={acting === b.id}
                      onClick={() => doAction(rejectBooking, b.id, 'Booking rejected')}>Reject</Button>
                  </>
                ) : b.status === 'accepted' ? (
                  <Button size="sm" variant="primary" loading={acting === b.id}
                    onClick={() => doAction(completeBooking, b.id, 'Marked as complete!')}>Mark Complete</Button>
                ) : null
              ) : null
            } />
          ))}
        </div>
       )
      }
    </DashboardLayout>
  )
}
