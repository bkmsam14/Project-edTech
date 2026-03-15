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
        <section className="lg:w-1/4 flex flex-col gap-6 h-[calc(100vh-8rem)] overflow-y-auto pr-2 pb-20 lg:pb-0"
          style={{ scrollbarWidth: 'thin' }}>



          {/* Quick Actions */}
          <div className="bg-white rounded-3xl p-6 shadow-lg border border-white" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
            <h2 className="text-gray-400 font-bold uppercase tracking-widest text-[10px] mb-4">Quick Actions</h2>
            <div className="flex flex-col gap-2.5">
              {[
                { icon: '🪄', label: 'Explain lesson', desc: 'Get personalized breakdown' },
                { icon: '✨', label: 'Simplify lesson', desc: 'Make language easier' },
                { icon: '📝', label: 'Summarize lesson', desc: 'Key points only' },
                { icon: '📚', label: 'Define concepts', desc: 'Vocabulary help' },
              ].map(action => (
                <button
                  key={action.label}
                  className="w-full text-left p-3 rounded-xl border-2 border-[#e8eef6] hover:border-[#1d348a]/30 hover:bg-[#f8fafc] transition-all flex items-center gap-3 group focus:outline-none focus:ring-4 focus:ring-[#c2d1e7]"
                >
                  <div className="w-10 h-10 bg-white rounded-lg shadow-sm border border-gray-100 flex items-center justify-center text-lg group-hover:scale-110 transition-transform shrink-0">
                    {action.icon}
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-800 text-sm leading-tight mb-0.5">{action.label}</h4>
                    <p className="text-xs text-gray-500">{action.desc}</p>
                  </div>
                </button>
              ))}
            </div>

            {/* Take Quiz Button */}
            <Link to="/quiz">
              <button className="w-full mt-4 p-4 rounded-xl bg-gradient-to-r from-[#10B981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-white transition-all flex items-center gap-3 group shadow-lg hover:scale-105">
                <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center text-lg shrink-0 backdrop-blur-sm">
                  ✅
                </div>
                <div className="flex-1 text-left">
                  <h4 className="font-black text-white text-sm leading-tight mb-0.5">Take Quiz</h4>
                  <p className="text-xs text-white/80">Test your understanding</p>
                </div>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </button>
            </Link>
          </div>

          {/* Ask Question Box */}
          <div className="bg-white rounded-3xl p-6 shadow-lg border border-white mb-2" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
            <h2 className="text-gray-400 font-bold uppercase tracking-widest text-[10px] mb-4">Ask Questions</h2>
            <div className="bg-[#f8fafc] rounded-xl p-3 border border-[#e8eef6] focus-within:border-[#1d348a] focus-within:ring-4 focus-within:ring-[#c2d1e7] transition-all">
              <textarea
                placeholder="Ask about this lesson..."
                className="w-full bg-transparent outline-none resize-none text-gray-800 placeholder-gray-400 text-sm leading-relaxed h-20"
              ></textarea>
              <div className="flex justify-end mt-2">
                <Button variant="primary" className="rounded-lg px-5 py-2 text-sm">
                  Ask AI
                </Button>
              </div>
            </div>

            <div className="mt-4">
              <p className="text-[10px] text-gray-400 font-semibold mb-2">SUGGESTED</p>
              <div className="flex flex-wrap gap-1.5">
                {['What is photosynthesis?', 'Explain chlorophyll', 'Summarize'].map(prompt => (
                  <button key={prompt} className="px-3 py-1.5 bg-[#eef1f9] hover:bg-[#dce3f5] text-[#1d348a] text-xs font-medium rounded-full transition-colors">
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ── Right Column: AI Response Panel ── */}
        <section className="lg:w-3/4 flex flex-col h-[calc(100vh-8rem)]">
          <ExplanationCard supportMode={supportMode} step={step} setStep={setStep} />
        </section>

      </main>
    </div>
  )
}
