import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Button from '../components/Button'

export default function LessonSelection() {
  const navigate = useNavigate()
  const [isHovering, setIsHovering] = useState(false)
  const [uploading, setUploading] = useState(false)

  function handleDrop(e) {
    e.preventDefault()
    setIsHovering(false)
    simulateUpload()
  }

  function simulateUpload() {
    setUploading(true)
    setTimeout(() => {
      setUploading(false)
      navigate('/workspace')
    }, 1500)
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-8 lg:p-12" style={{ background: '#efefee' }}>
      {/* Background blobs */}
      <div aria-hidden="true" className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[40rem] h-[40rem] rounded-full opacity-20" style={{ background: '#c2d1e7', filter: 'blur(120px)' }} />
        <div className="absolute -bottom-40 -right-40 w-[40rem] h-[40rem] rounded-full opacity-20" style={{ background: '#1d348a', filter: 'blur(120px)' }} />
      </div>

      {/* Wide Container */}
      <div className="relative w-full max-w-6xl">
        <div className="mb-12">
          <Link to="/home" className="inline-flex items-center gap-3 text-gray-500 hover:text-[#1d348a] font-bold text-lg transition-colors mb-8 bg-white px-6 py-3 rounded-2xl shadow-sm border border-gray-100">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5" /><polyline points="12 19 5 12 12 5" />
            </svg>
            Back to Dashboard
          </Link>
          <h1 className="text-5xl lg:text-6xl font-black text-[#1d1f2e] tracking-tight leading-tight">
            Choose a Lesson
          </h1>
          <p className="text-gray-500 mt-4 text-xl lg:text-2xl leading-relaxed max-w-3xl">
            Upload your trusted learning material so we can personalize it for you and make it easier to read.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-10">
          {/* Main Content Area: Upload Box */}
          <section className="flex-1 bg-white rounded-[2.5rem] p-10 lg:p-14 shadow-2xl" style={{ boxShadow: '0 24px 80px rgba(29,52,138,0.06)' }}>
            <h2 className="text-3xl font-black text-[#1d1f2e] mb-8">Option 1 — Upload Lesson</h2>

            <div
              onDragOver={e => { e.preventDefault(); setIsHovering(true) }}
              onDragLeave={() => setIsHovering(false)}
              onDrop={handleDrop}
              className={[
                'mt-4 flex flex-col items-center justify-center p-16 lg:p-20 text-center rounded-[2rem] border-4 border-dashed transition-all duration-300',
                isHovering ? 'border-[#1d348a] bg-[#eef1f9] scale-[1.02]' : 'border-[#c2d1e7] bg-white hover:border-[#1d348a]/50 hover:bg-[#f8fafc]'
              ].join(' ')}
            >
              <div
                className="w-28 h-28 flex items-center justify-center rounded-full mb-8 shadow-sm"
                style={{ background: isHovering ? '#1d348a' : '#e8eef6', color: isHovering ? 'white' : '#1d348a', transition: 'all 0.3s' }}
              >
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>

              <h3 className="text-2xl lg:text-3xl font-black text-[#1d1f2e] mb-4">
                Drag and drop your file here
              </h3>
              <p className="text-gray-600 mb-10 max-w-lg text-lg lg:text-xl leading-relaxed">
                or click the button below to easily browse files from your computer.
              </p>

              <div className="flex flex-wrap items-center justify-center gap-4 mb-12">
                {['PDF', 'Text', 'Lecture Notes'].map(format => (
                  <span key={format} className="px-5 py-2.5 rounded-xl text-lg font-bold border-2" style={{ borderColor: '#e8eef6', color: '#1d348a', background: '#f8fafc' }}>
                    {format}
                  </span>
                ))}
              </div>

              <input type="file" id="file-upload" className="hidden" onChange={simulateUpload} />
              <label htmlFor="file-upload">
                <Button as="span" className="pointer-events-none px-10 py-5 text-xl font-bold shadow-xl shadow-[#1d348a]/20">
                  {uploading ? 'Processing File...' : 'Browse Files'}
                </Button>
              </label>
            </div>
          </section>

          {/* Sidebar: Profile Info */}
          <aside className="lg:w-96 shrink-0 flex flex-col gap-8">
            <div className="bg-white rounded-[2.5rem] p-10 shadow-2xl" style={{ boxShadow: '0 24px 80px rgba(29,52,138,0.06)' }}>
              <div className="flex items-center gap-6 mb-8 pb-8 border-b-2 border-gray-100">
                <div className="w-20 h-20 flex items-center justify-center bg-[#1d348a] text-white rounded-3xl font-black text-3xl shadow-lg border border-white">
                  JM
                </div>
                <div>
                  <h3 className="font-black text-gray-800 text-2xl">Student Profile</h3>
                  <p className="text-lg font-bold text-gray-500 mt-1">Active Settings</p>
                </div>
              </div>

              <div className="flex flex-col gap-8">
                <div>
                  <p className="text-lg text-gray-400 font-black uppercase tracking-widest mb-3">Support Mode</p>
                  <div className="flex items-center gap-4 bg-[#f8fafc] border-2 border-[#e8eef6] p-5 rounded-2xl text-[#1d1f2e] font-black text-xl shadow-sm">
                    <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center text-[#1d348a]">
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" />
                      </svg>
                    </div>
                    Visual Support
                  </div>
                </div>

                <div>
                  <p className="text-lg text-gray-400 font-black uppercase tracking-widest mb-3">Learning Format</p>
                  <div className="flex items-center gap-4 bg-[#f8fafc] border-2 border-[#e8eef6] p-5 rounded-2xl text-[#1d1f2e] font-black text-xl shadow-sm">
                    <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center text-[#1d348a]">
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
                      </svg>
                    </div>
                    Simplified Text
                  </div>
                </div>

                <div className="mt-4 p-6 bg-[#ECFDF5] border-2 border-[#A7F3D0] rounded-2xl">
                  <p className="text-lg text-[#047857] font-bold leading-relaxed">
                    🌟 Lessons are automatically formatted for easier reading according to your preferences.
                  </p>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </main>
  )
}
