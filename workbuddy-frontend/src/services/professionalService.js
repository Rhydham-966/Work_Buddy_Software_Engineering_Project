import api from './api'

export const getProfile = () =>
  api.get('/professional/profile')

export const createProfile = (experience, area, work_radius) =>
  api.post('/professional/profile', { experience, area, work_radius })

export const addServicePricing = (service_id, custom_price) =>
  api.post('/professional/services', { service_id, custom_price })

export const getMySlots = () =>
  api.get('/professional/slots')

export const addSlot = (slot_date, start_time, end_time) =>
  api.post('/professional/slots', { slot_date, start_time, end_time })

export const getProfessionalBookings = () =>
  api.get('/professional/bookings')

export const getProfessionalHistory = () =>
  api.get('/professional/history')

export const acceptBooking = (bookingId) =>
  api.post(`/professional/accept/${bookingId}`)

export const rejectBooking = (bookingId) =>
  api.post(`/professional/reject/${bookingId}`)

export const completeBooking = (bookingId) =>
  api.post(`/professional/complete/${bookingId}`)

export const getAvailableServices = () =>
  api.get('/available-services')
