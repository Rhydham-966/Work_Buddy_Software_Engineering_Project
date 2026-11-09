import api from './api'

export const getServices = () =>
  api.get('/services')

export const getProfessionals = (serviceId) =>
  api.get(`/professionals/${serviceId}`)

export const getSlots = (professionalId) =>
  api.get(`/slots/${professionalId}`)

export const createBooking = (data) =>
  api.post('/bookings', data)

export const getCustomerBookings = () =>
  api.get('/customer/bookings')

export const getCustomerHistory = () =>
  api.get('/customer/history')

export const cancelBooking = (bookingId) =>
  api.post(`/customer/cancel/${bookingId}`)
