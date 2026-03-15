import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Button from '../components/Button'
import { getRecommendations, getProfile } from '../services/api'

export default function ProgressPage() {
  const [loading, setLoading] = useState(true)
  const [studentData, setStudentData] = useState({
    name: 'Student',
    supportMode: 'Visual Support',
    currentLesson: 'N/A',
    overallMastery: 0,
    recentQuizScore: 0,
    lastActive: 'Today'
  })
  const [topicProgress, setTopicProgress] = useState([])
  const [weakConcepts, setWeakConcepts] = useState([])
  const [recentActivity, setRecentActivity] = useState([])

  useEffect(() => {
    async function fetchData() {
      try {
        const profile = JSON.parse(localStorage.getItem('eduai_profile') || '{}')
        const userId = profile.user_id || 'user_001'

        // Load quiz history from localStorage
        const quizHistory = JSON.parse(localStorage.getItem('eduai_quiz_history') || '[]')

        // Derive stats from quiz history
        const recentQuizScore = quizHistory.length > 0 ? quizHistory[0].percentage : 0
        const overallMastery = quizHistory.length > 0
          ? Math.round(quizHistory.reduce((sum, q) => sum + q.percentage, 0) / quizHistory.length)
          : 0

        // Build recent activity feed from quiz history (last 5)
        const activityFeed = quizHistory.slice(0, 5).map((q, i) => ({
          id: q.id || i,
          type: 'quiz',
          title: q.quizTitle || 'Quiz',
          date: new Date(q.date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
          score: q.percentage,
          passed: q.passed,
        }))
        setRecentActivity(activityFeed)

        // Update student data
        const lesson = JSON.parse(localStorage.getItem('eduai_lesson') || '{}')
        setStudentData(prev => ({
          ...prev,
          name: profile.name || profile.full_name || profile.user_id || 'Student',
          supportMode: profile.support_mode || 'Visual Support',
          currentLesson: lesson.title || 'N/A',
          lastActive: 'Today',
          recentQuizScore,
          overallMastery,
        }))

        // Try to load recommendations for topic progress
        const [recResult] = await Promise.allSettled([
          getRecommendations({ userId, depth: 3 }),
        ])

        if (recResult.status === 'fulfilled') {
          const recData = recResult.value?.data || recResult.value || {}
          const recommendations = recData.recommendations || []

          if (recommendations.length > 0) {
            const colors = [
              'from-[#10B981] to-[#059669]',
              'from-[#3B82F6] to-[#2563EB]',
              'from-[#F59E0B] to-[#D97706]',
            ]
            setTopicProgress(recommendations.slice(0, 3).map((r, i) => ({
              id: i + 1,
              name: r.title || r.lesson_id || `Topic ${i + 1}`,
              mastery: Math.round((r.score || 0.5) * 100),
              color: colors[i % colors.length],
            })))
          }

          const weakConceptsData = recData.weak_concepts || []
          setWeakConcepts(weakConceptsData.map((c, i) => ({
            id: i + 1,
            concept: typeof c === 'string' ? c : c.concept || `Concept ${i + 1}`,
            urgency: i === 0 ? 'high' : 'medium',
          })))
        }

      } catch (err) {
        console.error('Failed to fetch progress data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#efefee' }}>
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#1d348a] border-t-transparent rounded-full animate-spin mx-auto mb-6" />
          <p className="text-xl font-bold text-gray-600">Loading your progress...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#efefee] flex flex-col items-center py-6 lg:py-10 px-4 lg:px-6 font-sans" style={{ fontSize: 'var(--user-font-size)' }}>

      {/* Header bar */}
      <div className="w-full max-w-[1400px] flex items-center justify-between mb-8">
        <Link to="/home" className="text-gray-500 hover:text-[#1d348a] font-bold flex items-center gap-2 transition-colors bg-white px-5 py-2.5 rounded-xl shadow-sm border border-gray-100">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5" /><polyline points="12 19 5 12 12 5" />
          </svg>
          Back to Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <div className="bg-[#1d348a] text-white p-2 rounded-xl">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20v-6M6 20V10M18 20V4" /></svg>
          </div>
          <h1 className="font-black text-[#1d1f2e] text-2xl tracking-tight hidden sm:block">My Progress</h1>
        </div>
      </div>

      <div className="w-full max-w-[1400px] grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">

        {/* Left Column (Overview & Next Steps) */}
        <div className="lg:col-span-1 flex flex-col gap-6 lg:gap-8">

          {/* 1. Learning Overview */}
          <div className="bg-white rounded-[2rem] p-8 shadow-xl border border-white relative overflow-hidden" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
            <div className="absolute top-0 right-0 w-40 h-40 bg-[#c2d1e7] rounded-full blur-[50px] opacity-30 -mr-10 -mt-10 pointer-events-none"></div>

            <h2 className="text-gray-400 font-bold uppercase tracking-[3px] text-xs mb-8 border-b border-gray-100 pb-4">Learning Overview</h2>

            <div className="flex flex-col items-center mb-8 relative z-10">
              <div className="relative mb-4">
                <svg className="w-32 h-32 transform -rotate-90">
                  <circle cx="64" cy="64" r="56" stroke="#f1f5f9" strokeWidth="12" fill="none" />
                  <circle cx="64" cy="64" r="56" stroke="#10B981" strokeWidth="12" fill="none" strokeDasharray="351.85" strokeDashoffset={351.85 - (351.85 * studentData.overallMastery) / 100} className="transition-all duration-1000 ease-out" strokeLinecap="round" />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center flex-col">
                  <span className="text-4xl font-black text-gray-800">{studentData.overallMastery}%</span>
                </div>
              </div>
              <p className="font-extrabold text-[#1d1f2e] text-lg">Overall Mastery</p>
            </div>

            <div className="space-y-4 relative z-10">
              <div className="flex justify-between items-center p-4 bg-[#f8fafc] rounded-2xl border border-[#e8eef6]">
                <span className="text-sm font-bold text-gray-500">Latest Quiz</span>
                <span className="text-base font-black text-[#1d348a]">{studentData.recentQuizScore}%</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-[#f8fafc] rounded-2xl border border-[#e8eef6]">
                <span className="text-sm font-bold text-gray-500">Support</span>
                <span className="text-sm font-bold text-[#10B981] bg-[#ECFDF5] px-3 py-1 rounded-lg">{studentData.supportMode}</span>
              </div>
            </div>
          </div>

          {/* 4. Recommended Next Steps */}
          <div className="bg-gradient-to-br from-[#1d348a] to-[#2d4aa0] rounded-[2rem] p-8 shadow-xl border border-transparent relative overflow-hidden" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.2)' }}>
            <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full blur-[30px] -mr-10 -mt-10 pointer-events-none"></div>

            <h2 className="text-white/60 font-bold uppercase tracking-[3px] text-xs mb-6 border-b border-white/10 pb-4 relative z-10">Recommended Next Steps</h2>

            <div className="space-y-4 relative z-10">
              <Link to="/workspace" className="w-full flex items-center gap-4 bg-white p-4 rounded-2xl hover:scale-[1.02] transition-transform shadow-lg group">
                <div className="w-12 h-12 bg-[#eef1f9] rounded-xl flex items-center justify-center text-2xl shrink-0 group-hover:rotate-12 transition-transform">
                  📖
                </div>
                <div>
                  <h3 className="font-black text-gray-800 text-sm">Review Content</h3>
                  <p className="text-xs text-gray-500 font-medium">Revisit your current lesson</p>
                </div>
              </Link>

              <Link to="/quiz" className="w-full flex items-center gap-4 bg-[#10B981] p-4 rounded-2xl hover:scale-[1.02] transition-transform shadow-lg group">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center text-2xl shrink-0">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-1 transition-transform"><polyline points="9 18 15 12 9 6" /></svg>
                </div>
                <div>
                  <h3 className="font-black text-white text-sm">Practice Quiz</h3>
                  <p className="text-xs text-white/80 font-medium">Test weak concepts</p>
                </div>
              </Link>
            </div>
          </div>

        </div>

        {/* Right Column (Topics, Weaknesses, Activity) */}
        <div className="lg:col-span-2 flex flex-col gap-6 lg:gap-8">

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
            {/* 2. Topic Progress */}
            <div className="bg-white rounded-[2rem] p-8 shadow-xl border border-white relative overflow-hidden" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
              <h2 className="text-gray-400 font-bold uppercase tracking-[3px] text-xs mb-8 border-b border-gray-100 pb-4">Topic Progress</h2>

              <div className="space-y-6">
                {topicProgress.length > 0 ? topicProgress.map(topic => (
                  <div key={topic.id}>
                    <div className="flex justify-between items-end mb-2">
                      <span className="font-bold text-gray-700 text-sm">{topic.name}</span>
                      <span className="font-black text-gray-900 text-sm">{topic.mastery}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                      <div className={`h-full bg-gradient-to-r ${topic.color} rounded-full transition-all duration-1000 ease-out`} style={{ width: `${topic.mastery}%` }}></div>
                    </div>
                  </div>
                )) : (
                  <div className="p-6 text-center bg-[#f8fafc] rounded-2xl border border-[#e8eef6]">
                    <p className="font-bold text-gray-500">Complete some lessons to see progress here.</p>
                  </div>
                )}
              </div>
            </div>

            {/* 3. Concepts to Review */}
            <div className="bg-white rounded-[2rem] p-8 shadow-xl border border-white relative overflow-hidden" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
              <h2 className="text-gray-400 font-bold uppercase tracking-[3px] text-xs mb-8 border-b border-gray-100 pb-4">Concepts to Review</h2>

              <div className="space-y-4">
                {weakConcepts.length > 0 ? (
                  weakConcepts.map(concept => (
                    <div key={concept.id} className="flex items-center gap-4 p-4 bg-[#f8fafc] rounded-2xl border border-red-100">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${concept.urgency === 'high' ? 'bg-red-100 text-red-500' : 'bg-orange-100 text-orange-500'}`}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
                      </div>
                      <div>
                        <h3 className="font-bold text-gray-800 text-sm">{concept.concept}</h3>
                        <p className="text-xs font-semibold mt-1 text-gray-500">Needs more practice</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center bg-[#ECFDF5] rounded-2xl border border-[#6EE7B7]">
                    <span className="text-3xl block mb-2">🎉</span>
                    <p className="font-bold text-[#059669]">No weak concepts detected!</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 5. Recent Learning Activity */}
          <div className="bg-white rounded-[2rem] p-8 shadow-xl border border-white relative overflow-hidden flex-1" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
            <h2 className="text-gray-400 font-bold uppercase tracking-[3px] text-xs mb-8 border-b border-gray-100 pb-4">Recent Quiz History</h2>

            <div className="space-y-0">
              {recentActivity.length > 0 ? recentActivity.map((activity, index) => (
                <div key={activity.id} className="flex gap-6 relative">
                  {index !== recentActivity.length - 1 && (
                    <div className="absolute left-[1.35rem] top-12 bottom-[-1rem] w-0.5 bg-gray-100 z-0"></div>
                  )}

                  <div className={`w-11 h-11 rounded-full flex items-center justify-center relative z-10 shrink-0 shadow-sm border-[3px] border-white ${activity.passed ? 'bg-[#ECFDF5] text-[#10B981]' : 'bg-[#FEF2F2] text-red-400'}`}>
                    {activity.passed ? (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    ) : (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    )}
                  </div>

                  <div className="pb-8 pt-2 flex-1">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <h3 className="font-black text-gray-800 text-base">{activity.title}</h3>
                      <span className={`text-xs font-black px-3 py-1 rounded-full ${activity.passed ? 'bg-[#ECFDF5] text-[#059669]' : 'bg-[#FEF2F2] text-red-600'}`}>
                        {activity.passed ? 'PASSED' : 'FAILED'}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-1.5 text-sm">
                      <span className="font-semibold text-gray-400">{activity.date}</span>
                      {activity.score !== undefined && (
                        <>
                          <span className="w-1 h-1 rounded-full bg-gray-300"></span>
                          <span className={`font-bold ${activity.passed ? 'text-[#10B981]' : 'text-red-500'}`}>
                            {activity.score}%
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )) : (
                <div className="p-6 text-center bg-[#f8fafc] rounded-2xl border border-[#e8eef6]">
                  <p className="font-bold text-gray-500">Complete a quiz to see your history here.</p>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
