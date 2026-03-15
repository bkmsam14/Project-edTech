import { useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import Button from '../components/Button'

export default function QuizResults() {
  const location = useLocation()
  const state = location.state

  // Use data passed from Quiz page, or show fallback
  const results = state ? {
    quizTitle: state.quizTitle || 'Quiz',
    totalQuestions: state.totalQuestions || 0,
    correctAnswers: (state.questions || []).filter(q => q.isCorrect).length,
    questions: (state.questions || []).map(q => ({
      question: q.question,
      userAnswer: q.userAnswer,
      correctAnswer: q.correctAnswer,
      isCorrect: q.isCorrect,
      hintsUsed: q.hintsUsed || 0,
    }))
  } : null

  if (!results) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#efefee' }}>
        <div className="text-center max-w-md">
          <p className="text-xl font-bold text-gray-600 mb-4">No quiz results to display.</p>
          <Link to="/quiz" className="px-6 py-3 bg-[#1d348a] text-white font-bold rounded-xl hover:bg-[#162870] transition-colors inline-block">
            Take a Quiz
          </Link>
        </div>
      </div>
    )
  }

  const percentage = results.totalQuestions > 0
    ? Math.round((results.correctAnswers / results.totalQuestions) * 100)
    : 0
  const passed = percentage >= 70

  // Persist this attempt to localStorage for the Progress page
  useEffect(() => {
    if (!results) return
    const entry = {
      id: Date.now(),
      quizTitle: results.quizTitle,
      date: new Date().toISOString(),
      percentage,
      passed,
      correctAnswers: results.correctAnswers,
      totalQuestions: results.totalQuestions,
    }
    try {
      const existing = JSON.parse(localStorage.getItem('eduai_quiz_history') || '[]')
      const updated = [entry, ...existing].slice(0, 20) // keep last 20
      localStorage.setItem('eduai_quiz_history', JSON.stringify(updated))
    } catch (_) {}
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#efefee', fontSize: 'var(--user-font-size)' }}>
      {/* Header */}
      <header className="bg-white px-6 lg:px-10 py-4 shadow-sm flex items-center justify-between border-b border-[#e8eef6]">
        <div className="flex items-center gap-6">
          <Link to="/workspace" className="text-gray-500 hover:text-[#1d348a] font-medium flex items-center gap-2 transition-colors">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5" /><polyline points="12 19 5 12 12 5" />
            </svg>
            Back to Workspace
          </Link>
          <div className="h-6 w-px bg-gray-200 hidden sm:block"></div>
          <h1 className="font-extrabold text-[#1d1f2e] text-xl tracking-tight">Quiz Results</h1>
        </div>
      </header>

      {/* Decorative background blobs */}
      <div aria-hidden="true" className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-20 -left-20 w-[28rem] h-[28rem] rounded-full opacity-25" style={{ background: '#10B981', filter: 'blur(100px)' }} />
        <div className="absolute bottom-40 -right-20 w-[32rem] h-[32rem] rounded-full opacity-20" style={{ background: '#1d348a', filter: 'blur(120px)' }} />
        <div className="absolute top-1/3 left-1/3 w-[25rem] h-[25rem] rounded-full opacity-15" style={{ background: '#F59E0B', filter: 'blur(100px)' }} />
      </div>

      {/* Main Content */}
      <main className="flex-1 p-6 lg:p-10 relative z-10">
        <div className="max-w-4xl mx-auto">

          {/* Score Card */}
          <div className={`bg-gradient-to-br ${passed ? 'from-[#10B981] to-[#059669]' : 'from-[#F59E0B] to-[#D97706]'} rounded-3xl p-8 lg:p-10 shadow-2xl mb-8 text-white text-center`}>
            <div className={`w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center ${passed ? 'bg-white/20' : 'bg-white/20'} backdrop-blur-sm`}>
              {passed ? (
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              ) : (
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              )}
            </div>

            <h2 className="text-4xl lg:text-5xl font-black mb-3">{percentage}%</h2>
            <p className="text-xl lg:text-2xl font-bold mb-4">
              {passed ? 'Great Job!' : 'Keep Learning!'}
            </p>
            <p className="text-lg opacity-90">
              You got <span className="font-black">{results.correctAnswers}</span> out of <span className="font-black">{results.totalQuestions}</span> questions correct
            </p>

            {!passed && (
              <div className="mt-6 bg-white/10 backdrop-blur-sm rounded-2xl p-5 border-2 border-white/20">
                <p className="text-base font-semibold">Don't worry! Learning takes time. Review the explanations and try again when you're ready.</p>
              </div>
            )}
          </div>

          {/* Question Review */}
          <div className="bg-white rounded-3xl shadow-xl border-2 border-gray-100 p-8 lg:p-10 mb-8">
            <h3 className="text-2xl font-black text-gray-900 mb-6 flex items-center gap-3">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-[#1d348a]">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
              </svg>
              Review Your Answers
            </h3>

            <div className="space-y-6">
              {results.questions.map((q, index) => (
                <div
                  key={index}
                  className={`p-6 rounded-2xl border-2 ${q.isCorrect
                      ? 'bg-[#ECFDF5] border-[#10B981]'
                      : 'bg-[#FEF2F2] border-red-300'
                    }`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 font-bold text-white ${q.isCorrect ? 'bg-[#10B981]' : 'bg-red-400'
                      }`}>
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="text-lg font-bold text-gray-900 mb-3">{q.question}</p>

                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-gray-600">Your answer:</span>
                          <span className={`text-base font-bold ${q.isCorrect ? 'text-[#059669]' : 'text-red-600'}`}>
                            {q.userAnswer}
                          </span>
                          {q.isCorrect ? (
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-[#10B981]">
                              <polyline points="20 6 9 17 4 12" />
                            </svg>
                          ) : (
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-red-400">
                              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                            </svg>
                          )}
                        </div>

                        {!q.isCorrect && (
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-gray-600">Correct answer:</span>
                            <span className="text-base font-bold text-[#059669]">{q.correctAnswer}</span>
                          </div>
                        )}

                        {q.hintsUsed > 0 && (
                          <div className="flex items-center gap-2 mt-2">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-[#F59E0B]">
                              <circle cx="12" cy="12" r="10" /><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" />
                            </svg>
                            <span className="text-sm text-gray-600">Used {q.hintsUsed} hint{q.hintsUsed > 1 ? 's' : ''}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/quiz">
              <button className="px-8 py-4 bg-gradient-to-r from-[#1d348a] to-[#2d4aa0] hover:from-[#162870] hover:to-[#1d348a] text-white rounded-2xl font-bold shadow-lg hover:scale-105 transition-all flex items-center gap-3">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
                </svg>
                Retake Quiz
              </button>
            </Link>

            <Link to="/workspace">
              <button className="px-8 py-4 bg-white hover:bg-gray-50 text-gray-700 border-2 border-gray-200 rounded-2xl font-bold shadow-lg hover:scale-105 transition-all flex items-center gap-3">
                Continue Learning
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </button>
            </Link>
          </div>

        </div>
      </main>
    </div>
  )
}
