import { useState, useEffect } from 'react'
import { Users, Briefcase, Calendar, TrendingUp } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { StatsCard }   from '../../components/common/StatsCard'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { getAllServices, getPendingProfessionals } from '../../services/adminService'
import toast from 'react-hot-toast'

export default function AdminDashboard() {
  const [services, setServices] = useState([])
  const [pending, setPending]   = useState([])
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    Promise.all([getAllServices(), getPendingProfessionals()])
      .then(([sRes, pRes]) => {
        setServices(sRes.data.services || [])
        setPending(pRes.data.professionals || [])
      })
      .catch(() => toast.error('Failed to load dashboard data'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <DashboardLayout>
      {/* Hero */}
      <div className="relative rounded-3xl overflow-hidden mb-8 bg-gradient-to-r from-rose-600 to-pink-500 p-8 text-white">
        <div className="relative">
          <p className="text-white/80 text-sm font-medium mb-1">🛡️ Admin Panel</p>
          <h1 className="text-3xl font-bold mb-1">System Overview</h1>
          <p className="text-white/70">Monitor users, services, and bookings across the platform.</p>
        </div>
        <div className="absolute right-8 top-8 text-7xl opacity-20 select-none">⚙️</div>
      </div>

      {loading ? <SpinnerOverlay /> : (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
            <StatsCard label="Total Services"       value={services.length}                  icon={Briefcase}    color="primary" />
            <StatsCard label="Pending Approvals"    value={pending.length}                   icon={Users}        color="warning" />
            <StatsCard label="Active Services"      value={services.length}                  icon={TrendingUp}   color="success" />
            <StatsCard label="Platform Health"      value="✓ OK"                             icon={Calendar}     color="info" />
          </div>

          {/* Pending professionals table */}
          {pending.length > 0 && (
            <div>
              <h2 className="text-xl font-bold text-surface-900 dark:text-surface-100 mb-4">Pending Approvals</h2>
              <div className="bg-white dark:bg-surface-800 border border-surface-100 dark:border-surface-700 rounded-2xl overflow-hidden shadow-card">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-surface-50 dark:bg-surface-700">
                      {['Name','Area','Experience','Approval Status'].map(h => (
                        <th key={h} className="text-left px-5 py-3 text-surface-500 font-semibold text-xs uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-surface-100 dark:divide-surface-700">
                    {pending.map(p => (
                      <tr key={p.id} className="hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-colors">
                        <td className="px-5 py-3 font-medium text-surface-900 dark:text-surface-100">{p.user_name || `Professional #${p.id}`}</td>
                        <td className="px-5 py-3 text-surface-500">{p.area}</td>
                        <td className="px-5 py-3 text-surface-500">{p.experience} yrs</td>
                        <td className="px-5 py-3">
                          <span className="badge badge-pending">Pending</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </DashboardLayout>
  )
}
