import { Link } from 'react-router-dom'
import Button from '../components/Button'

export default function ProgressPage() {
  // Mock student data
  const studentData = {
    name: 'Sarah',
    supportMode: 'Visual Support',
    currentLesson: 'Photosynthesis',
    overallMastery: 78,
    recentQuizScore: 85,
    lastActive: 'Today'
  }

  const topicProgress = [
    { id: 1, name: 'Plant Biology Basics', mastery: 95, color: 'from-[#10B981] to-[#059669]' },
    { id: 2, name: 'Photosynthesis Cycle', mastery: 75, color: 'from-[#3B82F6] to-[#2563EB]' },
    { id: 3, name: 'Cellular Respiration', mastery: 40, color: 'from-[#F59E0B] to-[#D97706]' },
  ]

  const weakConcepts = [
    { id: 1, concept: 'Role of Chlorophyll', urgency: 'high' },
    { id: 2, concept: 'Energy Storage (ATP)', urgency: 'medium' },
  ]

  const recentActivity = [
    { id: 1, type: 'quiz', title: 'Photosynthesis Quiz', score: 85, date: 'Today' },
    { id: 2, type: 'lesson', title: 'Completed Lesson: Photosynthesis', date: 'Yesterday' },
    { id: 3, type: 'lesson', title: 'Completed Lesson: Plant Cells', date: '3 days ago' },
  ]

  return (
    <div className="min-h-screen bg-[#efefee] flex flex-col items-center py-6 lg:py-10 px-4 lg:px-6 font-sans">

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
                  <p className="text-xs text-gray-500 font-medium">Revisit Cellular Respiration</p>
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
                {topicProgress.map(topic => (
                  <div key={topic.id}>
                    <div className="flex justify-between items-end mb-2">
                      <span className="font-bold text-gray-700 text-sm">{topic.name}</span>
                      <span className="font-black text-gray-900 text-sm">{topic.mastery}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                      <div className={`h-full bg-gradient-to-r ${topic.color} rounded-full transition-all duration-1000 ease-out`} style={{ width: `${topic.mastery}%` }}></div>
                    </div>
                  </div>
                ))}
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
            <h2 className="text-gray-400 font-bold uppercase tracking-[3px] text-xs mb-8 border-b border-gray-100 pb-4">Recent Learning Activity</h2>

            <div className="space-y-0">
              {recentActivity.map((activity, index) => (
                <div key={activity.id} className="flex gap-6 relative">
                  {/* Timeline line */}
                  {index !== recentActivity.length - 1 && (
                    <div className="absolute left-[1.35rem] top-12 bottom-[-1rem] w-0.5 bg-gray-100 z-0"></div>
                  )}

                  <div className={`w-11 h-11 rounded-full flex items-center justify-center relative z-10 shrink-0 shadow-sm border-[3px] border-white ${activity.type === 'quiz' ? 'bg-[#FEF3C7] text-[#D97706]' : 'bg-[#eef1f9] text-[#1d348a]'}`}>
                    {activity.type === 'quiz' ? '📝' : '📖'}
                  </div>

                  <div className="pb-8 pt-2">
                    <h3 className="font-black text-gray-800 text-base">{activity.title}</h3>
                    <div className="flex items-center gap-3 mt-1.5 text-sm">
                      <span className="font-semibold text-gray-400">{activity.date}</span>
                      {activity.score && (
                        <>
                          <span className="w-1 h-1 rounded-full bg-gray-300"></span>
                          <span className="font-bold text-[#10B981]">Score: {activity.score}%</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
