import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import InputField from '../components/InputField'
import Button from '../components/Button'
import { signUp } from '../services/api'

const EyeOpen = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
)
const EyeClosed = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
    <line x1="1" y1="1" x2="23" y2="23" />
  </svg>
)

export default function SignUp() {
  const navigate = useNavigate()

  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
  const [showPw, setShowPw] = useState(false)
  const [showCf, setShowCf] = useState(false)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  function set(field) {
    return e => setForm(f => ({ ...f, [field]: e.target.value }))
  }

  function validate() {
    const errs = {}
    if (!form.name.trim()) errs.name = 'Full name is required.'
    if (!form.email.trim()) errs.email = 'Email is required.'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
      errs.email = 'Please enter a valid email address.'
    if (!form.password) errs.password = 'Password is required.'
    else if (form.password.length < 8)
      errs.password = 'Password must be at least 8 characters.'
    if (!form.confirm) errs.confirm = 'Please confirm your password.'
    else if (form.password !== form.confirm)
      errs.confirm = 'Passwords do not match.'
    return errs
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setErrors({})
    setLoading(true)
    try {
      await signUp({ email: form.email, password: form.password, full_name: form.name })
      setSuccess(true)
      setTimeout(() => navigate('/create-profile'), 1200)
    } catch (err) {
      setErrors({ form: err.message || 'Sign up failed. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen w-full flex flex-col lg:flex-row bg-[#efefee] overflow-hidden">
      {/* ── Left: branding panel ── */}
      <div
        className="flex flex-col justify-center p-8 lg:p-14 lg:w-[45%] min-h-screen relative z-20 shadow-2xl"
        style={{ background: 'linear-gradient(160deg, #1d348a 0%, #162870 55%, #0f1e56 100%)' }}
      >
        <div className="max-w-xl mx-auto w-full">
          {/* Logo */}
          <div className="flex items-center gap-4 mb-10">
            <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20 shadow-lg">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
              </svg>
            </div>
            <span className="text-white font-black text-3xl tracking-tight">DysLearn</span>
          </div>

          <h2 className="text-white font-black mb-4 leading-[1.1]" style={{ fontSize: 'clamp(2rem, 3.5vw, 3rem)' }}>
            Join thousands of learners building confidence every day.
          </h2>
          <p className="text-blue-100 mb-8" style={{ fontSize: '1.2rem', lineHeight: 1.6 }}>
            Create your free account and let DysLearn build a personalised reading experience just for you.
          </p>

          {/* Feature list */}
          <ul className="flex flex-col gap-4">
            {[
              { icon: '👥', text: 'Trusted by thousands of dyslexic learners' },
              { icon: '✨', text: 'AI-powered personalisation from day one' },
              { icon: '✅', text: 'Approved by educators and reading specialists' },
            ].map(({ icon, text }) => (
              <li key={text} className="flex items-center gap-4">
                <span className="text-3xl drop-shadow-md">{icon}</span>
                <span className="text-white font-semibold text-lg tracking-wide">{text}</span>
              </li>
            ))}
          </ul>

          {/* Testimonial */}
          <div className="mt-10 p-6 rounded-3xl border border-white/10 backdrop-blur-md" style={{ background: 'rgba(255,255,255,0.06)' }}>
            <p className="text-blue-50 italic mb-4 font-medium leading-relaxed text-lg">
              "DysLearn helped me feel confident reading again — the personalised support makes every lesson feel manageable."
            </p>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full flex items-center justify-center font-black text-xl shadow-inner border border-white/20" style={{ background: '#c2d1e7', color: '#1d348a' }}>S</div>
              <div>
                <p className="text-white font-bold text-lg tracking-wide">Sarah M.</p>
                <p className="text-blue-200 text-base font-medium">Year 9 Student</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Right: full height form container ── */}
      <div className="flex flex-col justify-center items-center p-6 lg:p-12 lg:w-[55%] min-h-screen relative">
        {/* Blobs */}
        <div aria-hidden="true" className="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute top-0 right-0 w-[40rem] h-[40rem] rounded-full opacity-30 translate-x-1/3 -translate-y-1/3" style={{ background: '#c2d1e7', filter: 'blur(100px)' }} />
          <div className="absolute bottom-0 left-0 w-[40rem] h-[40rem] rounded-full opacity-15 translate-y-1/3 -translate-x-1/3" style={{ background: '#1d348a', filter: 'blur(100px)' }} />
        </div>

        <div
          className="w-full max-w-2xl bg-white rounded-[2rem] p-8 lg:p-12 shadow-2xl relative z-10 border border-[#e8eef6]"
          style={{ boxShadow: '0 24px 80px rgba(29,52,138,0.08)' }}
        >
          <h1 className="font-black mb-3 text-[#1d1f2e] tracking-tight" style={{ fontSize: 'clamp(2rem, 3.5vw, 3rem)', lineHeight: 1.1 }}>
            Create Your Account ✨
          </h1>
          <p className="text-gray-500 mb-6 text-lg font-medium tracking-wide">
            Set up your account and start building a learning profile tailored to you.
          </p>

          {success && (
            <div role="status" className="flex items-center gap-3 px-6 py-4 rounded-2xl text-lg font-bold tracking-wide shadow-md mb-6"
              style={{ background: '#ECFDF5', color: '#10B981', border: '2px solid #6EE7B7' }}>
              <span aria-hidden="true" className="text-xl">✓</span> Account created! Redirecting to setup…
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">
            <InputField id="fullname" label="Full Name" type="text" placeholder="Jane Doe"
              value={form.name} onChange={set('name')} error={errors.name} autoComplete="name" />
            <InputField id="email" label="Email Address" type="email" placeholder="you@example.com"
              value={form.email} onChange={set('email')} error={errors.email} autoComplete="email" />

            {/* Password fields side by side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <InputField id="password" label="Password" type={showPw ? 'text' : 'password'}
                placeholder="Min. 8 characters" value={form.password} onChange={set('password')}
                error={errors.password} autoComplete="new-password"
                rightElement={
                  <button type="button" aria-label={showPw ? 'Hide' : 'Show'}
                    onClick={() => setShowPw(v => !v)} className="text-gray-400 hover:text-[#1d348a] p-2 rounded-xl transition-colors hover:bg-[#eef1f9]">
                    {showPw ? <EyeClosed /> : <EyeOpen />}
                  </button>
                }
              />
              <InputField id="confirm" label="Confirm Password" type={showCf ? 'text' : 'password'}
                placeholder="Repeat password" value={form.confirm} onChange={set('confirm')}
                error={errors.confirm} autoComplete="new-password"
                rightElement={
                  <button type="button" aria-label={showCf ? 'Hide' : 'Show'}
                    onClick={() => setShowCf(v => !v)} className="text-gray-400 hover:text-[#1d348a] p-2 rounded-xl transition-colors hover:bg-[#eef1f9]">
                    {showCf ? <EyeClosed /> : <EyeOpen />}
                  </button>
                }
              />
            </div>

            {/* Password strength hint */}
            {form.password.length > 0 && (
              <div className="flex gap-2 items-center mt-1" aria-live="polite">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="h-2 flex-1 rounded-full transition-all duration-300 shadow-inner"
                    style={{ background: form.password.length >= i * 3 ? (i <= 1 ? '#EF4444' : i <= 2 ? '#F59E0B' : '#10B981') : '#e5e7eb' }} />
                ))}
                <span className="text-gray-500 ml-2 font-bold uppercase tracking-widest text-xs">
                  {form.password.length < 4 ? 'Weak' : form.password.length < 7 ? 'Fair' : form.password.length < 10 ? 'Good' : 'Strong'}
                </span>
              </div>
            )}

            {errors.form && (
              <div role="alert" className="flex items-center gap-3 px-5 py-4 rounded-xl text-base font-bold"
                style={{ background: '#FEF2F2', color: '#EF4444', border: '2px solid #FCA5A5' }}>
                <span aria-hidden="true" className="text-xl">⚠</span>{errors.form}
              </div>
            )}

            <Button type="submit" fullWidth disabled={loading || success} className="py-4 px-8 text-xl font-black rounded-[1.5rem] mt-2 shadow-xl hover:shadow-2xl hover:scale-[1.02] transition-all tracking-wide">
              {loading ? (
                <span className="flex items-center justify-center gap-3">
                  <svg className="animate-spin w-6 h-6" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  Creating account…
                </span>
              ) : 'Create Free Account'}
            </Button>
          </form>

          <p className="text-center mt-8 text-gray-500 text-lg font-medium tracking-wide">
            Already have an account?{' '}
            <Link to="/" className="font-extrabold hover:underline underline-offset-4 transition-colors p-2 rounded-lg hover:bg-[#eef1f9]" style={{ color: '#1d348a' }}>
              Sign In Instead
            </Link>
          </p>
        </div>
      </div>
    </main>
  )
}
