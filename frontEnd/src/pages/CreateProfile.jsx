import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/Button'

// ---------- Icons for support mode cards ----------
const PhonologicalIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="23" />
    <line x1="8" y1="23" x2="16" y2="23" />
  </svg>
)
const VisualIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
)
const ReadingSpeedIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
    <path d="M12 7h2" />
    <path d="M12 11h4" />
  </svg>
)
const MixedIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
)

const SUPPORT_MODES = [
  {
    id: 'phonological',
    label: 'Phonological Support',
    description: 'Helps with word decoding and pronunciation',
    Icon: PhonologicalIcon,
  },
  {
    id: 'visual',
    label: 'Visual Support',
    description: 'Improves readability with spacing and layout',
    Icon: VisualIcon,
  },
  {
    id: 'reading-speed',
    label: 'Reading Speed Support',
    description: 'Provides slower step-by-step explanations',
    Icon: ReadingSpeedIcon,
  },
  {
    id: 'mixed',
    label: 'Mixed Support',
    description: 'Combines multiple support strategies',
    Icon: MixedIcon,
  },
]

const LEARNING_FORMATS = [
  { id: 'simplified', label: 'Simplified Text', description: 'Content broken into short, easy sentences' },
  { id: 'audio-ready', label: 'Audio-ready Text', description: 'Text optimised for text-to-speech reading' },
  { id: 'visual-summary', label: 'Visual Summary', description: 'Key points shown as diagrams and charts' },
]

// Toggle Switch component
function Toggle({ id, checked, onChange, label }) {
  return (
    <label htmlFor={id} className="flex items-center justify-between cursor-pointer gap-6 p-2">
      <div>
        <span className="font-bold text-gray-800 text-xl">{label}</span>
        <p className="text-lg text-gray-500 mt-1 leading-relaxed">Highlights one sentence at a time</p>
      </div>
      <button
        id={id}
        role="switch"
        type="button"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className="relative inline-flex h-10 w-20 shrink-0 rounded-full transition-colors duration-200 focus:outline-none focus:ring-4 focus:ring-[#c2d1e7] focus:ring-offset-2"
        style={{ background: checked ? '#1d348a' : '#d1d5db' }}
      >
        <span
          className="pointer-events-none inline-block h-8 w-8 rounded-full bg-white shadow-md transform transition-transform duration-200"
          style={{
            transform: checked ? 'translateX(2.6rem)' : 'translateX(0.25rem)',
            marginTop: '0.25rem',
          }}
        />
      </button>
    </label>
  )
}

// Section wrapper
function Section({ title, subtitle, children }) {
  return (
    <div
      className="bg-white rounded-[2.5rem] p-8 sm:p-12 shadow-sm mb-6"
      style={{ boxShadow: '0 8px 30px rgba(29,52,138,0.06)', border: '1px solid #e8eef6' }}
    >
      <h2 className="font-extrabold text-3xl text-[#1d1f2e] mb-3 tracking-tight">
        {title}
      </h2>
      {subtitle && <p className="text-gray-500 text-lg sm:text-xl mb-8 leading-relaxed tracking-wide">{subtitle}</p>}
      {!subtitle && <div className="mb-8" />}
      {children}
    </div>
  )
}

