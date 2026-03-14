import { useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../components/Button'

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
              <path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/>
            </svg>
            Back
          </Link>
          <div className="h-6 w-px bg-gray-200 hidden sm:block"></div>
          <div className="flex items-center gap-3">
            <div className="bg-[#1d348a] text-white p-2 rounded-xl">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
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
              className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                supportMode === mode.id
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
                  <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
                </svg>
              </div>
              <div className="pt-1">
                <h3 className="font-extrabold text-gray-800 text-2xl mb-1 leading-tight">Photosynthesis</h3>
                <p className="text-[#1d348a] bg-[#eef1f9] inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-semibold mt-2">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
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
          <div className="bg-white flex-1 rounded-3xl shadow-xl flex flex-col overflow-hidden border border-white relative" style={{ boxShadow: '0 24px 80px rgba(29,52,138,0.1)' }}>
            
            {/* AI Panel Header */}
            <div className="p-8 lg:p-10 border-b border-gray-100 bg-white z-10 flex flex-col md:flex-row md:items-start justify-between gap-6">
              <div>
                <h2 className="text-3xl font-extrabold text-[#1d1f2e] mb-3 leading-tight">
                  Photosynthesis — Personalized Explanation
                </h2>
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold bg-[#ECFDF5] text-[#10B981] border border-[#6EE7B7]">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                  Adapted for: {
                    supportMode === 'phonological' ? 'Phonological Support' :
                    supportMode === 'visual' ? 'Visual Support' : 'Reading Speed Support'
                  }
                </div>
              </div>

              {/* Source Reference Tag */}
              <div className="bg-[#f8fafc] border border-[#e8eef6] p-4 rounded-2xl flex items-center gap-3 shrink-0">
                <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-[#1d348a] shadow-sm">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-semibold mb-0.5">BASED ON TRUSTED SOURCE</p>
                  <p className="font-bold text-gray-800 text-sm">Photosynthesis Lesson PDF</p>
                </div>
              </div>
            </div>

            {/* AI Panel Body (Dynamic based on support mode) */}
            <div className="flex-1 overflow-y-auto p-8 lg:p-12 relative" style={{ background: '#fafbfc' }}>
              
              {/* === Phonological Mode Mock === */}
              {supportMode === 'phonological' && (
                <div className="max-w-3xl animate-in fade-in duration-500">
                  <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 mb-8">
                    <div className="flex items-center justify-between flex-wrap gap-4 mb-8">
                      {/* Syllable Breakdown */}
                      <h3 className="text-4xl font-extrabold tracking-widest text-[#1d348a]">
                        Pho-to-<span className="text-[#F59E0B]">syn</span>-the-sis
                      </h3>
                      
                      {/* Audio Pronunciation */}
                      <button className="flex items-center gap-3 px-6 py-4 bg-[#1d348a] hover:bg-[#162870] text-white rounded-2xl font-bold transition-transform hover:-translate-y-1 shadow-lg shadow-[#1d348a]/30">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
                        </svg>
                        Play pronunciation
                      </button>
                    </div>

                    <div className="space-y-6 text-[#1d1f2e]">
                      <p className="text-2xl font-medium leading-relaxed bg-[#f8fafc] p-6 rounded-2xl border-l-4 border-[#1d348a]">
                        Photosynthesis is how plants make food.
                      </p>
                      
                      <div className="bg-[#f8fafc] p-6 rounded-2xl border-l-4 border-[#10B981]">
                        <p className="text-2xl font-medium mb-4">Plants need three things:</p>
                        <ul className="text-2xl font-medium space-y-4 pl-4">
                          <li className="flex items-center gap-3"><span className="text-3xl">☀️</span> sunlight</li>
                          <li className="flex items-center gap-3"><span className="text-3xl">💧</span> water</li>
                          <li className="flex items-center gap-3"><span className="text-3xl">💨</span> carbon dioxide</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* === Visual Support Mode Mock === */}
              {supportMode === 'visual' && (
                <div className="max-w-4xl animate-in fade-in duration-500">
                  <div className="bg-white p-8 lg:p-12 rounded-3xl shadow-sm border border-gray-100 mb-8">
                    
                    {/* Visual Support Features: Large text, wide spacing, highlighted keywords */}
                    <h3 className="text-5xl font-extrabold mb-12 text-gray-900 border-b-2 border-gray-100 pb-6 inline-block" style={{ lineHeight: '1.2' }}>
                      Photosynthesis
                    </h3>

                    <div className="space-y-12" style={{ fontSize: '28px', lineHeight: '2.2', letterSpacing: '0.5px' }}>
                      <p className="text-gray-800">
                        <span className="bg-[#FEF3C7] text-[#D97706] font-bold px-3 py-1 rounded-xl">Plants make food</span> using <span className="text-[#10B981] font-bold">sunlight</span>.
                      </p>
                      
                      <p className="text-gray-800">
                        This process happens in the <span className="bg-[#D1FAE5] text-[#059669] font-bold px-3 py-1 rounded-xl">leaves</span>.
                      </p>
                      
                      <p className="text-gray-800">
                        They breathe in <span className="font-bold underline decoration-4 decoration-[#1d348a] underline-offset-8">carbon dioxide</span> and release fresh <span className="bg-[#DBEAFE] text-[#2563EB] font-bold px-3 py-1 rounded-xl">oxygen</span>.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* === Reading Speed Mode Mock === */}
              {supportMode === 'reading-speed' && (
                <div className="max-w-3xl mx-auto flex flex-col items-center animate-in fade-in duration-500 py-10">
                  
                  {/* Step container */}
                  <div className="w-full relative">
                    {/* Previous step indicator */}
                    {step > 1 && (
                       <div className="absolute -top-16 left-0 right-0 flex justify-center opacity-40">
                         <div className="bg-white px-6 py-3 rounded-2xl shadow-sm text-gray-400 font-bold blur-[1px] scale-95 border border-gray-200">
                           Step {step - 1} ...
                         </div>
                       </div>
                    )}

                    <div className="bg-white p-10 lg:p-14 rounded-[2rem] shadow-2xl border-2 border-[#e8eef6] text-center transform transition-all duration-500 relative z-10 w-full">
                      <span className="text-[#1d348a] font-black tracking-widest uppercase text-sm mb-6 block bg-[#eef1f9] w-fit mx-auto px-5 py-2 rounded-full">
                        Step {step} of 3
                      </span>
                      
                      {/* Progressive Content */}
                      <p className="text-4xl lg:text-5xl font-extrabold text-[#1d1f2e] leading-tight mt-8 mb-6">
                        {step === 1 && 'Plants absorb sunlight through their leaves.'}
                        {step === 2 && 'They take in water from the ground.'}
                        {step === 3 && 'Together, sunlight and water create energy for the plant.'}
                      </p>
                    </div>
                  </div>

                  {/* Next Step Action */}
                  <div className="mt-14 w-full flex justify-center">
                    {step < 3 ? (
                      <button 
                        onClick={() => setStep(s => s + 1)}
                        className="group flex items-center gap-4 px-10 py-6 bg-[#10B981] hover:bg-[#059669] text-white rounded-full font-black text-2xl shadow-xl shadow-[#10B981]/30 transition-all hover:scale-105"
                      >
                        Next
                        <svg className="w-8 h-8 group-hover:translate-x-2 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
                      </button>
                    ) : (
                      <button 
                        onClick={() => setStep(1)}
                        className="group flex items-center gap-3 px-8 py-5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-full font-bold text-xl transition-all"
                      >
                        <svg className="w-6 h-6 group-hover:-rotate-180 transition-transform duration-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
                        Restart Explanation
                      </button>
                    )}
                  </div>

                </div>
              )}

            </div>
          </div>
        </section>

      </main>
    </div>
  )
}
