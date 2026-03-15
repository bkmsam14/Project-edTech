import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function Home() {
  const [supportMode] = useState('Visual Support'); // Typically fetched from global context/profile
  const navigate = useNavigate();

  const handleLogout = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#efefee] flex flex-col items-center py-10 px-6 font-sans">
      <div className="max-w-[1400px] w-full gap-8 flex flex-col">
        
        {/* Top Navbar items */}
        <div className="flex justify-end mb-2">
          <button onClick={handleLogout} className="text-gray-500 hover:text-red-500 font-bold transition-colors flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-white shadow-[0_4px_12px_rgba(0,0,0,0.02)] border border-transparent hover:border-gray-200">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
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
            
            <Link to="/lessons" className="group bg-white rounded-3xl p-10 shadow-lg border-2 border-[#e8eef6] hover:border-[#1d348a]/30 hover:shadow-2xl transition-all flex flex-col h-full transform hover:-translate-y-2 relative overflow-hidden">
              <div className="w-20 h-20 bg-[#eef1f9] text-[#1d348a] rounded-2xl flex items-center justify-center text-4xl mb-8 group-hover:scale-110 transition-transform shadow-inner border border-white">
                📚
              </div>
              <h2 className="text-3xl font-extrabold text-[#1d1f2e] mb-4">Lesson Selection</h2>
              <p className="text-gray-500 font-bold text-lg leading-relaxed content-start flex-1">Browse and choose from your customized curriculum and start learning.</p>
              <div className="mt-8 pt-6 flex items-center gap-3 text-[#1d348a] font-black tracking-[2px] uppercase text-sm border-t border-gray-100">
                Go to Lessons
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-3 transition-transform"><polyline points="9 18 15 12 9 6"/></svg>
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
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-3 transition-transform"><polyline points="9 18 15 12 9 6"/></svg>
              </div>
            </Link>

            <Link to="/quiz" className="group bg-white rounded-3xl p-10 shadow-lg border-2 border-[#e8eef6] hover:border-[#F59E0B]/50 hover:shadow-2xl hover:shadow-[#F59E0B]/10 transition-all flex flex-col h-full transform hover:-translate-y-2 relative overflow-hidden">
              <div className="w-20 h-20 bg-[#FEF3C7] text-[#D97706] rounded-2xl flex items-center justify-center text-4xl mb-8 group-hover:scale-110 transition-transform shadow-inner border border-[#FDE68A]">
                📝
              </div>
              <h2 className="text-3xl font-extrabold text-[#1d1f2e] mb-4">Quizzes & Progress</h2>
              <p className="text-gray-500 font-bold text-lg leading-relaxed flex-1">Test your knowledge and track your learning milestones over time.</p>
              <div className="mt-8 pt-6 flex items-center gap-3 text-[#D97706] font-black tracking-[2px] uppercase text-sm border-t border-gray-100">
                Check Progress
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-3 transition-transform"><polyline points="9 18 15 12 9 6"/></svg>
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
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-3 transition-transform"><polyline points="9 18 15 12 9 6"/></svg>
              </div>
            </Link>
          </section>

          {/* Sidebar Section (Right Col) */}
          <section className="flex flex-col gap-8">
            
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
                    <p className="font-black text-[#047857] text-base">Photosynthesis</p>
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
    </div>
  );
}
