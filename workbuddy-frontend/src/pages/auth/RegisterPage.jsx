import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { User, Phone, Mail, Lock, Eye, EyeOff, Check } from 'lucide-react'
import AuthLayout from '../../layouts/AuthLayout'
import { Button }  from '../../components/ui/Button'
import { register as apiRegister, verifyOtp } from '../../services/authService'
import toast from 'react-hot-toast'

const ROLES = [
  { value: 'customer',     label: 'Customer',     desc: 'Book home services', emoji: '🏠' },
  { value: 'professional', label: 'Professional', desc: 'Offer your skills',   emoji: '🛠️' },
]

const STEPS = ['Details', 'Role', 'Verify OTP']

export default function RegisterPage() {
  const navigate = useNavigate()
  const [step, setStep]     = useState(0)
  const [loading, setLoading] = useState(false)
  const [showPwd, setShowPwd] = useState(false)
  const [userId, setUserId]   = useState(null)
  const [otp, setOtp]         = useState('')

  const [form, setForm] = useState({
    name: '', email: '', phone: '', password: '', role: '',
  })

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }))

  const handleDetailsNext = (e) => {
    e.preventDefault()
    if (!form.name || !form.email || !form.phone || !form.password) {
      toast.error('Please fill in all fields')
      return
    }
    setStep(1)
  }

  const handleRoleNext = () => {
    if (!form.role) { toast.error('Please select a role'); return }
    setStep(2)
    handleRegister()
  }

  const handleRegister = async () => {
    setLoading(true)
    try {
      const res = await apiRegister(form.name, form.email, form.phone, form.password, form.role)
      if (res.data.success) {
        setUserId(res.data.user_id)
        toast.success('OTP sent! Check the console (dev mode).')
        if (res.data.otp) {
           toast(`[Demo Mode] Your OTP is: ${res.data.otp}`, { icon: '🔑', duration: 10000 });
        }
      } else {
        toast.error(res.data.message || 'Registration failed')
        setStep(1)
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Registration failed')
      setStep(1)
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOtp = async (e) => {
    e.preventDefault()
    if (!otp) { toast.error('Please enter the OTP'); return }
    setLoading(true)
    try {
      const res = await verifyOtp(userId, otp)
      if (res.data.success) {
        toast.success('Account verified! You can now log in. 🎉')
        navigate('/login')
      } else {
        toast.error(res.data.message || 'Invalid OTP')
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Invalid OTP')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout>
      <div className="px-8 py-8">
        {/* Stepper */}
        <div className="flex items-center gap-0 mb-8">
          {STEPS.map((s, i) => (
            <div key={s} className="flex items-center flex-1">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors ${
                i < step  ? 'bg-primary-600 border-primary-600 text-white' :
                i === step ? 'border-primary-600 text-primary-600 bg-white dark:bg-surface-900' :
                             'border-surface-300 text-surface-400 bg-white dark:bg-surface-900'
              }`}>
                {i < step ? <Check size={12}/> : i + 1}
              </div>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-0.5 mx-1 transition-colors ${i < step ? 'bg-primary-500' : 'bg-surface-200'}`} />
              )}
            </div>
          ))}
        </div>

        {/* Step 0 — Details */}
        {step === 0 && (
          <form onSubmit={handleDetailsNext} className="space-y-4 animate-slide-up">
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-100 mb-1">Create account</h1>
            <p className="text-surface-500 text-sm mb-5">Join WorkBuddy today</p>

            {[
              { key: 'name',     label: 'Full Name',    icon: User,  type: 'text',     ph: 'John Doe' },
              { key: 'email',    label: 'Email',         icon: Mail,  type: 'email',    ph: 'john@email.com' },
              { key: 'phone',    label: 'Phone / Username', icon: Phone, type: 'text', ph: 'e.g. cust1' },
            ].map(({ key, label, icon: Icon, type, ph }) => (
              <div key={key}>
                <label className="form-label">{label}</label>
                <div className="relative">
                  <Icon size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
                  <input
                    id={`reg-${key}`}
                    type={type}
                    value={form[key]}
                    onChange={e => set(key, e.target.value)}
                    placeholder={ph}
                    className="input-field pl-10"
                  />
                </div>
              </div>
            ))}

            <div>
              <label className="form-label">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
                <input
                  id="reg-password"
                  type={showPwd ? 'text' : 'password'}
                  value={form.password}
                  onChange={e => set('password', e.target.value)}
                  placeholder="Create password"
                  className="input-field pl-10 pr-10"
                />
                <button type="button" onClick={() => setShowPwd(s => !s)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600 transition-colors">
                  {showPwd ? <EyeOff size={16}/> : <Eye size={16}/>}
                </button>
              </div>
            </div>

            <Button type="submit" fullWidth size="lg">Continue</Button>
            <p className="text-sm text-center text-surface-500">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-600 font-semibold hover:underline">Sign in</Link>
            </p>
          </form>
        )}

        {/* Step 1 — Role */}
        {step === 1 && (
          <div className="animate-slide-up">
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100 mb-1">Choose your role</h2>
            <p className="text-surface-500 text-sm mb-6">How will you use WorkBuddy?</p>

            <div className="space-y-3 mb-6">
              {ROLES.map(r => (
                <label key={r.value}
                  className={`flex items-start gap-4 p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                    form.role === r.value
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-950'
                      : 'border-surface-200 dark:border-surface-700 hover:border-primary-300'
                  }`}
                >
                  <input type="radio" className="hidden" value={r.value} checked={form.role === r.value}
                    onChange={() => set('role', r.value)} />
                  <span className="text-3xl">{r.emoji}</span>
                  <div className="flex-1">
                    <div className="font-semibold text-surface-900 dark:text-surface-100">{r.label}</div>
                    <div className="text-sm text-surface-500">{r.desc}</div>
                  </div>
                  {form.role === r.value && (
                    <div className="w-6 h-6 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                      <Check size={14} className="text-white" />
                    </div>
                  )}
                </label>
              ))}
            </div>

            <div className="flex gap-3">
              <Button variant="secondary" onClick={() => setStep(0)} size="lg" className="flex-1">Back</Button>
              <Button onClick={handleRoleNext} loading={loading} size="lg" className="flex-1">Register</Button>
            </div>
          </div>
        )}

        {/* Step 2 — OTP */}
        {step === 2 && (
          <form onSubmit={handleVerifyOtp} className="animate-slide-up">
            <div className="text-center mb-6">
              <div className="w-16 h-16 rounded-3xl bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-3xl mx-auto mb-4">📲</div>
              <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100 mb-1">Verify your account</h2>
              <p className="text-surface-500 text-sm">Enter the OTP sent to your phone</p>
            </div>

            <input
              id="otp"
              type="text"
              maxLength={6}
              value={otp}
              onChange={e => setOtp(e.target.value)}
              placeholder="Enter 6-digit OTP"
              className="input-field text-center text-lg tracking-[0.5em] font-bold mb-6"
            />

            <Button type="submit" fullWidth loading={loading} size="lg">Verify &amp; Continue</Button>
          </form>
        )}
      </div>
    </AuthLayout>
  )
}
