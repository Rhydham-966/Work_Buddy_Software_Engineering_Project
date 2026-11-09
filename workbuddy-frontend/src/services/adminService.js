import api from './api'

export const addService = (name, description, base_price, estimated_time) =>
  api.post('/admin/services', { name, description, base_price, estimated_time })

export const getPendingProfessionals = () =>
  api.get('/admin/professionals')

export const approveProfessional = (id) =>
  api.post(`/admin/approve/${id}`)

export const rejectProfessional = (id) =>
  api.post(`/admin/reject/${id}`)

// Reuse public endpoints
export const getAllServices = () =>
  api.get('/services')

export const getAllBookings = () =>
  api.get('/customer/bookings')
