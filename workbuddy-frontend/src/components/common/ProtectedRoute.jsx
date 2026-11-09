import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Spinner } from '../ui/Spinner'

const ROLE_HOME = {
  customer:     '/customer/dashboard',
  professional: '/professional/dashboard',
  admin:        '/admin/dashboard',
}

export function ProtectedRoute({ children, role }) {
  const { user, loading, isAuthenticated } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-600 to-primary-400 flex items-center justify-center">
            <span className="text-white font-black text-xl">W</span>
          </div>
          <Spinner size={28} />
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // If a specific role is required
  if (role && user.role !== role) {
    return <Navigate to={ROLE_HOME[user.role] || '/login'} replace />
  }

  return children
}
