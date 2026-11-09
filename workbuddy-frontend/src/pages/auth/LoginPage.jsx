import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Phone, Lock, Eye, EyeOff } from 'lucide-react'
import AuthLayout from '../../layouts/AuthLayout'
import { Button } from '../../components/ui/Button'
import { useAuth } from '../../context/AuthContext'
import { login as apiLogin } from '../../services/authService'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [form, setForm]       = useState({ phone: '', password: '' })
  const [showPwd, setShowPwd] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login }             = useAuth()
  const navigate              = useNavigate()

  const ROLE_HOME = {
    customer:     '/customer/dashboard',
    professional: '/professional/dashboard',
    admin:        '/admin/dashboard',
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.phone || !form.password) {
      toast.error('Please fill in all fields')
      return
    }
    setLoading(true)
    try {
      const res = await apiLogin(form.phone, form.password)
      if (res.data.success) {
        login(res.data.user)
        toast.success(`Welcome back, ${res.data.user.name}! 👋`)
        navigate(ROLE_HOME[res.data.user.role] || '/customer/dashboard')
      } else {
        toast.error(res.data.message || 'Login failed')
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout>
      <div className="px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-100 mb-1">Welcome back</h1>
          <p className="text-surface-500 text-sm">Sign in to your WorkBuddy account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Phone */}
          <div>
            <label className="form-label">Phone Number</label>
            <div className="relative">
              <Phone size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
              <input
                id="login-phone"
                type="text"
                value={form.phone}
                onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                placeholder="Enter phone or username"
                className="input-field pl-10"
                autoComplete="username"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="form-label">Password</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
              <input
                id="login-password"
                type={showPwd ? 'text' : 'password'}
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                placeholder="Enter password"
                className="input-field pl-10 pr-10"
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPwd(s => !s)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600 transition-colors"
              >
                {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <Button type="submit" fullWidth loading={loading} size="lg">
            Sign In
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-surface-500">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-600 font-semibold hover:underline">
              Sign up
            </Link>
          </p>
        </div>

        {/* Demo hint */}
        <div className="mt-6 p-4 bg-surface-50 dark:bg-surface-800 rounded-xl border border-surface-100 dark:border-surface-700">
          <p className="text-xs text-surface-500 dark:text-surface-400 font-medium mb-2">🔑 Demo Credentials</p>
          <div className="grid grid-cols-3 gap-2 text-xs">
            {[
              { role: 'Customer', phone: 'cust1', pw: 'pass' },
              { role: 'Pro',      phone: 'pro1',  pw: 'pass' },
              { role: 'Admin',    phone: 'admin1', pw: 'pass' },
            ].map(c => (
              <button
                key={c.role}
                type="button"
                onClick={() => setForm({ phone: c.phone, password: c.pw })}
                className="p-2 bg-white dark:bg-surface-700 rounded-lg border border-surface-200 dark:border-surface-600 text-center hover:border-primary-300 hover:bg-primary-50 dark:hover:bg-primary-950 transition-colors"
              >
                <div className="font-semibold text-surface-700 dark:text-surface-300">{c.role}</div>
                <div className="text-surface-400">{c.phone}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </AuthLayout>
  )
}
