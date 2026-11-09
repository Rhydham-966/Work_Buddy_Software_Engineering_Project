import { useState, useEffect } from 'react'
import { Users, CheckCircle, XCircle } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { Button }       from '../../components/ui/Button'
import { Badge }        from '../../components/ui/Badge'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { EmptyState }   from '../../components/ui/EmptyState'
import { getPendingProfessionals, approveProfessional, rejectProfessional } from '../../services/adminService'
import toast from 'react-hot-toast'

export default function ManageUsersPage() {
  const [professionals, setPros] = useState([])
  const [loading, setLoading]    = useState(true)
  const [acting, setActing]      = useState(null)

  const fetchData = () => {
    setLoading(true)
    getPendingProfessionals()
      .then(r => setPros(r.data.professionals || []))
      .catch(() => toast.error('Failed to load professionals'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const doAction = async (fn, id, label) => {
    setActing(id)
    try {
      const res = await fn(id)
      toast.success(label)
      fetchData()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Action failed')
    } finally {
      setActing(null) }
  }

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="page-title mb-1">Manage Users</h1>
        <p className="text-surface-500 text-sm">Review and approve pending professional registrations</p>
      </div>

      {loading ? <SpinnerOverlay /> :
       professionals.length === 0 ? (
        <EmptyState icon={Users} title="No pending approvals" description="All professionals have been reviewed." />
       ) : (
        <div className="bg-white dark:bg-surface-800 border border-surface-100 dark:border-surface-700 rounded-2xl overflow-hidden shadow-card">
          <div className="px-5 py-3 bg-surface-50 dark:bg-surface-700 border-b border-surface-100 dark:border-surface-600">
            <p className="text-sm font-semibold text-surface-600 dark:text-surface-300">
              {professionals.length} pending professional{professionals.length > 1 ? 's' : ''}
            </p>
          </div>
          <div className="divide-y divide-surface-100 dark:divide-surface-700">
            {professionals.map(p => (
              <div key={p.id} className="flex items-center justify-between gap-4 px-5 py-4 hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-colors">
                <div className="flex items-center gap-4 min-w-0">
                  {/* Avatar */}
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white font-bold flex-shrink-0">
                    {p.user_name?.charAt(0)?.toUpperCase() || 'P'}
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-surface-900 dark:text-surface-100 truncate">
                      {p.user_name || `Professional #${p.id}`}
                    </p>
                    <p className="text-xs text-surface-500 truncate">
                      {p.area} • {p.experience} yrs • Radius: {p.work_radius}km
                    </p>
                    {p.services_offered?.length > 0 && (
                      <p className="text-xs text-primary-500 mt-0.5">
                        Services: {p.services_offered.map(s => s.service_name || s.name).join(', ')}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  <Badge status="pending">Pending</Badge>
                  <Button size="sm" variant="success" loading={acting === p.id}
                    icon={<CheckCircle size={14} />}
                    onClick={() => doAction(() => approveProfessional(p.id), p.id, 'Professional approved!')}>
                    Approve
                  </Button>
                  <Button size="sm" variant="danger" loading={acting === p.id}
                    icon={<XCircle size={14} />}
                    onClick={() => doAction(() => rejectProfessional(p.id), p.id, 'Professional rejected')}>
                    Reject
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
       )
      }
    </DashboardLayout>
  )
}
