import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, CheckCircle, Clock, Briefcase, ArrowRight, Sparkles } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { StatsCard }   from '../../components/common/StatsCard'
import { ServiceCard }  from '../../components/common/ServiceCard'
import { SkeletonGrid } from '../../components/ui/Skeleton'
import { EmptyState }   from '../../components/ui/EmptyState'
import { useAuth } from '../../context/AuthContext'
import { getServices } from '../../services/customerService'
import { getCustomerBookings } from '../../services/customerService'
import toast from 'react-hot-toast'

export default function CustomerDashboard() {
  const { user }         = useAuth()
  const navigate         = useNavigate()
  const [services, setServices]   = useState([])
  const [bookings, setBookings]   = useState([])
  const [loadingSvc, setLoadingSvc] = useState(true)

  useEffect(() => {
    getServices()
      .then(r => setServices(r.data.services || []))
      .catch(() => toast.error('Failed to load services'))
      .finally(() => setLoadingSvc(false))

    getCustomerBookings()
      .then(r => setBookings(r.data.bookings || []))
      .catch(() => {})
  }, [])

  const pending   = bookings.filter(b => b.status === 'pending').length
  const accepted  = bookings.filter(b => b.status === 'accepted').length
  const completed = bookings.filter(b => b.status === 'completed').length

  return (
    <DashboardLayout>
      {/* Hero banner */}
      <div className="relative rounded-3xl overflow-hidden mb-8 bg-gradient-to-r from-primary-600 via-primary-500 to-accent-500 p-8 text-white">
        <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-2 text-white/80 text-sm font-medium">
            <Sparkles size={16} />
            <span>Welcome back</span>
          </div>
          <h1 className="text-3xl font-bold mb-1">{user?.name} 👋</h1>
          <p className="text-white/80 mb-6">Find and book professional services near you</p>
          <button
            onClick={() => navigate('/customer/services')}
            className="inline-flex items-center gap-2 bg-white text-primary-700 font-semibold px-5 py-2.5 rounded-xl hover:bg-white/90 transition-colors shadow-md"
          >
            Browse Services <ArrowRight size={16} />
          </button>
        </div>
        {/* Decorative */}
        <div className="absolute right-8 top-8 text-7xl opacity-20 select-none">🔧</div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatsCard label="Total Bookings"    value={bookings.length} icon={Calendar}     color="primary" />
        <StatsCard label="Pending"           value={pending}         icon={Clock}        color="warning" />
        <StatsCard label="Confirmed"         value={accepted}        icon={CheckCircle}  color="info"    />
        <StatsCard label="Completed"         value={completed}       icon={CheckCircle}  color="success" />
      </div>

      {/* Available Services */}
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-xl font-bold text-surface-900 dark:text-surface-100">Available Services</h2>
        <button
          onClick={() => navigate('/customer/services')}
          className="text-sm text-primary-600 dark:text-primary-400 font-semibold hover:underline flex items-center gap-1"
        >
          View all <ArrowRight size={14} />
        </button>
      </div>
      {loadingSvc
        ? <SkeletonGrid count={3} />
        : services.length === 0
          ? <EmptyState icon={Briefcase} title="No services available" description="Check back later for new services." />
          : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {services.slice(0, 6).map(s => <ServiceCard key={s.id} service={s} />)}
            </div>
          )
      }
    </DashboardLayout>
  )
}
