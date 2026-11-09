import { useState, useEffect } from 'react'
import { Plus, Clock, Calendar } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { Card }         from '../../components/ui/Card'
import { Button }       from '../../components/ui/Button'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { EmptyState }   from '../../components/ui/EmptyState'
import { Modal }        from '../../components/ui/Modal'
import { Badge }        from '../../components/ui/Badge'
import { getProfile, getMySlots, addSlot } from '../../services/professionalService'
import toast from 'react-hot-toast'

export default function ManageSlotsPage() {
  const [profile, setProfile] = useState(null)
  const [slots, setSlots]     = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving]   = useState(false)
  const [form, setForm]       = useState({ slot_date: '', start_time: '', end_time: '' })

  const fetchData = () => {
    setLoading(true)
    Promise.all([getProfile(), getMySlots()])
      .then(([pRes, sRes]) => {
        setProfile(pRes.data.profile)
        setSlots(sRes.data.slots || [])
      })
      .catch(() => toast.error('Failed to load slots'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const handleAdd = async (e) => {
    e.preventDefault()
    if (!form.slot_date || !form.start_time || !form.end_time) {
      toast.error('All time fields are required')
      return
    }
    setSaving(true)
    try {
      const res = await addSlot(form.slot_date, form.start_time, form.end_time)
      if (res.data.success) {
        toast.success('Slot added!')
        setShowModal(false)
        setForm({ slot_date: '', start_time: '', end_time: '' })
        fetchData()
      } else {
        toast.error(res.data.message)
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to add slot')
    } finally {
      setSaving(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title mb-1">My Time Slots</h1>
          <p className="text-surface-500 text-sm">Manage your availability for bookings</p>
        </div>
        {profile?.is_approved && (
          <Button icon={<Plus size={16}/>} onClick={() => setShowModal(true)}>Add Slot</Button>
        )}
      </div>

      {profile && !profile.is_approved && (
        <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-xl text-amber-700 dark:text-amber-400 text-sm">
          Your profile must be approved by an admin before you can add time slots.
        </div>
      )}

      {loading ? <SpinnerOverlay /> :
       slots.length === 0 ? (
        <EmptyState icon={Clock} title="No slots added"
          description="Add your availability slots so customers can book you on specific times."
          action={profile?.is_approved && (
            <Button icon={<Plus size={16}/>} onClick={() => setShowModal(true)}>Add First Slot</Button>
          )} />
       ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {slots.map(slot => (
            <Card key={slot.id} className="p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-xl bg-primary-50 dark:bg-primary-950 flex items-center justify-center">
                  <Calendar size={18} className="text-primary-600 dark:text-primary-400" />
                </div>
                <div>
                  <p className="font-semibold text-surface-900 dark:text-surface-100">{slot.slot_date}</p>
                  <p className="text-xs text-surface-500">{slot.start_time} – {slot.end_time}</p>
                </div>
              </div>
              <Badge status={slot.is_booked ? 'accepted' : 'active'}>
                {slot.is_booked ? 'Booked' : 'Available'}
              </Badge>
            </Card>
          ))}
        </div>
       )
      }

      <Modal open={showModal} onClose={() => setShowModal(false)} title="Add Time Slot">
        <form onSubmit={handleAdd} className="space-y-4">
          <div>
            <label className="form-label">Date</label>
            <input type="date" value={form.slot_date}
              min={new Date().toISOString().split('T')[0]}
              onChange={e => setForm(f => ({ ...f, slot_date: e.target.value }))}
              className="input-field" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">Start Time</label>
              <input type="time" value={form.start_time}
                onChange={e => setForm(f => ({ ...f, start_time: e.target.value }))}
                className="input-field" />
            </div>
            <div>
              <label className="form-label">End Time</label>
              <input type="time" value={form.end_time}
                onChange={e => setForm(f => ({ ...f, end_time: e.target.value }))}
                className="input-field" />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <Button type="button" variant="secondary" className="flex-1" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button type="submit" className="flex-1" loading={saving}>Add Slot</Button>
          </div>
        </form>
      </Modal>
    </DashboardLayout>
  )
}
