import { useState, useEffect } from 'react'
import { Plus, Briefcase, IndianRupee, Clock } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { Card }         from '../../components/ui/Card'
import { Button }       from '../../components/ui/Button'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { EmptyState }   from '../../components/ui/EmptyState'
import { Modal }        from '../../components/ui/Modal'
import { getAllServices, addService } from '../../services/adminService'
import toast from 'react-hot-toast'

export default function AdminManageServicesPage() {
  const [services, setServices] = useState([])
  const [loading, setLoading]   = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving]     = useState(false)
  const [form, setForm]         = useState({ name: '', description: '', base_price: '', estimated_time: '' })

  const fetchData = () => {
    setLoading(true)
    getAllServices()
      .then(r => setServices(r.data.services || []))
      .catch(() => toast.error('Failed to load services'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const handleAdd = async (e) => {
    e.preventDefault()
    if (!form.name || !form.base_price) {
      toast.error('Service name and base price are required')
      return
    }
    setSaving(true)
    try {
      const res = await addService(form.name, form.description, parseFloat(form.base_price), form.estimated_time)
      if (res.data.success) {
        toast.success('Service added!')
        setShowModal(false)
        setForm({ name: '', description: '', base_price: '', estimated_time: '' })
        fetchData()
      } else {
        toast.error(res.data.message)
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to add service')
    } finally {
      setSaving(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title mb-1">Manage Services</h1>
          <p className="text-surface-500 text-sm">Add and manage platform services</p>
        </div>
        <Button icon={<Plus size={16} />} onClick={() => setShowModal(true)}>Add Service</Button>
      </div>

      {loading ? <SpinnerOverlay /> :
       services.length === 0 ? (
        <EmptyState icon={Briefcase} title="No services yet"
          description="Add the first service to get started."
          action={<Button icon={<Plus size={16}/>} onClick={() => setShowModal(true)}>Add First Service</Button>} />
       ) : (
        <>
          <p className="text-sm text-surface-500 mb-4">{services.length} service{services.length > 1 ? 's' : ''} on the platform</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {services.map(s => (
              <Card key={s.id} className="p-5">
                <div className="w-12 h-12 rounded-2xl bg-primary-50 dark:bg-primary-950 flex items-center justify-center text-2xl mb-3">🛠️</div>
                <h4 className="font-bold text-surface-900 dark:text-surface-100 mb-1">{s.name}</h4>
                <p className="text-xs text-surface-500 mb-3 line-clamp-2">{s.description || 'Professional home service'}</p>
                <div className="flex flex-wrap gap-3 text-xs text-surface-500">
                  <div className="flex items-center gap-1">
                    <IndianRupee size={12} className="text-accent-500" />
                    <span className="font-semibold text-surface-700 dark:text-surface-300">₹{s.base_price}</span>
                  </div>
                  {s.estimated_time && (
                    <div className="flex items-center gap-1">
                      <Clock size={12} /> {s.estimated_time}
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </>
       )
      }

      <Modal open={showModal} onClose={() => setShowModal(false)} title="Add New Service">
        <form onSubmit={handleAdd} className="space-y-4">
          <div>
            <label className="form-label">Service Name *</label>
            <input type="text" placeholder="e.g. AC Repair"
              value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              className="input-field" />
          </div>
          <div>
            <label className="form-label">Description</label>
            <textarea rows={3} placeholder="Brief description of the service..."
              value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              className="input-field resize-none" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">Base Price (₹) *</label>
              <input type="number" min="0" placeholder="500"
                value={form.base_price} onChange={e => setForm(f => ({ ...f, base_price: e.target.value }))}
                className="input-field" />
            </div>
            <div>
              <label className="form-label">Estimated Time</label>
              <input type="text" placeholder="e.g. 2 hours"
                value={form.estimated_time} onChange={e => setForm(f => ({ ...f, estimated_time: e.target.value }))}
                className="input-field" />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <Button type="button" variant="secondary" className="flex-1" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button type="submit" className="flex-1" loading={saving}>Add Service</Button>
          </div>
        </form>
      </Modal>
    </DashboardLayout>
  )
}
