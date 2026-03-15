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
            Welcome back to your learning journey.
          </h2>
          <p className="text-blue-100 mb-8" style={{ fontSize: '1.2rem', lineHeight: 1.6 }}>
            AI-Powered Adaptive Learning for Dyslexia — personalised support that rigorously expands to your specific needs.
          </p>

          {/* Feature list */}
          <ul className="flex flex-col gap-4">
            {[
              { icon: '🕐', text: 'Learn at your own pace with adaptive content' },
              { icon: '🧠', text: 'Phonological and visual support natively built in' },
              { icon: '⭐', text: 'Profile completely tailored to your cognitive style' },
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
              "DysLearn completely transformed my reading confidence. The deeply personalised visual support makes studying actually enjoyable rather than a chore."
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
          className="w-full max-w-xl bg-white rounded-[2rem] p-8 lg:p-12 shadow-2xl relative z-10 border border-[#e8eef6]"
          style={{ boxShadow: '0 24px 80px rgba(29,52,138,0.08)' }}
        >
          <h1 className="font-black mb-3 text-[#1d1f2e] tracking-tight" style={{ fontSize: 'clamp(2rem, 3.5vw, 3rem)', lineHeight: 1.1 }}>
            Sign In 👋
          </h1>
          <p className="text-gray-500 mb-8 text-lg font-medium tracking-wide">
            Securely sign in to continue your personalised workspace.
          </p>

          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-6">
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
                  onClick={() => setShowPw(v => !v)} className="text-gray-400 hover:text-[#1d348a] p-2 rounded-xl transition-colors hover:bg-[#eef1f9]">
                  {showPw ? <EyeClosed /> : <EyeOpen />}
                </button>
              }
            />

            {errors.form && (
              <div role="alert" className="flex items-center gap-3 px-5 py-4 rounded-xl text-base font-bold"
                style={{ background: '#FEF2F2', color: '#EF4444', border: '2px solid #FCA5A5' }}>
                <span aria-hidden="true" className="text-xl">⚠</span>{errors.form}
              </div>
            )}

            <Button type="submit" fullWidth disabled={loading} className="py-4 px-8 text-xl font-black rounded-[1.5rem] mt-2 shadow-xl hover:shadow-2xl hover:scale-[1.02] transition-all tracking-wide">
              {loading ? (
                <span className="flex items-center justify-center gap-3">
                  <svg className="animate-spin w-6 h-6" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  Signing in…
                </span>
              ) : 'Sign In'}
            </Button>
          </form>

          <p className="text-center mt-8 text-gray-500 text-lg font-medium tracking-wide">
            Don't have an account?{' '}
            <Link to="/signup" className="font-extrabold hover:underline underline-offset-4 transition-colors p-2 rounded-lg hover:bg-[#eef1f9]" style={{ color: '#1d348a' }}>
              Sign Up For Free
            </Link>
          </p>
        </div>
      </div>
    </main>
  )
}
