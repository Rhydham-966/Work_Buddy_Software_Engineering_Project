import { useState, useEffect } from 'react'
import { ClipboardList, CheckCircle, Clock, Briefcase, AlertTriangle } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { StatsCard }   from '../../components/common/StatsCard'
import { BookingCard }  from '../../components/common/BookingCard'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { EmptyState }   from '../../components/ui/EmptyState'
import { Button }       from '../../components/ui/Button'
import { Badge }        from '../../components/ui/Badge'
import { useAuth }      from '../../context/AuthContext'
import {
  getProfile, getProfessionalBookings, getProfessionalHistory,
  acceptBooking, rejectBooking, completeBooking
} from '../../services/professionalService'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function ProfessionalDashboard() {
  const { user }     = useAuth()
  const navigate     = useNavigate()
  const [profile, setProfile]   = useState(null)
  const [bookings, setBookings] = useState([])
  const [history, setHistory]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [acting, setActing]     = useState(null)

  const fetchAll = () => {
    setLoading(true)
    Promise.all([getProfile(), getProfessionalBookings(), getProfessionalHistory()])
      .then(([pRes, bRes, hRes]) => {
        setProfile(pRes.data.profile)
        setBookings(bRes.data.bookings || [])
        setHistory(hRes.data.bookings  || [])
      })
      .catch(() => toast.error('Failed to load data'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchAll() }, [])

  const doAction = async (fn, id, label) => {
    setActing(id)
    try {
      const res = await fn(id)
      if (res.data.success) { toast.success(res.data.message || label); fetchAll() }
      else toast.error(res.data.message)
    } catch (err) { toast.error(err.response?.data?.message || 'Action failed') }
    finally { setActing(null) }
  }

  const pending   = bookings.filter(b => b.status === 'pending').length
  const completed = history.filter(b => b.status === 'completed').length

  return (
    <DashboardLayout>
      {/* Approval warning */}
      {profile && !profile.is_approved && (
        <div className="mb-6 flex items-start gap-3 p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-2xl">
          <AlertTriangle size={20} className="text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-amber-800 dark:text-amber-300">Profile Pending Approval</p>
            <p className="text-sm text-amber-700 dark:text-amber-400 mt-0.5">
              Your profile is awaiting admin approval. You can prepare your services meanwhile.
            </p>
          </div>
        </div>
      )}

      {/* Hero */}
      <div className="relative rounded-3xl overflow-hidden mb-8 bg-gradient-to-r from-emerald-600 to-teal-500 p-8 text-white">
        <div className="relative">
          <p className="text-white/80 text-sm font-medium mb-1">Professional Dashboard</p>
          <h1 className="text-3xl font-bold mb-1">Hello, {user?.name} 👋</h1>
          <p className="text-white/70 mb-5">Manage your bookings and services from here.</p>
          {!profile && !loading && (
            <Button variant="secondary" size="md" onClick={() => navigate('/professional/profile')}>
              Complete Your Profile →
            </Button>
          )}
          {profile && (
            <div className="flex items-center gap-3">
              <Badge status={profile.is_approved ? 'approved' : 'pending'}>
                {profile.is_approved ? 'Approved' : 'Pending'}
              </Badge>
              <span className="text-white/70 text-sm">{profile.area} • {profile.experience} yrs exp</span>
            </div>
          )}
        </div>
        <div className="absolute right-8 top-8 text-7xl opacity-20 select-none">🛠️</div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatsCard label="Total Bookings"  value={bookings.length + history.length} icon={ClipboardList} color="primary" />
        <StatsCard label="Pending"         value={pending}   icon={Clock}         color="warning" />
        <StatsCard label="Active"          value={bookings.filter(b => b.status === 'accepted').length} icon={Briefcase} color="info" />
        <StatsCard label="Completed"       value={completed} icon={CheckCircle}   color="success" />
      </div>

      {/* Recent Requests */}
      <h2 className="text-xl font-bold text-surface-900 dark:text-surface-100 mb-4">Recent Requests</h2>
      {loading ? <SpinnerOverlay /> :
       bookings.length === 0 ? (
        <EmptyState icon={ClipboardList} title="No pending requests" description="Booking requests will appear here." />
       ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {bookings.slice(0, 6).map(b => (
            <BookingCard key={b.id} booking={b} actions={
              b.status === 'pending' ? (
                <>
                  <Button size="sm" variant="success" loading={acting === b.id}
                    onClick={() => doAction(acceptBooking, b.id, 'Booking accepted')}>Accept</Button>
                  <Button size="sm" variant="danger" loading={acting === b.id}
                    onClick={() => doAction(rejectBooking, b.id, 'Booking rejected')}>Reject</Button>
                </>
              ) : b.status === 'accepted' ? (
                <Button size="sm" variant="primary" loading={acting === b.id}
                  onClick={() => doAction(completeBooking, b.id, 'Marked as complete')}>Mark Complete</Button>
              ) : null
            } />
          ))}
        </div>
       )
      }
    </DashboardLayout>
  )
}
