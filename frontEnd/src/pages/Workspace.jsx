import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Button from '../components/Button'
import ExplanationCard from '../components/ExplanationCard'
import AIResponseDisplay from '../components/AIResponseDisplay'
import { learn } from '../services/api'

export default function Workspace() {
  const [supportMode, setSupportMode] = useState('visual')
  const [step, setStep] = useState(1)
  const [hoveredPanel, setHoveredPanel] = useState(null)
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiResponse, setAiResponse] = useState(null)
  const [error, setError] = useState(null)

  // Load profile from localStorage
  const profile = JSON.parse(localStorage.getItem('eduai_profile') || '{}')
  const userId = profile.user_id || 'user_001'
  const lesson = JSON.parse(localStorage.getItem('eduai_lesson') || '{}')
  const lessonId = lesson.lesson_id || localStorage.getItem('eduai_lesson_id') || ''
  const documentId = lesson.document_id || null
  const course = JSON.parse(localStorage.getItem('eduai_course') || '{}')
  const courseId = course.course_id || null
  const courseName = course.course_name || null

  useEffect(() => {
    if (profile.support_mode) setSupportMode(profile.support_mode)
  }, [])

  async function handleAsk(msg, intent = 'explain') {
    if (!msg?.trim()) return
    setLoading(true)
    setError(null)
    setAiResponse(null)
    try {
      const res = await learn({
        userId,
        lessonId,
        documentId,
        courseId,
        question: msg,
        intent,
        supportMode,
        preferredFormat: profile.preferred_format || 'simplified_text',
      })
      setAiResponse(res)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  function handleQuickAction(label) {
    const intents = {
      'Explain lesson': 'explain',
      'Simplify lesson': 'simplify',
      'Summarize lesson': 'summarize',
      'Define concepts': 'qa',
    }
    handleAsk(label, intents[label] || 'explain')
  }

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#efefee', fontSize: 'var(--user-font-size)' }}>
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
            <h1 className="font-extrabold text-[#1d1f2e] text-xl tracking-tight hidden sm:block">
              DysLearn Workspace
              {courseName && <span className="text-sm font-medium text-gray-400 ml-2">| {courseName}</span>}
            </h1>
          </div>
        </div>
        <div className="flex items-center gap-3 bg-[#e8eef6] p-1.5 rounded-2xl">
          {[
            { id: 'phonological', label: 'Phonological' },
            { id: 'visual', label: 'Visual' },
            { id: 'reading-speed', label: 'Reading Speed' }
          ].map(mode => (
            <button
              key={mode.id}
              onClick={() => { setSupportMode(mode.id); setStep(1) }}
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

      <main className="flex-1 flex flex-col lg:flex-row gap-6 lg:gap-8 p-6 lg:p-10 max-w-[1600px] w-full mx-auto relative z-10">
        <div aria-hidden="true" className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
          <div className="absolute top-20 -left-40 w-[30rem] h-[30rem] rounded-full opacity-30" style={{ background: '#c2d1e7', filter: 'blur(100px)' }} />
          <div className="absolute bottom-10 -right-20 w-[40rem] h-[40rem] rounded-full opacity-20" style={{ background: '#c2d1e7', filter: 'blur(120px)' }} />
        </div>

        {/* Course Context Banner */}
        {courseName && (
          <div className="lg:absolute lg:top-0 lg:left-0 lg:right-0 lg:-mt-4 mb-4 lg:mb-0">
            <div className="bg-gradient-to-r from-[#1d348a] to-[#2d4aa0] rounded-2xl p-4 shadow-lg border-2 border-white flex items-center gap-4">
              <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center shrink-0">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-white/70 font-bold uppercase tracking-wider mb-0.5">Current Course</p>
                <p className="text-white font-black text-sm lg:text-base truncate">{courseName}</p>
              </div>
              <div className="px-3 py-1.5 bg-white/10 rounded-lg backdrop-blur-sm">
                <p className="text-white text-xs font-bold">AI Active</p>
              </div>
            </div>
          </div>
        )}

        {/* Left Column */}
        <section className={`flex flex-col gap-6 h-[calc(100vh-8rem)] transition-all duration-700 ${courseName ? 'lg:mt-20' : ''} ${hoveredPanel === 'quick' || hoveredPanel === 'chat' ? 'lg:flex-[0.45]' : hoveredPanel === 'lesson' ? 'lg:flex-[0.18]' : 'lg:flex-[0.25]'}`}>
          {/* Quick Actions */}
          <div
            className={`bg-white rounded-[2.5rem] p-6 lg:p-8 shadow-lg border border-white flex flex-col overflow-y-auto transition-all duration-700 ${hoveredPanel === 'quick' ? 'flex-[1.8] scale-[1.03] z-20' : hoveredPanel ? 'flex-[0.4] opacity-50' : 'flex-1'}`}
            style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}
            onMouseEnter={() => setHoveredPanel('quick')}
            onMouseLeave={() => setHoveredPanel(null)}
          >
            <h2 className="text-gray-400 font-bold uppercase tracking-widest text-[10px] mb-4 shrink-0">Quick Actions</h2>
            <div className="flex flex-col gap-2.5">
              {[
                {
                  icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
                  label: 'Explain lesson',
                  desc: 'Get personalized breakdown'
                },
                {
                  icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>,
                  label: 'Simplify lesson',
                  desc: 'Make language easier'
                },
                {
                  icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="15" x2="15" y2="15"/></svg>,
                  label: 'Summarize lesson',
                  desc: 'Key points only'
                },
                {
                  icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>,
                  label: 'Define concepts',
                  desc: 'Vocabulary help'
                },
              ].map(action => (
                <button
                  key={action.label}
                  onClick={() => handleQuickAction(action.label)}
                  disabled={loading}
                  className="w-full text-left p-3 rounded-2xl border-2 border-[#e8eef6] hover:border-[#1d348a]/30 hover:bg-[#f8fafc] transition-all flex items-center gap-3 group disabled:opacity-50"
                >
                  <div className="w-10 h-10 bg-white rounded-xl shadow-sm border border-gray-100 flex items-center justify-center text-[#1d348a] group-hover:scale-110 transition-transform shrink-0">
                    {action.icon}
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-800 text-sm leading-tight mb-0.5">{action.label}</h4>
                    <p className="text-xs text-gray-500">{action.desc}</p>
                  </div>
                </button>
              ))}
            </div>
            <Link to="/quiz" className="shrink-0 mt-4">
              <button className="w-full p-4 rounded-2xl bg-gradient-to-r from-[#10B981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-white transition-all flex items-center gap-3 group shadow-lg hover:scale-105">
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center shrink-0">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                    <polyline points="9 11 12 14 22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                </div>
                <div className="flex-1 text-left">
                  <h4 className="font-black text-white text-sm leading-tight mb-0.5">Take Quiz</h4>
                  <p className="text-xs text-white/80">Test your understanding</p>
                </div>
              </button>
            </Link>
          </div>

          {/* Ask Question */}
          <div
            className={`bg-white rounded-[2.5rem] p-6 lg:p-8 shadow-lg border border-white flex flex-col overflow-y-auto transition-all duration-700 ${hoveredPanel === 'chat' ? 'flex-[1.8] scale-[1.03] z-20' : hoveredPanel ? 'flex-[0.4] opacity-50' : 'flex-1'}`}
            style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}
            onMouseEnter={() => setHoveredPanel('chat')}
            onMouseLeave={() => setHoveredPanel(null)}
          >
            <h2 className="text-gray-400 font-bold uppercase tracking-widest text-[10px] mb-4 shrink-0">Chat / Ask Questions</h2>
            <div className="bg-[#f8fafc] rounded-2xl p-3 border border-[#e8eef6] focus-within:border-[#1d348a] focus-within:ring-4 focus-within:ring-[#c2d1e7] transition-all flex-1 flex flex-col min-h-[60px]">
              <textarea
                placeholder="Ask about this lesson..."
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAsk(question, 'qa') } }}
                className="w-full bg-transparent outline-none resize-none text-gray-800 placeholder-gray-400 text-sm leading-relaxed flex-1"
              />
              <div className="flex justify-end mt-2 pt-2 border-t border-[#e8eef6]">
                <Button
                  variant="primary"
                  className="rounded-xl px-5 py-2 text-sm shrink-0"
                  onClick={() => handleAsk(question, 'qa')}
                  disabled={loading || !question.trim()}
                >
                  {loading ? 'Thinking...' : 'Ask AI'}
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Main Content: AI Response */}
        <section
          className={`flex flex-col h-[calc(100vh-8rem)] transition-all duration-700 ${courseName ? 'lg:mt-20' : ''} ${hoveredPanel === 'lesson' ? 'lg:flex-[0.85] scale-[1.01] z-20' : hoveredPanel ? 'lg:flex-[0.6] opacity-60' : 'lg:flex-[0.75]'}`}
          onMouseEnter={() => setHoveredPanel('lesson')}
          onMouseLeave={() => setHoveredPanel(null)}
        >
          {loading ? (
            <div className="bg-white rounded-[2.5rem] p-8 shadow-lg flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin w-12 h-12 border-4 border-[#c2d1e7] border-t-[#1d348a] rounded-full mx-auto mb-4"></div>
                <p className="text-gray-500 font-medium">AI is thinking...</p>
              </div>
            </div>
          ) : error ? (
            <div className="bg-white rounded-[2.5rem] p-8 shadow-lg flex-1">
              <div className="bg-red-50 text-red-700 p-4 rounded-2xl">{error}</div>
            </div>
          ) : aiResponse ? (
            <AIResponseDisplay response={aiResponse} supportMode={supportMode} />
          ) : (
            <ExplanationCard supportMode={supportMode} step={step} setStep={setStep} />
          )}
        </section>
      </main>
    </div>
  )
}
