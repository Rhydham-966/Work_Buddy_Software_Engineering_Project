import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, IndianRupee, Clock, User, Calendar } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { ProfessionalCard } from '../../components/common/ProfessionalCard'
import { Button }           from '../../components/ui/Button'
import { SpinnerOverlay }   from '../../components/ui/Spinner'
import { EmptyState }       from '../../components/ui/EmptyState'
import { getServices, getProfessionals, getSlots, createBooking } from '../../services/customerService'
import toast from 'react-hot-toast'

export default function ServiceDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [service, setService]         = useState(null)
  const [professionals, setPros]      = useState([])
  const [slots, setSlots]             = useState([])
  const [selectedPro, setSelectedPro] = useState(null)
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [paymentMethod, setPayMethod]   = useState('cash')
  const [booking, setBooking]         = useState(false)
  const [loading, setLoading]         = useState(true)

  useEffect(() => {
    getServices()
      .then(r => {
        const svc = (r.data.services || []).find(s => s.id === parseInt(id))
        setService(svc)
      })
      .catch(() => toast.error('Failed to load service'))

    getProfessionals(id)
      .then(r => { setPros(r.data.professionals || []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (!selectedPro) { setSlots([]); return }
    getSlots(selectedPro.professional_id || selectedPro.id)
      .then(r => setSlots(r.data.slots || []))
      .catch(() => setSlots([]))
    setSelectedSlot(null)
  }, [selectedPro])

  const handleBook = async () => {
    if (!selectedPro) { toast.error('Please select a professional'); return }
    setBooking(true)
    try {
      const res = await createBooking({
        professional_id: selectedPro.professional_id || selectedPro.id,
        service_id:      parseInt(id),
        booking_type:    selectedSlot ? 'scheduled' : 'instant',
        payment_method:  paymentMethod,
        total_price:     selectedPro.custom_price || service?.base_price || 0,
        slot_id:         selectedSlot?.id || null,
      })
      if (res.data.success) {
        toast.success('Booking created successfully! 🎉')
        navigate('/customer/bookings')
      } else {
        toast.error(res.data.message || 'Booking failed')
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Booking failed')
    } finally {
      setBooking(false)
    }
  }

  return (
    <DashboardLayout>
      <button onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-surface-500 hover:text-primary-600 mb-6 transition-colors text-sm font-medium">
        <ArrowLeft size={16} /> Back to Services
      </button>

      {!service && !loading && (
        <EmptyState icon={IndianRupee} title="Service not found" description="This service may have been removed." />
      )}

      {service && (
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left — Service info + Professionals */}
          <div className="lg:col-span-2 space-y-6">
            {/* Service Card */}
            <div className="bg-white dark:bg-surface-800 rounded-2xl border border-surface-100 dark:border-surface-700 shadow-card p-6">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 rounded-2xl bg-primary-50 dark:bg-primary-950 flex items-center justify-center text-4xl flex-shrink-0">🛠️</div>
                <div className="flex-1">
                  <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-100 mb-1">{service.name}</h1>
                  <p className="text-surface-500 text-sm mb-4">{service.description}</p>
                  <div className="flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center gap-1.5 text-surface-600 dark:text-surface-400">
                      <IndianRupee size={15} className="text-accent-500" />
                      <span className="font-semibold">₹{service.base_price}</span>
                      <span className="text-surface-400">base price</span>
                    </div>
                    {service.estimated_time && (
                      <div className="flex items-center gap-1.5 text-surface-600 dark:text-surface-400">
                        <Clock size={15} className="text-primary-400" />
                        <span>{service.estimated_time}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Professionals */}
            <div>
              <h2 className="text-lg font-bold text-surface-900 dark:text-surface-100 mb-4 flex items-center gap-2">
                <User size={18} className="text-primary-500" /> Available Professionals
              </h2>
              {loading ? <SpinnerOverlay text="Loading professionals..." /> :
               professionals.length === 0 ? (
                <EmptyState icon={User} title="No professionals available" description="There are no professionals for this service yet." />
               ) : (
                <div className="grid sm:grid-cols-2 gap-4">
                  {professionals.map(p => (
                    <ProfessionalCard
                      key={p.id || p.professional_id}
                      professional={p}
                      selected={selectedPro?.id === p.id}
                      onSelect={setSelectedPro}
                    />
                  ))}
                </div>
               )
              }
            </div>

            {/* Slots */}
            {selectedPro && (
              <div>
                <h2 className="text-lg font-bold text-surface-900 dark:text-surface-100 mb-4 flex items-center gap-2">
                  <Calendar size={18} className="text-primary-500" /> Available Slots
                </h2>
                {slots.length === 0 ? (
                  <p className="text-sm text-surface-400">No scheduled slots. Booking will be instant.</p>
                ) : (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {slots.map(slot => (
                      <button
                        key={slot.id}
                        onClick={() => setSelectedSlot(s => s?.id === slot.id ? null : slot)}
                        className={`p-3 rounded-xl border-2 text-sm transition-colors text-left ${
                          selectedSlot?.id === slot.id
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300'
                            : 'border-surface-200 dark:border-surface-600 hover:border-primary-300'
                        }`}
                      >
                        <div className="font-semibold">{slot.slot_date}</div>
                        <div className="text-xs text-surface-500">{slot.start_time} – {slot.end_time}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right — Booking Summary */}
          <div>
            <div className="bg-white dark:bg-surface-800 rounded-2xl border border-surface-100 dark:border-surface-700 shadow-card p-6 sticky top-24">
              <h3 className="text-lg font-bold text-surface-900 dark:text-surface-100 mb-5">Booking Summary</h3>

              <div className="space-y-3 text-sm mb-5">
                <div className="flex justify-between">
                  <span className="text-surface-500">Service</span>
                  <span className="font-medium">{service.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-surface-500">Professional</span>
                  <span className="font-medium">{selectedPro?.name || '—'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-surface-500">Slot</span>
                  <span className="font-medium">{selectedSlot ? `${selectedSlot.slot_date}` : 'Instant'}</span>
                </div>
                <div className="flex justify-between font-bold text-base border-t pt-3 border-surface-100 dark:border-surface-700">
                  <span>Total</span>
                  <span className="text-primary-600">₹{selectedPro?.custom_price || service.base_price}</span>
                </div>
              </div>

              {/* Payment method */}
              <label className="form-label">Payment Method</label>
              <select
                value={paymentMethod}
                onChange={e => setPayMethod(e.target.value)}
                className="input-field mb-5"
              >
                <option value="cash">Cash on Service</option>
                <option value="upi">UPI (Online)</option>
              </select>

              <Button fullWidth onClick={handleBook} loading={booking} size="lg"
                disabled={!selectedPro}>
                Confirm Booking
              </Button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  )
}
