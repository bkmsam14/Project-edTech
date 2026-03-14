import { useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../components/Button'
import ExplanationCard from '../components/ExplanationCard'

export default function Workspace() {
  const [supportMode, setSupportMode] = useState('visual') // 'phonological', 'visual', 'reading-speed'
  const [step, setStep] = useState(1)

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#efefee' }}>
      {/* Header bar */}
      <header className="bg-white px-6 lg:px-10 py-4 shadow-sm flex items-center justify-between border-b border-[#e8eef6] sticky top-0 z-20">
        <div className="flex items-center gap-6">
          <Link to="/lessons" className="text-gray-500 hover:text-[#1d348a] font-medium flex items-center gap-2 transition-colors">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5" /><polyline points="12 19 5 12 12 5" />
            </svg>
            Back
          </Link>
          <div className="h-6 w-px bg-gray-200 hidden sm:block"></div>
          <div className="flex items-center gap-3">
            <div className="bg-[#1d348a] text-white p-2 rounded-xl">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
              </svg>
            </div>
            <h1 className="font-extrabold text-[#1d1f2e] text-xl tracking-tight hidden sm:block">DysLearn Workspace</h1>
          </div>
        </div>

        {/* Demo Mode Toggle (Right side of header) */}
        <div className="flex items-center gap-3 bg-[#e8eef6] p-1.5 rounded-2xl">
          {[
            { id: 'phonological', label: 'Phonological' },
            { id: 'visual', label: 'Visual' },
            { id: 'reading-speed', label: 'Reading Speed' }
          ].map(mode => (
            <button
              key={mode.id}
              onClick={() => { setSupportMode(mode.id); setStep(1); }}
              className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${supportMode === mode.id
                ? 'bg-white text-[#1d348a] shadow-sm'
                : 'text-gray-500 hover:text-gray-800'
                }`}
            >
              {mode.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Workspace Layout */}
      <main className="flex-1 flex flex-col lg:flex-row gap-6 lg:gap-8 p-6 lg:p-10 max-w-[1600px] w-full mx-auto relative z-10">

        {/* Decorative background blobs */}
        <div aria-hidden="true" className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
          <div className="absolute top-20 -left-40 w-[30rem] h-[30rem] rounded-full opacity-30" style={{ background: '#c2d1e7', filter: 'blur(100px)' }} />
          <div className="absolute bottom-10 -right-20 w-[40rem] h-[40rem] rounded-full opacity-20" style={{ background: '#c2d1e7', filter: 'blur(120px)' }} />
        </div>

        {/* ── Left Column: Lesson Tools ── */}
        <section className="lg:w-1/3 flex flex-col gap-6 h-[calc(100vh-8rem)] overflow-y-auto pr-2 pb-20 lg:pb-0"
          style={{ scrollbarWidth: 'thin' }}>

          {/* Lesson Information Card */}
          <div className="bg-white rounded-3xl p-8 shadow-lg border border-white" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
            <h2 className="text-gray-400 font-bold uppercase tracking-widest text-xs mb-4">Lesson Information</h2>
            <div className="flex items-start gap-4">
              <div className="p-3 bg-[#eef1f9] text-[#1d348a] rounded-2xl border-2 border-white shadow-sm shrink-0">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
                </svg>
              </div>
              <div className="pt-1">
                <h3 className="font-extrabold text-gray-800 text-2xl mb-1 leading-tight">Photosynthesis</h3>
                <p className="text-[#1d348a] bg-[#eef1f9] inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-semibold mt-2">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>
                  biology_notes.pdf
                </p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-3xl p-8 shadow-lg border border-white" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
            <h2 className="text-gray-400 font-bold uppercase tracking-widest text-xs mb-5">Quick Actions</h2>
            <div className="flex flex-col gap-3">
              {[
                { icon: '🪄', label: 'Explain lesson', desc: 'Get a personalized breakdown' },
                { icon: '✨', label: 'Simplify lesson', desc: 'Make the language easier' },
                { icon: '📝', label: 'Summarize lesson', desc: 'Key points only' },
                { icon: '📚', label: 'Define key concepts', desc: 'Vocabulary and terminology' },
              ].map(action => (
                <button
                  key={action.label}
                  className="w-full text-left p-4 rounded-2xl border-2 border-[#e8eef6] hover:border-[#1d348a]/30 hover:bg-[#f8fafc] transition-all flex items-center gap-4 group focus:outline-none focus:ring-4 focus:ring-[#c2d1e7]"
                >
                  <div className="w-12 h-12 bg-white rounded-xl shadow-sm border border-gray-100 flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
                    {action.icon}
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-800 text-[1rem] leading-none mb-1.5">{action.label}</h4>
                    <p className="text-sm text-gray-500">{action.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Ask Question Box */}
          <div className="bg-white rounded-3xl p-8 shadow-lg border border-white mb-2" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
            <h2 className="text-gray-400 font-bold uppercase tracking-widest text-xs mb-5">Ask Questions</h2>
            <div className="bg-[#f8fafc] rounded-2xl p-4 border border-[#e8eef6] focus-within:border-[#1d348a] focus-within:ring-4 focus-within:ring-[#c2d1e7] transition-all">
              <textarea
                placeholder="Ask a question about this lesson..."
                className="w-full bg-transparent outline-none resize-none text-gray-800 placeholder-gray-400 text-lg leading-relaxed h-28"
              ></textarea>
              <div className="flex justify-end mt-2">
                <Button variant="primary" className="rounded-xl px-6">
                  Ask AI
                </Button>
              </div>
            </div>

            <div className="mt-6">
              <p className="text-xs text-gray-400 font-semibold mb-3">SUGGESTED PROMPTS</p>
              <div className="flex flex-wrap gap-2">
                {['What is photosynthesis?', 'Explain chlorophyll', 'Summarize the process'].map(prompt => (
                  <button key={prompt} className="px-4 py-2 bg-[#eef1f9] hover:bg-[#dce3f5] text-[#1d348a] text-sm font-medium rounded-full transition-colors">
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ── Right Column: AI Response Panel ── */}
        <section className="lg:w-2/3 flex flex-col h-[calc(100vh-8rem)]">
          <ExplanationCard supportMode={supportMode} step={step} setStep={setStep} />
        </section>

      </main>
    </div>
  )
}
