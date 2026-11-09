import { useState, useEffect } from 'react'
import { Plus, Wrench, IndianRupee } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { Card, CardBody } from '../../components/ui/Card'
import { Button }         from '../../components/ui/Button'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { EmptyState }     from '../../components/ui/EmptyState'
import { Modal }          from '../../components/ui/Modal'
import { getProfile, addServicePricing, getAvailableServices } from '../../services/professionalService'
import toast from 'react-hot-toast'

export default function ManageServicesPage() {
  const [profile, setProfile]       = useState(null)
  const [myServices, setMyServices] = useState([])
  const [available, setAvailable]   = useState([])
  const [loading, setLoading]       = useState(true)
  const [showModal, setShowModal]   = useState(false)
  const [form, setForm]             = useState({ service_id: '', custom_price: '' })
  const [saving, setSaving]         = useState(false)

  const fetchData = () => {
    setLoading(true)
    Promise.all([getProfile(), getAvailableServices()])
      .then(([pRes, sRes]) => {
        setProfile(pRes.data.profile)
        setMyServices(pRes.data.services || [])
        setAvailable(sRes.data.services  || [])
      })
      .catch(() => toast.error('Failed to load data'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const handleAdd = async (e) => {
    e.preventDefault()
    if (!form.service_id || !form.custom_price) {
      toast.error('Please select a service and enter your price')
      return
    }
    setSaving(true)
    try {
      const res = await addServicePricing(parseInt(form.service_id), parseFloat(form.custom_price))
      if (res.data.success) {
        toast.success('Service added!')
        setShowModal(false)
        setForm({ service_id: '', custom_price: '' })
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
          <h1 className="page-title mb-1">My Services</h1>
          <p className="text-surface-500 text-sm">Services you offer with your custom pricing</p>
        </div>
        {profile && (
          <Button icon={<Plus size={16} />} onClick={() => setShowModal(true)}>
            Add Service
          </Button>
        )}
      </div>

      {!profile && !loading && (
        <div className="p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-xl text-amber-700 dark:text-amber-400 text-sm mb-6">
          You need to create a professional profile first before adding services.
        </div>
      )}

      {loading ? <SpinnerOverlay /> :
       myServices.length === 0 ? (
        <EmptyState icon={Wrench} title="No services added yet"
          description="Add services you offer so customers can book you."
          action={profile && <Button icon={<Plus size={16} />} onClick={() => setShowModal(true)}>Add First Service</Button>} />
       ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {myServices.map(s => (
            <Card key={s.id} className="p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-11 h-11 rounded-xl bg-primary-50 dark:bg-primary-950 flex items-center justify-center text-2xl">🛠️</div>
                <div>
                  <h4 className="font-semibold text-surface-900 dark:text-surface-100">{s.service_name || s.name}</h4>
                </div>
              </div>
              <div className="flex items-center gap-1.5 text-sm">
                <IndianRupee size={14} className="text-accent-500" />
                <span className="font-bold text-surface-800 dark:text-surface-200">₹{s.custom_price}</span>
                <span className="text-surface-400 text-xs">your rate</span>
              </div>
            </Card>
          ))}
        </div>
       )
      }

      {/* Add Service Modal */}
      <Modal open={showModal} onClose={() => setShowModal(false)} title="Add a Service">
        <form onSubmit={handleAdd} className="space-y-4">
          <div>
            <label className="form-label">Service</label>
            <select value={form.service_id} onChange={e => setForm(f => ({ ...f, service_id: e.target.value }))}
              className="input-field">
              <option value="">Select a service...</option>
              {available.map(s => (
                <option key={s.id} value={s.id}>{s.name} (base: ₹{s.base_price})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="form-label">Your Custom Price (₹)</label>
            <input type="number" min="0" placeholder="e.g. 600"
              value={form.custom_price}
              onChange={e => setForm(f => ({ ...f, custom_price: e.target.value }))}
              className="input-field" />
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
