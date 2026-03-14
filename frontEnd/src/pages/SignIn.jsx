import { useState } from 'react'
import { Link } from 'react-router-dom'
import InputField from '../components/InputField'
import Button from '../components/Button'

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

export default function SignIn() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  function validate() {
    const errs = {}
    if (!email.trim()) errs.email = 'Email address is required.'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      errs.email = 'Please enter a valid email address.'
    if (!password) errs.password = 'Password is required.'
    return errs
  }

  function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setErrors({})
    setLoading(true)
    // Simulate sign-in (replace with real API call)
    setTimeout(() => setLoading(false), 1500)
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-6 lg:p-10" style={{ background: '#efefee' }}>
      {/* Blobs */}
      <div aria-hidden="true" className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[36rem] h-[36rem] rounded-full opacity-25" style={{ background: '#c2d1e7', filter: 'blur(100px)' }} />
        <div className="absolute -bottom-40 -right-40 w-[36rem] h-[36rem] rounded-full opacity-25" style={{ background: '#1d348a', filter: 'blur(100px)' }} />
      </div>

      {/* Wide card */}
      <div className="relative w-full max-w-5xl">
        <div
          className="bg-white rounded-3xl overflow-hidden shadow-2xl flex flex-col lg:flex-row"
          style={{ boxShadow: '0 24px 80px rgba(29,52,138,0.13)' }}
        >
          {/* ── Left: branding panel ── */}
          <div
            className="flex flex-col justify-between p-10 lg:p-14 lg:w-5/12"
            style={{ background: 'linear-gradient(160deg, #1d348a 0%, #162870 55%, #0f1e56 100%)' }}
          >
            {/* Logo */}
            <div>
              <div className="flex items-center gap-3 mb-12">
                <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-white/15">
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                  </svg>
                </div>
                <span className="text-white font-bold text-2xl tracking-tight">DysLearn</span>
              </div>

              <h2 className="text-white font-extrabold mb-4 leading-tight" style={{ fontSize: 'clamp(1.6rem, 2.5vw, 2.2rem)' }}>
                Welcome back to your learning journey
              </h2>
              <p className="text-blue-200 leading-relaxed mb-10" style={{ fontSize: '1.05rem', lineHeight: 1.75 }}>
                AI-Powered Adaptive Learning for Dyslexia — personalised support that grows with you.
              </p>

              {/* Feature list */}
              <ul className="flex flex-col gap-5">
                {[
                  { icon: '🕐', text: 'Learn at your own pace with adaptive content' },
                  { icon: '🧠', text: 'Phonological and visual support built in' },
                  { icon: '⭐', text: 'Profile personalised to your learning style' },
                ].map(({ icon, text }) => (
                  <li key={text} className="flex items-center gap-3">
                    <span className="text-2xl">{icon}</span>
                    <span className="text-blue-100" style={{ fontSize: '1rem' }}>{text}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Testimonial */}
            <div className="mt-12 p-5 rounded-2xl" style={{ background: 'rgba(255,255,255,0.09)' }}>
              <p className="text-blue-100 italic leading-relaxed mb-3" style={{ fontSize: '0.95rem' }}>
                "DysLearn helped me feel confident reading again — the personalised support makes every lesson feel manageable."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm" style={{ background: '#c2d1e7', color: '#1d348a' }}>S</div>
                <div>
                  <p className="text-white font-semibold text-sm">Sarah M.</p>
                  <p className="text-blue-300 text-xs">Year 9 Student</p>
                </div>
              </div>
            </div>
          </div>

          {/* ── Right: form ── */}
          <div className="flex flex-col justify-center p-10 lg:p-14 lg:w-7/12">
            <h1 className="font-extrabold mb-3" style={{ color: '#1d1f2e', fontSize: 'clamp(2rem, 3vw, 2.75rem)', lineHeight: 1.2 }}>
              Welcome Back 👋
            </h1>
            <p className="text-gray-500 mb-10" style={{ fontSize: '1.1rem', lineHeight: 1.7 }}>
              Sign in to continue your personalised learning experience.
            </p>

            <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-7">
              <InputField
                id="email"
                label="Email Address"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                error={errors.email}
                autoComplete="email"
              />
              <InputField
                id="password"
                label="Password"
                type={showPw ? 'text' : 'password'}
                placeholder="Enter your password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                error={errors.password}
                autoComplete="current-password"
                rightElement={
                  <button type="button" aria-label={showPw ? 'Hide password' : 'Show password'}
                    onClick={() => setShowPw(v => !v)} className="text-gray-400 hover:text-[#1d348a] p-1 rounded-lg">
                    {showPw ? <EyeClosed /> : <EyeOpen />}
                  </button>
                }
              />

              {errors.form && (
                <div role="alert" className="flex items-center gap-2 px-5 py-4 rounded-xl text-base font-medium"
                  style={{ background: '#FEF2F2', color: '#EF4444', border: '1px solid #FCA5A5' }}>
                  <span aria-hidden="true">⚠</span>{errors.form}
                </div>
              )}

              <Button type="submit" fullWidth disabled={loading} className="py-4 text-lg">
                {loading ? (
                  <>
                    <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Signing in…
                  </>
                ) : 'Sign In'}
              </Button>
            </form>

            <p className="text-center mt-8 text-gray-600" style={{ fontSize: '1.05rem' }}>
              Don't have an account?{' '}
              <Link to="/signup" className="font-semibold hover:underline underline-offset-2" style={{ color: '#1d348a' }}>
                Sign Up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
