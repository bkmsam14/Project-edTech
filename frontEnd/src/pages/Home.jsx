import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { connectMoodle, getMoodleCourses, selectMoodleCourse } from '../services/api';

export default function Home() {
  const navigate = useNavigate();
  const profile = JSON.parse(localStorage.getItem('eduai_profile') || '{}');
  const userId = profile.user_id || 'user_001';
  const [supportMode] = useState(profile.support_mode || 'Visual Support');

  // Moodle state
  const [showMoodleModal, setShowMoodleModal] = useState(false);
  const [moodleCookie, setMoodleCookie] = useState('');
  const [moodleConnected, setMoodleConnected] = useState(false);
  const [moodleProfile, setMoodleProfile] = useState(null);
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [moodleLoading, setMoodleLoading] = useState(false);
  const [moodleError, setMoodleError] = useState(null);
  const [ingesting, setIngesting] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('eduai_moodle');
    if (stored) {
      const data = JSON.parse(stored);
      setMoodleConnected(true);
      setMoodleProfile(data.profile);
    }
    const storedCourse = localStorage.getItem('eduai_course');
    if (storedCourse) {
      setSelectedCourse(JSON.parse(storedCourse));
    }
  }, []);

  const handleLogout = () => {
    navigate('/');
  };

  async function handleMoodleConnect() {
    if (!moodleCookie.trim()) return;
    setMoodleLoading(true);
    setMoodleError(null);
    try {
      const res = await connectMoodle({ userId, sessionCookie: moodleCookie.trim() });
      if (res.success) {
        setMoodleConnected(true);
        setMoodleProfile(res.profile);
        localStorage.setItem('eduai_moodle', JSON.stringify({
          connected: true,
          profile: res.profile,
          session_cookie: moodleCookie.trim(),
        }));
        // Fetch courses
        const coursesRes = await getMoodleCourses(userId);
        if (coursesRes.success) setCourses(coursesRes.courses);
      } else {
        setMoodleError(res.error || 'Connection failed');
      }
    } catch (err) {
      setMoodleError(err.message || 'Connection failed');
    } finally {
      setMoodleLoading(false);
    }
  }

  async function handleCourseSelect(course) {
    setIngesting(true);
    setMoodleError(null);
    try {
      const res = await selectMoodleCourse({
        userId,
        courseId: course.id,
        courseName: course.fullname,
      });
      if (res.success) {
        const courseData = {
          course_id: res.course.course_id,
          course_name: res.course.course_name,
          document_id: res.course.document_id,
        };
        setSelectedCourse(courseData);
        localStorage.setItem('eduai_course', JSON.stringify(courseData));
        if (res.grades) {
          localStorage.setItem('eduai_moodle_grades', JSON.stringify(res.grades));
        }
        setShowMoodleModal(false);
      }
    } catch (err) {
      setMoodleError(err.message || 'Failed to select course');
    } finally {
      setIngesting(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#efefee] flex flex-col items-center py-10 px-6 font-sans" style={{ fontSize: 'var(--user-font-size)' }}>
      <div className="max-w-[1400px] w-full gap-8 flex flex-col">

        {/* Top Navbar items */}
        <div className="flex justify-end mb-2">
          <button onClick={handleLogout} className="text-gray-500 hover:text-red-500 font-bold transition-colors flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-white shadow-[0_4px_12px_rgba(0,0,0,0.02)] border border-transparent hover:border-gray-200">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
            Sign Out
          </button>
        </div>

        {/* Header / Welcome Section */}
        <header className="bg-white rounded-[2.5rem] p-10 lg:p-16 shadow-xl border border-white text-center relative overflow-hidden" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
          <div className="absolute top-0 right-0 w-80 h-80 bg-[#c2d1e7] rounded-full blur-[100px] opacity-40 -mr-20 -mt-20 pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 w-80 h-80 bg-[#c2d1e7] rounded-full blur-[100px] opacity-40 -ml-20 -mb-20 pointer-events-none"></div>

          <div className="inline-flex items-center justify-center p-4 bg-[#eef1f9] rounded-2xl mb-8 relative z-10 shadow-sm border border-[#e8eef6]">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#1d348a" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
            </svg>
          </div>

          <h1 className="text-5xl lg:text-6xl font-black text-[#1d1f2e] mb-5 relative z-10 tracking-tight">
            Welcome back to <span className="text-[#1d348a]">DysLearn</span>!
          </h1>
          <p className="text-gray-500 text-xl lg:text-2xl font-medium max-w-3xl mx-auto relative z-10 leading-relaxed">
            Your personalized learning dashboard. Pick up where you left off or adjust your accessibility settings.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Main Navigation Cards (Left 2 Col) */}
          <section className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-8">

            {/* Connect to Moodle Card */}
            <button onClick={() => setShowMoodleModal(true)} className="group bg-white rounded-3xl p-10 shadow-lg border-2 border-[#e8eef6] hover:border-[#F97316]/50 hover:shadow-2xl hover:shadow-[#F97316]/10 transition-all flex flex-col h-full transform hover:-translate-y-2 relative overflow-hidden text-left">
              {selectedCourse && (
                <div className="absolute top-4 right-4 px-3 py-1.5 bg-[#10B981] text-white text-[10px] font-black uppercase rounded-lg tracking-[1px]">Connected</div>
              )}
              <div className="w-20 h-20 bg-[#FFF7ED] text-[#F97316] rounded-2xl flex items-center justify-center text-4xl mb-8 group-hover:scale-110 transition-transform shadow-inner border border-[#FED7AA]">
                🎓
              </div>
              <h2 className="text-3xl font-extrabold text-[#1d1f2e] mb-4">
                {selectedCourse ? 'Moodle Course' : 'Connect to Moodle'}
              </h2>
              <p className="text-gray-500 font-bold text-lg leading-relaxed flex-1">
                {selectedCourse
                  ? selectedCourse.course_name
                  : 'Link your MedTech Moodle account to import courses and grades.'}
              </p>
              <div className="mt-8 pt-6 flex items-center gap-3 text-[#F97316] font-black tracking-[2px] uppercase text-sm border-t border-gray-100">
                {selectedCourse ? 'Change Course' : 'Connect Now'}
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-3 transition-transform"><polyline points="9 18 15 12 9 6" /></svg>
              </div>
            </button>

            <Link to="/lessons" className="group bg-white rounded-3xl p-10 shadow-lg border-2 border-[#e8eef6] hover:border-[#1d348a]/30 hover:shadow-2xl transition-all flex flex-col h-full transform hover:-translate-y-2 relative overflow-hidden">
              <div className="w-20 h-20 bg-[#eef1f9] text-[#1d348a] rounded-2xl flex items-center justify-center text-4xl mb-8 group-hover:scale-110 transition-transform shadow-inner border border-white">
                📚
              </div>
              <h2 className="text-3xl font-extrabold text-[#1d1f2e] mb-4">Lesson Selection</h2>
              <p className="text-gray-500 font-bold text-lg leading-relaxed content-start flex-1">Browse and choose from your customized curriculum and start learning.</p>
              <div className="mt-8 pt-6 flex items-center gap-3 text-[#1d348a] font-black tracking-[2px] uppercase text-sm border-t border-gray-100">
                Go to Lessons
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-3 transition-transform"><polyline points="9 18 15 12 9 6" /></svg>
              </div>
            </Link>

            <Link to="/workspace" className="group bg-white rounded-3xl p-10 shadow-lg border-2 border-[#e8eef6] hover:border-[#10B981]/50 hover:shadow-2xl hover:shadow-[#10B981]/10 transition-all flex flex-col h-full transform hover:-translate-y-2 relative overflow-hidden">
              <div className="w-20 h-20 bg-[#ECFDF5] text-[#10B981] rounded-2xl flex items-center justify-center text-4xl mb-8 group-hover:scale-110 transition-transform shadow-inner border border-[#A7F3D0]">
                💻
              </div>
              <h2 className="text-3xl font-extrabold text-[#1d1f2e] mb-4">Learning Workspace</h2>
              <p className="text-gray-500 font-bold text-lg leading-relaxed flex-1">Dive into your current lesson with AI-assisted explanations and tools.</p>
              <div className="mt-8 pt-6 flex items-center gap-3 text-[#059669] font-black tracking-[2px] uppercase text-sm border-t border-gray-100">
                Open Workspace
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-3 transition-transform"><polyline points="9 18 15 12 9 6" /></svg>
              </div>
            </Link>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 md:contents">
              <Link to="/progress" className="group bg-white rounded-3xl p-10 shadow-lg border-2 border-[#e8eef6] hover:border-[#F59E0B]/50 hover:shadow-2xl hover:shadow-[#F59E0B]/10 transition-all flex flex-col h-full transform hover:-translate-y-2 relative overflow-hidden">
                <div className="w-20 h-20 bg-[#FEF3C7] text-[#D97706] rounded-2xl flex items-center justify-center text-4xl mb-8 group-hover:scale-110 transition-transform shadow-inner border border-[#FDE68A]">
                  📝
                </div>
                <h2 className="text-3xl font-extrabold text-[#1d1f2e] mb-4">Quizzes & Progress</h2>
                <p className="text-gray-500 font-bold text-lg leading-relaxed flex-1">Test your knowledge and track your learning milestones over time.</p>
                <div className="mt-8 pt-6 flex items-center gap-3 text-[#D97706] font-black tracking-[2px] uppercase text-sm border-t border-gray-100">
                  Check Progress
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-3 transition-transform"><polyline points="9 18 15 12 9 6" /></svg>
                </div>
              </Link>

              <Link to="/create-profile" className="group bg-gradient-to-br from-[#1d348a] to-[#2d4aa0] rounded-3xl p-10 shadow-lg border-2 border-transparent hover:shadow-2xl hover:shadow-[#1d348a]/30 transition-all flex flex-col h-full transform hover:-translate-y-2 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full blur-[30px] -mr-10 -mt-10 pointer-events-none"></div>
                <div className="w-20 h-20 bg-white/10 text-white rounded-2xl flex items-center justify-center text-4xl mb-8 group-hover:rotate-45 transition-transform backdrop-blur-sm border border-white/20">
                  ⚙️
                </div>
                <h2 className="text-3xl font-extrabold text-white mb-4">Profile Setup</h2>
                <p className="text-white/80 font-bold text-lg leading-relaxed flex-1">Adjust your learning preferences, support modes, and formats.</p>
                <div className="mt-8 pt-6 flex items-center gap-3 text-white font-black tracking-[2px] uppercase text-sm border-t border-white/20">
                  Manage Profile
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-3 transition-transform"><polyline points="9 18 15 12 9 6" /></svg>
                </div>
              </Link>
            </div>
          </section>

          {/* Sidebar Section (Right Col) */}
          <section className="flex flex-col gap-8">

            {/* Moodle Status */}
            {moodleConnected && (
              <div className="bg-white rounded-3xl p-8 shadow-lg border border-white relative overflow-hidden" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
                <h3 className="text-gray-400 font-black uppercase tracking-[3px] text-xs mb-8 block border-b border-gray-100 pb-4">Moodle Status</h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-5 bg-gradient-to-r from-[#FFF7ED] to-[#FFEDD5] p-5 rounded-2xl border border-[#FED7AA]">
                    <div className="w-14 h-14 bg-white rounded-xl shadow-sm flex items-center justify-center text-3xl border border-[#FED7AA] shrink-0">🎓</div>
                    <div>
                      <p className="text-[11px] text-[#C2410C] font-extrabold uppercase tracking-widest mb-1.5">Connected As</p>
                      <p className="font-extrabold text-[#1d1f2e] text-base">{moodleProfile?.full_name || 'Student'}</p>
                    </div>
                  </div>
                  {selectedCourse && (
                    <div className="flex items-center gap-5 bg-gradient-to-r from-[#ECFDF5] to-[#D1FAE5] p-5 rounded-2xl border border-[#6EE7B7]">
                      <div className="w-14 h-14 bg-white rounded-xl shadow-sm flex items-center justify-center text-3xl border border-[#A7F3D0] shrink-0">📖</div>
                      <div>
                        <p className="text-[11px] text-[#059669] font-extrabold uppercase tracking-widest mb-1.5">Active Course</p>
                        <p className="font-black text-[#047857] text-sm leading-tight">{selectedCourse.course_name}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Learner Profile Summary */}
            <div className="bg-white rounded-3xl p-8 shadow-lg border border-white relative overflow-hidden" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
              <h3 className="text-gray-400 font-black uppercase tracking-[3px] text-xs mb-8 block border-b border-gray-100 pb-4">Learner Profile</h3>

              <div className="space-y-4 relative z-10">
                <div className="flex items-center gap-5 bg-[#f8fafc] p-5 rounded-2xl border border-[#e8eef6]">
                  <div className="w-14 h-14 bg-white rounded-xl shadow-sm flex items-center justify-center text-3xl border border-gray-100 shrink-0">👁️</div>
                  <div>
                    <p className="text-[11px] text-gray-400 font-extrabold uppercase tracking-widest mb-1.5">Support Mode</p>
                    <p className="font-extrabold text-[#1d1f2e] text-base">{supportMode}</p>
                  </div>
                </div>

                <div className="flex items-center gap-5 bg-[#f8fafc] p-5 rounded-2xl border border-[#e8eef6]">
                  <div className="w-14 h-14 bg-white rounded-xl shadow-sm flex items-center justify-center text-3xl border border-gray-100 shrink-0">📹</div>
                  <div>
                    <p className="text-[11px] text-gray-400 font-extrabold uppercase tracking-widest mb-1.5">Pref. Format</p>
                    <p className="font-extrabold text-[#1d1f2e] text-base">Video & Visual Text</p>
                  </div>
                </div>

                <div className="flex items-center gap-5 bg-gradient-to-r from-[#ECFDF5] to-[#D1FAE5] p-5 rounded-2xl border border-[#6EE7B7]">
                  <div className="w-14 h-14 bg-white rounded-xl shadow-sm flex items-center justify-center text-3xl border border-[#A7F3D0] shrink-0">🌱</div>
                  <div>
                    <p className="text-[11px] text-[#059669] font-extrabold uppercase tracking-widest mb-1.5">Current Lesson</p>
                    <p className="font-black text-[#047857] text-base">{selectedCourse?.course_name || 'No course selected'}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Accessibility Tools Section */}
            <div className="bg-white rounded-3xl p-8 shadow-lg border border-white" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
              <h3 className="text-gray-400 font-black uppercase tracking-[3px] text-xs mb-8 block border-b border-gray-100 pb-4">Accessibility Status</h3>

              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between p-5 bg-[#f8fafc] rounded-2xl border border-[#e8eef6]">
                  <div className="flex items-center gap-4">
                    <div className="text-2xl">🎙️</div>
                    <p className="font-bold text-gray-800 text-sm">Hover Speech</p>
                  </div>
                  <span className="px-3.5 py-1.5 bg-[#10B981] text-white text-[10px] font-black uppercase rounded-lg tracking-[2px] shadow-sm">Active</span>
                </div>

                <div className="flex items-center justify-between p-5 bg-[#f8fafc] rounded-2xl border border-[#e8eef6]">
                  <div className="flex items-center gap-4">
                    <div className="text-2xl font-serif font-bold h-6 flex items-end">A<span className="text-sm">A</span></div>
                    <p className="font-bold text-gray-800 text-sm">Dyslexic Font</p>
                  </div>
                  <span className="px-3.5 py-1.5 bg-gray-200 text-gray-600 text-[10px] font-black uppercase rounded-lg tracking-[2px]">Auto</span>
                </div>

                <div className="flex items-center justify-between p-5 bg-[#f8fafc] rounded-2xl border border-[#e8eef6]">
                  <div className="flex items-center gap-4">
                    <div className="text-2xl">🐢</div>
                    <p className="font-bold text-gray-800 text-sm">Reading Speed</p>
                  </div>
                  <span className="px-3.5 py-1.5 bg-[#10B981] text-white text-[10px] font-black uppercase rounded-lg tracking-[2px] shadow-sm">Ready</span>
                </div>
              </div>
            </div>

          </section>
        </div>
      </div>

      {/* Moodle Connection Modal */}
      {showMoodleModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6" onClick={() => setShowMoodleModal(false)}>
          <div className="bg-white rounded-[2rem] p-8 lg:p-10 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-3xl font-black text-[#1d1f2e]">
                {moodleConnected && courses.length > 0 ? 'Select a Course' : 'Connect to Moodle'}
              </h2>
              <button onClick={() => setShowMoodleModal(false)} className="w-10 h-10 rounded-xl bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
              </button>
            </div>

            {/* Step 1: Connect */}
            {!moodleConnected && (
              <div>
                <div className="bg-[#FFF7ED] border-2 border-[#FED7AA] rounded-2xl p-6 mb-6">
                  <h3 className="font-black text-[#C2410C] mb-4 text-lg">How to connect:</h3>
                  <ol className="space-y-3 text-[#9A3412] font-medium">
                    <li className="flex gap-3">
                      <span className="w-7 h-7 bg-[#F97316] text-white rounded-lg flex items-center justify-center font-black text-sm shrink-0">1</span>
                      <span>Click "Open Moodle" below and log in with your MedTech account</span>
                    </li>
                    <li className="flex gap-3">
                      <span className="w-7 h-7 bg-[#F97316] text-white rounded-lg flex items-center justify-center font-black text-sm shrink-0">2</span>
                      <span>Press <strong>F12</strong>, go to <strong>Application</strong> tab, then <strong>Cookies</strong></span>
                    </li>
                    <li className="flex gap-3">
                      <span className="w-7 h-7 bg-[#F97316] text-white rounded-lg flex items-center justify-center font-black text-sm shrink-0">3</span>
                      <span>Find <strong>MoodleSession</strong> and copy its value</span>
                    </li>
                    <li className="flex gap-3">
                      <span className="w-7 h-7 bg-[#F97316] text-white rounded-lg flex items-center justify-center font-black text-sm shrink-0">4</span>
                      <span>Paste it in the field below and click Connect</span>
                    </li>
                  </ol>
                </div>

                <button
                  onClick={() => window.open('https://moodle.medtech.tn', '_blank')}
                  className="w-full p-4 rounded-2xl bg-gradient-to-r from-[#F97316] to-[#EA580C] hover:from-[#EA580C] hover:to-[#C2410C] text-white font-black text-lg transition-all shadow-lg hover:scale-[1.02] mb-6 flex items-center justify-center gap-3"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                  Open Moodle
                </button>

                <div className="mb-6">
                  <label className="block text-sm font-black text-gray-500 uppercase tracking-widest mb-3">MoodleSession Cookie</label>
                  <input
                    type="text"
                    value={moodleCookie}
                    onChange={e => setMoodleCookie(e.target.value)}
                    placeholder="Paste your MoodleSession cookie value here..."
                    className="w-full p-4 rounded-2xl border-2 border-[#e8eef6] focus:border-[#F97316] focus:ring-4 focus:ring-[#FED7AA] outline-none transition-all text-gray-800 font-medium text-sm"
                  />
                </div>

                {moodleError && (
                  <div className="mb-6 p-4 bg-red-50 border-2 border-red-200 text-red-700 rounded-xl font-bold text-sm">{moodleError}</div>
                )}

                <button
                  onClick={handleMoodleConnect}
                  disabled={moodleLoading || !moodleCookie.trim()}
                  className="w-full p-4 rounded-2xl bg-[#1d348a] hover:bg-[#2d4aa0] text-white font-black text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {moodleLoading ? 'Connecting...' : 'Connect'}
                </button>
              </div>
            )}

            {/* Step 2: Course Selection */}
            {moodleConnected && courses.length > 0 && (
              <div>
                {moodleProfile && (
                  <div className="flex items-center gap-4 p-5 bg-[#ECFDF5] border-2 border-[#A7F3D0] rounded-2xl mb-6">
                    <div className="w-12 h-12 bg-[#10B981] text-white rounded-xl flex items-center justify-center font-black text-xl">
                      {moodleProfile.full_name?.charAt(0) || 'M'}
                    </div>
                    <div>
                      <p className="font-black text-[#047857]">{moodleProfile.full_name}</p>
                      <p className="text-sm text-[#059669]">{moodleProfile.email}</p>
                    </div>
                  </div>
                )}

                <p className="text-gray-500 font-bold mb-4">Select a course to load its content:</p>

                {moodleError && (
                  <div className="mb-4 p-4 bg-red-50 border-2 border-red-200 text-red-700 rounded-xl font-bold text-sm">{moodleError}</div>
                )}

                <div className="space-y-3 max-h-[400px] overflow-y-auto">
                  {courses.map(course => (
                    <button
                      key={course.id}
                      onClick={() => handleCourseSelect(course)}
                      disabled={ingesting}
                      className={`w-full text-left p-5 rounded-2xl border-2 transition-all flex items-center gap-4 ${
                        selectedCourse?.course_id === course.id
                          ? 'border-[#10B981] bg-[#ECFDF5]'
                          : 'border-[#e8eef6] hover:border-[#F97316]/50 hover:bg-[#FFF7ED]'
                      } disabled:opacity-50`}
                    >
                      <div className="w-12 h-12 bg-[#eef1f9] text-[#1d348a] rounded-xl flex items-center justify-center font-black text-lg shrink-0">
                        📖
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-[#1d1f2e] text-sm leading-tight truncate">{course.fullname}</p>
                        {course.grade && (
                          <p className="text-xs text-gray-500 mt-1">Grade: {course.grade}</p>
                        )}
                      </div>
                      {selectedCourse?.course_id === course.id && (
                        <span className="px-3 py-1 bg-[#10B981] text-white text-[10px] font-black uppercase rounded-lg shrink-0">Active</span>
                      )}
                    </button>
                  ))}
                </div>

                {ingesting && (
                  <div className="mt-6 p-5 bg-[#eef1f9] rounded-2xl flex items-center gap-4">
                    <div className="animate-spin w-8 h-8 border-4 border-[#c2d1e7] border-t-[#1d348a] rounded-full shrink-0"></div>
                    <div>
                      <p className="font-bold text-[#1d348a]">Loading course content...</p>
                      <p className="text-sm text-gray-500">Fetching grades and indexing course materials for AI</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Connected but no courses fetched yet */}
            {moodleConnected && courses.length === 0 && !moodleLoading && (
              <div className="text-center py-8">
                <p className="text-gray-500 font-bold mb-4">Connected! Fetching your courses...</p>
                <button
                  onClick={async () => {
                    setMoodleLoading(true);
                    try {
                      const res = await getMoodleCourses(userId);
                      if (res.success) setCourses(res.courses);
                    } finally {
                      setMoodleLoading(false);
                    }
                  }}
                  className="px-6 py-3 bg-[#1d348a] text-white rounded-2xl font-bold"
                >
                  {moodleLoading ? 'Loading...' : 'Refresh Courses'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