export default function CreateProfile() {
  const navigate = useNavigate()

  const [academicLevel, setAcademicLevel] = useState('')
  const [supportMode, setSupportMode] = useState('')
  const [learningFormat, setLearningFormat] = useState('')
  const [fontSize, setFontSize] = useState(18)
  const [lineSpacing, setLineSpacing] = useState(1.6)
  const [focusMode, setFocusMode] = useState(false)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  function validate() {
    const errs = {}
    if (!academicLevel) errs.academicLevel = 'Please select your academic level.'
    if (!supportMode) errs.supportMode = 'Please select a dyslexia support mode.'
    if (!learningFormat) errs.learningFormat = 'Please select a preferred learning format.'
    return errs
  }

  function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setErrors({})
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      setSuccess(true)
    }, 1500)
  }

  return (
    <main
      className="min-h-screen px-4 py-12"
      style={{ background: '#efefee' }}
    >
      {/* Background blobs */}
      <div aria-hidden="true" className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[32rem] h-[32rem] rounded-full opacity-15" style={{ background: '#c2d1e7', filter: 'blur(100px)' }} />
        <div className="absolute -bottom-40 -right-40 w-[32rem] h-[32rem] rounded-full opacity-15" style={{ background: '#1d348a', filter: 'blur(100px)' }} />
      </div>

      <div className="relative max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div
            className="inline-flex items-center justify-center w-24 h-24 rounded-3xl mb-8 shadow-xl border-4 border-white"
            style={{ background: '#1d348a' }}
          >
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
            </svg>
          </div>
          <h1
            className="font-black mb-6 text-[#1d348a] text-5xl sm:text-6xl tracking-tight"
            style={{ lineHeight: 1.15 }}
          >
            Create Your Profile
          </h1>
          <p className="text-gray-500 text-xl sm:text-2xl max-w-2xl mx-auto leading-relaxed tracking-wide">
            Help us personalise your experience so we can support your learning journey with dyslexia in mind.
          </p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-8" aria-label="Profile setup progress">
          {['Academic', 'Support Mode', 'Format', 'Accessibility'].map((step, i) => (
            <div key={step} className="flex items-center gap-2">
              <div
                className="flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold"
                style={{ background: '#1d348a', color: 'white', fontSize: '0.75rem' }}
              >
                {i + 1}
              </div>
              <span className="text-xs text-gray-500 hidden sm:block">{step}</span>
              {i < 3 && <div className="w-6 h-0.5 bg-[#c2d1e7] hidden sm:block" />}
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-10">
          {/* ─── Section 1: Academic Information ─── */}
          <Section title="📚 Academic Information" subtitle="Tell us your current level of education.">
            <div className="flex flex-col gap-3">
              <label
                htmlFor="academicLevel"
                className="text-xl font-bold text-gray-700 tracking-wide pl-1"
              >
                Academic Level
              </label>
              <div className="relative">
                <select
                  id="academicLevel"
                  value={academicLevel}
                  onChange={e => setAcademicLevel(e.target.value)}
                  aria-invalid={errors.academicLevel ? 'true' : 'false'}
                  className={[
                    'w-full appearance-none px-6 py-5 rounded-3xl border-2 bg-[#f8fafc] text-xl text-gray-800 outline-none cursor-pointer transition-all',
                    'focus:border-[#1d348a] focus:ring-4 focus:ring-[#c2d1e7] focus:bg-white',
                    errors.academicLevel
                      ? 'border-[#EF4444] bg-red-50'
                      : 'border-[#e8eef6] hover:border-[#1d348a]/50 hover:bg-white',
                  ].join(' ')}
                >
                  <option value="" disabled>Select your level…</option>
                  <option value="elementary">Elementary School</option>
                  <option value="middle">Middle School</option>
                  <option value="high">High School</option>
                  <option value="university">University</option>
                </select>
                {/* Custom dropdown arrow */}
                <div className="pointer-events-none absolute right-6 top-1/2 -translate-y-1/2 text-gray-400">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </div>
              </div>
              {errors.academicLevel && (
                <p role="alert" className="text-lg flex items-center gap-2 mt-2 font-medium" style={{ color: '#EF4444' }}>
                  <span aria-hidden="true">⚠</span>{errors.academicLevel}
                </p>
              )}
            </div>
          </Section>

          {/* ─── Section 2: Dyslexia Support Mode ─── */}
          <Section
            title="🧠 Dyslexia Support Mode"
            subtitle="Choose the support strategy that works best for you."
          >
            {errors.supportMode && (
              <p role="alert" className="text-lg flex items-center gap-2 mb-4 font-medium" style={{ color: '#EF4444' }}>
                <span aria-hidden="true">⚠</span>{errors.supportMode}
              </p>
            )}
            <div
              role="radiogroup"
              aria-label="Dyslexia support mode"
              className="grid grid-cols-1 sm:grid-cols-2 gap-6"
            >
              {SUPPORT_MODES.map(({ id, label, description, Icon }) => {
                const selected = supportMode === id
                return (
                  <button
                    key={id}
                    type="button"
                    role="radio"
                    aria-checked={selected}
                    onClick={() => setSupportMode(id)}
                    className={[
                      'text-left p-8 rounded-3xl border-[3px] transition-all duration-300 transform cursor-pointer focus:outline-none focus:ring-4',
                      selected
                        ? 'border-[#1d348a] bg-[#eef1f9] focus:ring-[#c2d1e7] scale-[1.02]'
                        : 'border-[#e8eef6] bg-[#f8fafc] hover:border-[#1d348a]/40 hover:bg-white focus:ring-[#c2d1e7] hover:scale-[1.01]',
                    ].join(' ')}
                    style={{ boxShadow: selected ? '0 12px 30px rgba(29,52,138,0.1)' : undefined }}
                  >
                    <div
                      className="flex items-center justify-center w-20 h-20 rounded-2xl mb-6 shadow-sm"
                      style={{
                        background: selected ? '#1d348a' : 'white',
                        color: selected ? 'white' : '#1d348a',
                        border: selected ? 'none' : '2px solid #e8eef6',
                      }}
                    >
                      <Icon />
                    </div>
                    <p className="font-bold text-gray-800 mb-2 text-xl">{label}</p>
                    <p className="text-lg text-gray-500 leading-relaxed">{description}</p>
                    {selected && (
                      <div className="mt-6 flex items-center gap-2 text-sm font-black tracking-widest uppercase" style={{ color: '#1d348a' }}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                        Selected Focus
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
          </Section>

          {/* ─── Section 3: Preferred Learning Format ─── */}
          <Section title="🎯 Preferred Learning Format" subtitle="How would you like content to be delivered?">
            {errors.learningFormat && (
              <p role="alert" className="text-lg flex items-center gap-2 mb-4 font-medium" style={{ color: '#EF4444' }}>
                <span aria-hidden="true">⚠</span>{errors.learningFormat}
              </p>
            )}
            <fieldset className="flex flex-col gap-4">
              <legend className="sr-only">Preferred learning format</legend>
              {LEARNING_FORMATS.map(({ id, label, description }) => {
                const selected = learningFormat === id
                return (
                  <label
                    key={id}
                    htmlFor={`format-${id}`}
                    className={[
                      'flex items-center gap-6 p-6 rounded-3xl border-2 cursor-pointer transition-all duration-300',
                      selected
                        ? 'border-[#1d348a] bg-[#eef1f9] shadow-md scale-[1.01]'
                        : 'border-[#e8eef6] bg-[#f8fafc] hover:border-[#1d348a]/40 hover:bg-white',
                    ].join(' ')}
                  >
                    <div className="flex items-center justify-center shrink-0">
                      <input
                        id={`format-${id}`}
                        type="radio"
                        name="learningFormat"
                        value={id}
                        checked={selected}
                        onChange={() => setLearningFormat(id)}
                        className="sr-only"
                      />
                      {/* Custom radio button */}
                      <div
                        className="w-8 h-8 rounded-full border-[3px] flex items-center justify-center transition-all duration-300"
                        style={{
                          borderColor: selected ? '#1d348a' : '#c2d1e7',
                          background: selected ? '#1d348a' : 'white',
                          boxShadow: selected ? '0 0 0 4px rgba(29,52,138,0.1)' : 'none',
                        }}
                      >
                        {selected && (
                          <div className="w-3 h-3 rounded-full bg-white" />
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="font-bold text-gray-800 text-xl">{label}</p>
                      <p className="text-lg text-gray-500 mt-1 leading-relaxed">{description}</p>
                    </div>
                  </label>
                )
              })}
            </fieldset>
          </Section>

          {/* ─── Section 4: Accessibility Options ─── */}
          <Section title="⚙️ Accessibility Options" subtitle="Optional: fine-tune the interface for your comfort.">
            <div className="flex flex-col gap-10">
              {/* Font Size */}
              <div className="bg-[#f8fafc] p-8 rounded-3xl border border-[#e8eef6]">
                <div className="flex items-center justify-between mb-4">
                  <label htmlFor="fontSize" className="font-bold text-gray-800 text-xl tracking-wide">
                    Base Font Size
                  </label>
                  <span
                    className="px-4 py-2 rounded-xl text-lg font-black tracking-widest shadow-sm"
                    style={{ background: '#eef1f9', color: '#1d348a' }}
                  >
                    {fontSize}px
                  </span>
                </div>
                <input
                  id="fontSize"
                  type="range"
                  min="16"
                  max="32"
                  value={fontSize}
                  onChange={e => setFontSize(Number(e.target.value))}
                  className="w-full h-3 bg-[#c2d1e7] rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-4 focus:ring-[#1d348a]/30"
                  aria-label={`Font size: ${fontSize} pixels`}
                />
                <div className="flex justify-between text-base text-gray-500 mt-3 font-medium">
                  <span>16px (A)</span>
                  <span className="text-xl">32px (A)</span>
                </div>
              </div>

              {/* Line Spacing */}
              <div className="bg-[#f8fafc] p-8 rounded-3xl border border-[#e8eef6]">
                <div className="flex items-center justify-between mb-4">
                  <label htmlFor="lineSpacing" className="font-bold text-gray-800 text-xl tracking-wide">
                    Line Spacing Density
                  </label>
                  <span
                    className="px-4 py-2 rounded-xl text-lg font-black tracking-widest shadow-sm"
                    style={{ background: '#eef1f9', color: '#1d348a' }}
                  >
                    {lineSpacing.toFixed(1)}×
                  </span>
                </div>
                <input
                  id="lineSpacing"
                  type="range"
                  min="1.4"
                  max="3.0"
                  step="0.1"
                  value={lineSpacing}
                  onChange={e => setLineSpacing(Number(e.target.value))}
                  className="w-full h-3 bg-[#c2d1e7] rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-4 focus:ring-[#1d348a]/30"
                  aria-label={`Line spacing: ${lineSpacing.toFixed(1)} times`}
                />
                <div className="flex justify-between text-base text-gray-500 mt-3 font-medium">
                  <span>Standard gaps</span>
                  <span>Extremely wide gaps</span>
                </div>
              </div>

              {/* Preview card */}
              <div
                className="p-8 rounded-3xl border-[3px] border-[#c2d1e7] bg-white shadow-inner"
                aria-live="polite"
                aria-label="Typography preview"
              >
                <p className="text-base text-gray-400 mb-4 uppercase tracking-widest font-black flex items-center gap-2">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" />
                  </svg>
                  Live Preview
                </p>
                <p
                  className="text-gray-800 font-medium"
                  style={{ fontSize: `${fontSize}px`, lineHeight: lineSpacing }}
                >
                  The quick brown fox jumps over the lazy dog.
                </p>
              </div>

              {/* Focus Reading Mode */}
              <div
                className="p-8 rounded-3xl"
                style={{ background: '#f8fafc', border: '2px solid #e8eef6' }}
              >
                <Toggle
                  id="focusMode"
                  checked={focusMode}
                  onChange={setFocusMode}
                  label="Focus Reading Mode"
                />
              </div>
            </div>
          </Section>

          {/* Success banner */}
          {success && (
            <div
              role="status"
              className="flex items-center gap-4 px-8 py-6 rounded-3xl text-xl font-bold tracking-wide shadow-lg"
              style={{ background: '#ECFDF5', color: '#10B981', border: '2px solid #6EE7B7' }}
            >
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Profile successfully saved!
            </div>
          )}

          {/* Submit */}
          <Button
            type="submit"
            fullWidth
            disabled={loading || success}
            className="py-6 px-10 text-2xl font-bold rounded-[2rem] mt-4 shadow-xl hover:shadow-2xl hover:scale-[1.02] transition-all tracking-wide"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-4">
                <svg className="animate-spin w-8 h-8" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Saving your profile…
              </span>
            ) : success ? (
              '✓ Profile Created! Redirecting...'
            ) : (
              'Save & Create Profile'
            )}
          </Button>

          <p className="text-center text-gray-500 text-lg sm:text-xl pb-10 tracking-wide">
            You can update your profile accessibility settings at any time in your dashboard.
          </p>
        </form>
      </div>
    </main>
  )
}
