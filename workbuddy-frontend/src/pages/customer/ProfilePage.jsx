import { User, Mail, Phone, Shield } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { Card, CardBody } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { useAuth } from '../../context/AuthContext'

export default function ProfilePage() {
  const { user } = useAuth()

  const fields = [
    { label: 'Full Name',  value: user?.name,  icon: User },
    { label: 'Email',      value: user?.email, icon: Mail },
    { label: 'Phone',      value: user?.phone, icon: Phone },
  ]

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="page-title mb-1">My Profile</h1>
        <p className="text-surface-500 text-sm">Your account information</p>
      </div>

      <div className="max-w-2xl">
        <Card hover={false} className="mb-6">
          <CardBody>
            {/* Avatar */}
            <div className="flex items-center gap-5 mb-8">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white text-3xl font-black shadow-glow">
                {user?.name?.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100">{user?.name}</h2>
                <Badge status="active" className="mt-1">Active Account</Badge>
              </div>
            </div>

            {/* Fields */}
            <div className="space-y-4">
              {fields.map(({ label, value, icon: Icon }) => (
                <div key={label} className="flex items-center gap-4 p-4 bg-surface-50 dark:bg-surface-800 rounded-xl">
                  <div className="w-10 h-10 rounded-xl bg-primary-100 dark:bg-primary-900 flex items-center justify-center flex-shrink-0">
                    <Icon size={18} className="text-primary-600 dark:text-primary-400" />
                  </div>
                  <div>
                    <p className="text-xs text-surface-400 font-medium">{label}</p>
                    <p className="text-surface-900 dark:text-surface-100 font-semibold">{value || '—'}</p>
                  </div>
                </div>
              ))}
              {/* Role */}
              <div className="flex items-center gap-4 p-4 bg-surface-50 dark:bg-surface-800 rounded-xl">
                <div className="w-10 h-10 rounded-xl bg-primary-100 dark:bg-primary-900 flex items-center justify-center flex-shrink-0">
                  <Shield size={18} className="text-primary-600 dark:text-primary-400" />
                </div>
                <div>
                  <p className="text-xs text-surface-400 font-medium">Role</p>
                  <Badge status={user?.role} className="mt-0.5">{user?.role}</Badge>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        <div className="p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-xl text-sm text-amber-700 dark:text-amber-400">
          <strong>Note:</strong> Profile editing is managed by the system administrator.
          Contact support to update your details.
        </div>
      </div>
    </DashboardLayout>
  )
}
