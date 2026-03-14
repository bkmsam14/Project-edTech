import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/Button'

// ---------- Icons for support mode cards ----------
const PhonologicalIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="23" />
    <line x1="8" y1="23" x2="16" y2="23" />
  </svg>
)
const VisualIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
)
const ReadingSpeedIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
    <path d="M12 7h2" />
    <path d="M12 11h4" />
  </svg>
)
const MixedIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
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
    <label htmlFor={id} className="flex items-center justify-between cursor-pointer gap-4">
      <div>
        <span className="font-semibold text-gray-800" style={{ fontSize: '1rem' }}>{label}</span>
        <p className="text-sm text-gray-500 mt-0.5">Highlights one sentence at a time</p>
      </div>
      <button
        id={id}
        role="switch"
        type="button"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className="relative inline-flex h-7 w-14 shrink-0 rounded-full transition-colors duration-200 focus:outline-none focus:ring-3 focus:ring-[#c2d1e7] focus:ring-offset-2"
        style={{ background: checked ? '#1d348a' : '#d1d5db' }}
      >
        <span
          className="pointer-events-none inline-block h-6 w-6 rounded-full bg-white shadow-md transform transition-transform duration-200"
          style={{
            transform: checked ? 'translateX(1.75rem)' : 'translateX(0.125rem)',
            marginTop: '0.125rem',
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
      className="bg-white rounded-2xl p-6 sm:p-8 shadow-sm"
      style={{ boxShadow: '0 4px 24px rgba(29,52,138,0.07)', border: '1px solid #e8eef6' }}
    >
      <h2 className="font-bold text-gray-800 mb-1" style={{ fontSize: '1.2rem', color: '#1d1f2e' }}>
        {title}
      </h2>
      {subtitle && <p className="text-gray-500 text-sm mb-5">{subtitle}</p>}
      {!subtitle && <div className="mb-5" />}
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

      <div className="relative max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <div
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 shadow-lg"
            style={{ background: '#1d348a' }}
          >
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
            </svg>
          </div>
          <h1
            className="font-extrabold mb-2"
            style={{ color: '#1d348a', fontSize: 'clamp(1.75rem, 5vw, 2.25rem)', lineHeight: 1.2 }}
          >
            Create Your Learning Profile
          </h1>
          <p className="text-gray-500 max-w-md mx-auto" style={{ fontSize: '1.05rem', lineHeight: 1.7 }}>
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

        <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-6">
          {/* ─── Section 1: Academic Information ─── */}
          <Section title="📚 Academic Information" subtitle="Tell us your current level of education.">
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="academicLevel"
                className="text-sm font-semibold text-gray-700"
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
                    'w-full appearance-none px-4 py-3.5 rounded-xl border-2 bg-white text-base text-gray-800 outline-none cursor-pointer',
                    'focus:border-[#1d348a] focus:ring-3 focus:ring-[#c2d1e7]',
                    errors.academicLevel
                      ? 'border-[#EF4444] bg-red-50'
                      : 'border-[#c2d1e7] hover:border-[#1d348a]/50',
                  ].join(' ')}
                  style={{ fontSize: '1rem', lineHeight: '1.6' }}
                >
                  <option value="" disabled>Select your level…</option>
                  <option value="elementary">Elementary School</option>
                  <option value="middle">Middle School</option>
                  <option value="high">High School</option>
                  <option value="university">University</option>
                </select>
                {/* Custom dropdown arrow */}
                <div className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </div>
              </div>
              {errors.academicLevel && (
                <p role="alert" className="text-sm flex items-center gap-1.5" style={{ color: '#EF4444' }}>
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
              <p role="alert" className="text-sm flex items-center gap-1.5 mb-3" style={{ color: '#EF4444' }}>
                <span aria-hidden="true">⚠</span>{errors.supportMode}
              </p>
            )}
            <div
              role="radiogroup"
              aria-label="Dyslexia support mode"
              className="grid grid-cols-1 sm:grid-cols-2 gap-4"
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
                      'text-left p-5 rounded-2xl border-2 transition-all duration-200 cursor-pointer focus:outline-none focus:ring-3',
                      selected
                        ? 'border-[#1d348a] bg-[#eef1f9] focus:ring-[#c2d1e7]'
                        : 'border-[#e5e9f0] bg-white hover:border-[#1d348a]/40 hover:shadow-sm focus:ring-[#c2d1e7]',
                    ].join(' ')}
                    style={{ boxShadow: selected ? '0 0 0 4px rgba(29,52,138,0.08)' : undefined }}
                  >
                    <div
                      className="flex items-center justify-center w-12 h-12 rounded-xl mb-3"
                      style={{
                        background: selected ? '#1d348a' : '#e8eef6',
                        color: selected ? 'white' : '#1d348a',
                        transition: 'all 0.2s ease',
                      }}
                    >
                      <Icon />
                    </div>
                    <p className="font-semibold text-gray-800 mb-1" style={{ fontSize: '0.97rem' }}>{label}</p>
                    <p className="text-sm text-gray-500 leading-relaxed">{description}</p>
                    {selected && (
                      <div className="mt-3 flex items-center gap-1.5 text-xs font-semibold" style={{ color: '#1d348a' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                        Selected
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
              <p role="alert" className="text-sm flex items-center gap-1.5 mb-3" style={{ color: '#EF4444' }}>
                <span aria-hidden="true">⚠</span>{errors.learningFormat}
              </p>
            )}
            <fieldset className="flex flex-col gap-3">
              <legend className="sr-only">Preferred learning format</legend>
              {LEARNING_FORMATS.map(({ id, label, description }) => {
                const selected = learningFormat === id
                return (
                  <label
                    key={id}
                    htmlFor={`format-${id}`}
                    className={[
                      'flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all duration-200',
                      selected
                        ? 'border-[#1d348a] bg-[#eef1f9]'
                        : 'border-[#e5e9f0] bg-white hover:border-[#1d348a]/40',
                    ].join(' ')}
                  >
                    <div className="flex items-center justify-center mt-0.5">
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
                        className="w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0"
                        style={{
                          borderColor: selected ? '#1d348a' : '#c2d1e7',
                          background: 'white',
                        }}
                      >
                        {selected && (
                          <div className="w-2.5 h-2.5 rounded-full" style={{ background: '#1d348a' }} />
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800" style={{ fontSize: '1rem' }}>{label}</p>
                      <p className="text-sm text-gray-500 mt-0.5">{description}</p>
                    </div>
                  </label>
                )
              })}
            </fieldset>
          </Section>

          {/* ─── Section 4: Accessibility Options ─── */}
          <Section title="⚙️ Accessibility Options" subtitle="Optional: fine-tune the interface for your comfort.">
            <div className="flex flex-col gap-7">
              {/* Font Size */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label htmlFor="fontSize" className="font-semibold text-gray-800" style={{ fontSize: '1rem' }}>
                    Font Size
                  </label>
                  <span
                    className="px-3 py-1 rounded-lg text-sm font-semibold"
                    style={{ background: '#eef1f9', color: '#1d348a' }}
                  >
                    {fontSize}px
                  </span>
                </div>
                <input
                  id="fontSize"
                  type="range"
                  min="14"
                  max="28"
                  value={fontSize}
                  onChange={e => setFontSize(Number(e.target.value))}
                  className="w-full"
                  aria-label={`Font size: ${fontSize} pixels`}
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>14px (small)</span>
                  <span>28px (large)</span>
                </div>
              </div>

              {/* Line Spacing */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label htmlFor="lineSpacing" className="font-semibold text-gray-800" style={{ fontSize: '1rem' }}>
                    Line Spacing
                  </label>
                  <span
                    className="px-3 py-1 rounded-lg text-sm font-semibold"
                    style={{ background: '#eef1f9', color: '#1d348a' }}
                  >
                    {lineSpacing.toFixed(1)}×
                  </span>
                </div>
                <input
                  id="lineSpacing"
                  type="range"
                  min="1.0"
                  max="2.5"
                  step="0.1"
                  value={lineSpacing}
                  onChange={e => setLineSpacing(Number(e.target.value))}
                  className="w-full"
                  aria-label={`Line spacing: ${lineSpacing.toFixed(1)} times`}
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>Compact</span>
                  <span>Extra spacious</span>
                </div>
              </div>

              {/* Preview card */}
              <div
                className="p-4 rounded-xl border border-[#c2d1e7] bg-[#f8fafc]"
                aria-live="polite"
                aria-label="Typography preview"
              >
                <p className="text-xs text-gray-400 mb-2 uppercase tracking-wide font-semibold">Preview</p>
                <p
                  className="text-gray-700"
                  style={{ fontSize: `${fontSize}px`, lineHeight: lineSpacing }}
                >
                  The quick brown fox jumps over the lazy dog.
                </p>
              </div>

              {/* Focus Reading Mode */}
              <div
                className="p-5 rounded-xl"
                style={{ background: '#f8fafc', border: '1px solid #e8eef6' }}
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
              className="flex items-center gap-3 px-5 py-4 rounded-2xl text-base font-medium"
              style={{ background: '#ECFDF5', color: '#10B981', border: '1px solid #6EE7B7' }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Profile saved! Your personalised learning experience is ready.
            </div>
          )}

          {/* Submit */}
          <Button
            type="submit"
            fullWidth
            disabled={loading || success}
            className="py-4 text-lg rounded-2xl mt-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Saving your profile…
              </>
            ) : success ? (
              '✓ Profile Created!'
            ) : (
              'Create Profile'
            )}
          </Button>

          <p className="text-center text-gray-400 text-sm pb-4">
            You can update your profile settings at any time.
          </p>
        </form>
      </div>
    </main>
  )
}
