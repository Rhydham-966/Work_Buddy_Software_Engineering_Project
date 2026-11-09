import { useState, useEffect } from 'react'
import { User, MapPin, Briefcase, Radio } from 'lucide-react'
import DashboardLayout from '../../layouts/DashboardLayout'
import { Card, CardBody } from '../../components/ui/Card'
import { Button }         from '../../components/ui/Button'
import { SpinnerOverlay } from '../../components/ui/Spinner'
import { Badge }          from '../../components/ui/Badge'
import { useAuth }        from '../../context/AuthContext'
import { getProfile, createProfile } from '../../services/professionalService'
import toast from 'react-hot-toast'

export default function ProfessionalProfilePage() {
  const { user }         = useAuth()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ experience: '', area: '', work_radius: '' })

  useEffect(() => {
    getProfile()
      .then(r => setProfile(r.data.profile))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!form.experience || !form.area || !form.work_radius) {
      toast.error('All fields are required')
      return
    }
    setCreating(true)
    try {
      const res = await createProfile(parseInt(form.experience), form.area, parseInt(form.work_radius))
      if (res.data.success) {
        toast.success('Profile created! Awaiting admin approval.')
        setShowForm(false)
        const pRes = await getProfile()
        setProfile(pRes.data.profile)
      } else {
        toast.error(res.data.message)
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create profile')
    } finally {
      setCreating(false)
    }
  }

  const userFields = [
    { label: 'Name',  value: user?.name,  icon: User },
    { label: 'Email', value: user?.email, icon: User },
    { label: 'Phone', value: user?.phone, icon: User },
  ]

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="page-title mb-1">My Profile</h1>
        <p className="text-surface-500 text-sm">Manage your professional details</p>
      </div>

      {loading ? <SpinnerOverlay /> : (
        <div className="max-w-2xl space-y-6">
          {/* User info */}
          <Card hover={false}>
            <CardBody>
              <div className="flex items-center gap-4 mb-6">
                <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white text-3xl font-black">
                  {user?.name?.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-surface-900 dark:text-surface-100">{user?.name}</h2>
                  <p className="text-surface-500 text-sm">{user?.email}</p>
                  <Badge status="active" className="mt-1">Professional</Badge>
                </div>
              </div>
              <div className="space-y-3">
                {userFields.map(({ label, value, icon: Icon }) => (
                  <div key={label} className="flex items-center gap-3 p-3 bg-surface-50 dark:bg-surface-800 rounded-xl">
                    <Icon size={16} className="text-primary-500" />
                    <div>
                      <p className="text-xs text-surface-400">{label}</p>
                      <p className="font-medium text-surface-900 dark:text-surface-100 text-sm">{value}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Professional Profile */}
          {profile ? (
            <Card hover={false}>
              <CardBody>
                <div className="flex items-center justify-between mb-5">
                  <h3 className="font-bold text-surface-900 dark:text-surface-100">Professional Details</h3>
                  <Badge status={profile.is_approved ? 'approved' : 'pending'}>
                    {profile.is_approved ? '✓ Approved' : '⏳ Pending'}
                  </Badge>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Experience',   value: `${profile.experience} years`, icon: Briefcase },
                    { label: 'Service Area', value: profile.area,                  icon: MapPin },
                    { label: 'Work Radius',  value: `${profile.work_radius} km`,   icon: Radio },
                  ].map(({ label, value, icon: Icon }) => (
                    <div key={label} className="p-4 bg-surface-50 dark:bg-surface-800 rounded-xl">
                      <div className="flex items-center gap-2 mb-1">
                        <Icon size={14} className="text-primary-500" />
                        <p className="text-xs text-surface-400 font-medium">{label}</p>
                      </div>
                      <p className="font-semibold text-surface-900 dark:text-surface-100">{value}</p>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          ) : (
            !showForm ? (
              <Card hover={false}>
                <CardBody className="text-center py-8">
                  <div className="text-5xl mb-4">🛠️</div>
                  <h3 className="font-bold text-surface-900 dark:text-surface-100 mb-2">No Professional Profile Yet</h3>
                  <p className="text-surface-500 text-sm mb-6">Create your professional profile to start receiving bookings.</p>
                  <Button onClick={() => setShowForm(true)}>Create Profile</Button>
                </CardBody>
              </Card>
            ) : (
              <Card hover={false}>
                <CardBody>
                  <h3 className="font-bold text-surface-900 dark:text-surface-100 mb-5">Create Professional Profile</h3>
                  <form onSubmit={handleCreate} className="space-y-4">
                    <div>
                      <label className="form-label">Years of Experience</label>
                      <input type="number" min="0" max="50" placeholder="e.g. 5"
                        value={form.experience}
                        onChange={e => setForm(f => ({ ...f, experience: e.target.value }))}
                        className="input-field" />
                    </div>
                    <div>
                      <label className="form-label">Service Area</label>
                      <input type="text" placeholder="e.g. Downtown Mumbai"
                        value={form.area}
                        onChange={e => setForm(f => ({ ...f, area: e.target.value }))}
                        className="input-field" />
                    </div>
                    <div>
                      <label className="form-label">Work Radius (km)</label>
                      <input type="number" min="1" max="100" placeholder="e.g. 10"
                        value={form.work_radius}
                        onChange={e => setForm(f => ({ ...f, work_radius: e.target.value }))}
                        className="input-field" />
                    </div>
                    <div className="flex gap-3">
                      <Button type="button" variant="secondary" className="flex-1" onClick={() => setShowForm(false)}>Cancel</Button>
                      <Button type="submit" className="flex-1" loading={creating}>Create Profile</Button>
                    </div>
                  </form>
                </CardBody>
              </Card>
            )
          )}
        </div>
      )}
    </DashboardLayout>
  )
}
