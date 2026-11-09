import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Briefcase, Calendar, User, Users, Settings,
  ClipboardList, Shield, ChevronRight, Menu, X, Moon, Sun, LogOut,
  Bell, Wrench, Clock
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import toast from 'react-hot-toast'

const NAV = {
  customer: [
    { to: '/customer/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/customer/services',  icon: Briefcase,       label: 'Services' },
    { to: '/customer/bookings',  icon: Calendar,        label: 'My Bookings' },
    { to: '/customer/profile',   icon: User,            label: 'Profile' },
  ],
  professional: [
    { to: '/professional/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/professional/requests',  icon: ClipboardList,   label: 'Booking Requests' },
    { to: '/professional/services',  icon: Wrench,          label: 'My Services' },
    { to: '/professional/slots',     icon: Clock,           label: 'My Slots' },
    { to: '/professional/profile',   icon: User,            label: 'Profile' },
  ],
  admin: [
    { to: '/admin/dashboard',  icon: Shield,        label: 'Dashboard' },
    { to: '/admin/users',      icon: Users,         label: 'Manage Users' },
    { to: '/admin/services',   icon: Settings,      label: 'Manage Services' },
    { to: '/admin/bookings',   icon: Calendar,      label: 'Manage Bookings' },
  ],
}

const ROLE_COLOR = {
  customer:     'from-primary-600 to-primary-700',
  professional: 'from-emerald-600 to-teal-700',
  admin:        'from-rose-600 to-pink-700',
}

const ROLE_BADGE = {
  customer:     'bg-primary-100 text-primary-700',
  professional: 'bg-emerald-100 text-emerald-700',
  admin:        'bg-rose-100 text-rose-700',
}

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth()
  const { dark, toggle } = useTheme()
  const location = useLocation()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const role  = user?.role || 'customer'
  const links = NAV[role] || []
  const gradient = ROLE_COLOR[role]
  const roleBadge = ROLE_BADGE[role]

  const handleLogout = async () => {
    await logout()
    toast.success('Logged out successfully')
    navigate('/login')
  }

  const Sidebar = ({ mobile = false }) => (
    <aside className={`
      flex flex-col h-full w-64 bg-white dark:bg-surface-900 border-r border-surface-100 dark:border-surface-800
      ${mobile ? '' : 'fixed left-0 top-0 z-30 hidden lg:flex'}
    `}>
      {/* Logo */}
      <div className={`flex items-center gap-3 px-5 py-5 bg-gradient-to-r ${gradient}`}>
        <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
          <span className="text-white font-black text-lg">W</span>
        </div>
        <div>
          <div className="text-white font-bold text-base">WorkBuddy</div>
          <div className={`text-xs px-1.5 py-0.5 rounded-full ${roleBadge} font-semibold capitalize inline-block mt-0.5`}>
            {role}
          </div>
        </div>
      </div>

      {/* Nav links */}
      <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
        {links.map(({ to, icon: Icon, label }) => {
          const active = location.pathname === to || location.pathname.startsWith(to + '/')
          return (
            <Link
              key={to}
              to={to}
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
                ${active
                  ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300'
                  : 'text-surface-600 hover:text-primary-600 hover:bg-primary-50 dark:text-surface-400 dark:hover:text-primary-400 dark:hover:bg-primary-950'
                }`}
            >
              <Icon size={18} className="flex-shrink-0" />
              {label}
              {active && <ChevronRight size={14} className="ml-auto" />}
            </Link>
          )
        })}
      </nav>

      {/* User info + logout */}
      <div className="px-3 py-4 border-t border-surface-100 dark:border-surface-800 space-y-2">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${gradient} flex items-center justify-center flex-shrink-0`}>
            <span className="text-white text-sm font-bold">
              {user?.name?.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-surface-900 dark:text-surface-100 truncate">{user?.name}</p>
            <p className="text-xs text-surface-400 truncate">{user?.phone}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-red-500 hover:bg-red-50 dark:hover:bg-red-950 transition-colors"
        >
          <LogOut size={16} />
          Sign out
        </button>
      </div>
    </aside>
  )

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      {/* Desktop sidebar */}
      <Sidebar />

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-64 animate-slide-down">
            <Sidebar mobile />
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-20 bg-white/90 dark:bg-surface-900/90 backdrop-blur-sm border-b border-surface-100 dark:border-surface-800 px-4 sm:px-6 py-3.5 flex items-center gap-4">
          {/* Hamburger */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-xl text-surface-500 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
          >
            <Menu size={20} />
          </button>

          {/* Page title area (slot) */}
          <div className="flex-1" />

          <div className="flex items-center gap-2">
            {/* Dark mode toggle */}
            <button
              onClick={toggle}
              className="p-2 rounded-xl text-surface-500 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
              title="Toggle dark mode"
            >
              {dark ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            {/* Bell */}
            <button className="p-2 rounded-xl text-surface-500 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors">
              <Bell size={18} />
            </button>

            {/* Avatar */}
            <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${gradient} flex items-center justify-center`}>
              <span className="text-white text-sm font-bold">
                {user?.name?.charAt(0).toUpperCase()}
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  )
}
