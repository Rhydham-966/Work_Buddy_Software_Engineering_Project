import api from './api'

export const login = (phone, password) =>
  api.post('/login', { phone, password })

export const register = (name, email, phone, password, role) =>
  api.post('/register', { name, email, phone, password, role })

export const verifyOtp = (user_id, otp) =>
  api.post('/verify-otp', { user_id, otp })

export const logout = () =>
  api.post('/logout')

export const getMe = () =>
  api.get('/me')
