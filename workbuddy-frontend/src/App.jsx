import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { ProtectedRoute } from './components/common/ProtectedRoute'

// Auth
import LoginPage    from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'

// Customer
import CustomerDashboard from './pages/customer/CustomerDashboard'
import ServicesPage      from './pages/customer/ServicesPage'
import ServiceDetailPage from './pages/customer/ServiceDetailPage'
import BookingsPage      from './pages/customer/BookingsPage'
import ProfilePage       from './pages/customer/ProfilePage'

// Professional
import ProfessionalDashboard    from './pages/professional/ProfessionalDashboard'
import BookingRequestsPage      from './pages/professional/BookingRequestsPage'
import ManageServicesPage       from './pages/professional/ManageServicesPage'
import ManageSlotsPage          from './pages/professional/ManageSlotsPage'
import ProfessionalProfilePage  from './pages/professional/ProfessionalProfilePage'

// Admin
import AdminDashboard         from './pages/admin/AdminDashboard'
import ManageUsersPage        from './pages/admin/ManageUsersPage'
import AdminManageServicesPage from './pages/admin/AdminManageServicesPage'
import ManageBookingsPage     from './pages/admin/ManageBookingsPage'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 3500,
              style: {
                borderRadius: '12px',
                fontSize: '14px',
                fontFamily: 'Inter, sans-serif',
              },
              success: { iconTheme: { primary: '#22c55e', secondary: '#fff' } },
              error:   { iconTheme: { primary: '#ef4444', secondary: '#fff' } },
            }}
          />

          <Routes>
            {/* Root redirect */}
            <Route path="/" element={<Navigate to="/login" replace />} />

            {/* Auth */}
            <Route path="/login"    element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Customer routes */}
            <Route path="/customer/dashboard" element={
              <ProtectedRoute role="customer"><CustomerDashboard /></ProtectedRoute>} />
            <Route path="/customer/services" element={
              <ProtectedRoute role="customer"><ServicesPage /></ProtectedRoute>} />
            <Route path="/customer/services/:id" element={
              <ProtectedRoute role="customer"><ServiceDetailPage /></ProtectedRoute>} />
            <Route path="/customer/bookings" element={
              <ProtectedRoute role="customer"><BookingsPage /></ProtectedRoute>} />
            <Route path="/customer/profile" element={
              <ProtectedRoute role="customer"><ProfilePage /></ProtectedRoute>} />

            {/* Professional routes */}
            <Route path="/professional/dashboard" element={
              <ProtectedRoute role="professional"><ProfessionalDashboard /></ProtectedRoute>} />
            <Route path="/professional/requests" element={
              <ProtectedRoute role="professional"><BookingRequestsPage /></ProtectedRoute>} />
            <Route path="/professional/services" element={
              <ProtectedRoute role="professional"><ManageServicesPage /></ProtectedRoute>} />
            <Route path="/professional/slots" element={
              <ProtectedRoute role="professional"><ManageSlotsPage /></ProtectedRoute>} />
            <Route path="/professional/profile" element={
              <ProtectedRoute role="professional"><ProfessionalProfilePage /></ProtectedRoute>} />

            {/* Admin routes */}
            <Route path="/admin/dashboard" element={
              <ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>} />
            <Route path="/admin/users" element={
              <ProtectedRoute role="admin"><ManageUsersPage /></ProtectedRoute>} />
            <Route path="/admin/services" element={
              <ProtectedRoute role="admin"><AdminManageServicesPage /></ProtectedRoute>} />
            <Route path="/admin/bookings" element={
              <ProtectedRoute role="admin"><ManageBookingsPage /></ProtectedRoute>} />

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
