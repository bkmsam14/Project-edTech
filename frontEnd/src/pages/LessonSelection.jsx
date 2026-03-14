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
    <main className="min-h-screen flex items-center justify-center p-6 lg:p-10" style={{ background: '#efefee' }}>
      {/* Background blobs */}
      <div aria-hidden="true" className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[36rem] h-[36rem] rounded-full opacity-25" style={{ background: '#c2d1e7', filter: 'blur(100px)' }} />
        <div className="absolute -bottom-40 -right-40 w-[36rem] h-[36rem] rounded-full opacity-25" style={{ background: '#1d348a', filter: 'blur(100px)' }} />
      </div>

      {/* Wide Container */}
      <div className="relative w-full max-w-5xl">
        <div className="mb-8">
          <Link to="/" className="inline-flex items-center gap-2 text-gray-500 hover:text-[#1d348a] font-medium transition-colors mb-6">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/>
            </svg>
            Back to Dashboard
          </Link>
          <h1 className="text-4xl font-extrabold text-[#1d1f2e] tracking-tight">
            Choose a Lesson
          </h1>
          <p className="text-gray-500 mt-2 text-lg">
            Upload your trusted learning material so we can personalize it for you.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Main Content Area: Upload Box */}
          <section className="flex-1 bg-white rounded-3xl p-8 lg:p-12 shadow-xl" style={{ boxShadow: '0 20px 60px rgba(29,52,138,0.08)' }}>
            <h2 className="text-2xl font-bold text-[#1d1f2e] mb-6">Option 1 — Upload Lesson</h2>
            
            <div
              onDragOver={e => { e.preventDefault(); setIsHovering(true) }}
              onDragLeave={() => setIsHovering(false)}
              onDrop={handleDrop}
              className={[
                'mt-2 flex flex-col items-center justify-center p-12 text-center rounded-2xl border-3 border-dashed transition-all duration-300',
                isHovering ? 'border-[#1d348a] bg-[#eef1f9] scale-[1.02]' : 'border-[#c2d1e7] bg-white hover:border-[#1d348a]/50 hover:bg-[#f8fafc]'
              ].join(' ')}
            >
              <div
                className="w-20 h-20 flex items-center justify-center rounded-full mb-6"
                style={{ background: isHovering ? '#1d348a' : '#e8eef6', color: isHovering ? 'white' : '#1d348a', transition: 'all 0.3s' }}
              >
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
              </div>

              <h3 className="text-xl font-bold text-[#1d1f2e] mb-2">
                Drag and drop your file here
              </h3>
              <p className="text-gray-500 mb-8 max-w-sm text-base">
                or click the button below to browse files from your computer.
              </p>

              <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
                {['PDF', 'Text', 'Lecture Notes'].map(format => (
                  <span key={format} className="px-4 py-1.5 rounded-lg text-sm font-semibold border" style={{ borderColor: '#c2d1e7', color: '#1d348a', background: '#f8fafc' }}>
                    {format}
                  </span>
                ))}
              </div>

              <input type="file" id="file-upload" className="hidden" onChange={simulateUpload} />
              <label htmlFor="file-upload">
                <Button as="span" className="pointer-events-none px-8 py-4 text-lg">
                  {uploading ? 'Processing File...' : 'Browse Files'}
                </Button>
              </label>
            </div>
          </section>

          {/* Sidebar: Profile Info */}
          <aside className="lg:w-80 shrink-0 flex flex-col gap-6">
            <div className="bg-white rounded-3xl p-8 shadow-xl" style={{ boxShadow: '0 20px 60px rgba(29,52,138,0.08)' }}>
              <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-100">
                <div className="w-14 h-14 flex items-center justify-center bg-[#1d348a] text-white rounded-2xl font-bold text-xl shadow-md">
                  JM
                </div>
                <div>
                  <h3 className="font-bold text-gray-800 text-lg">Student Profile</h3>
                  <p className="text-sm text-gray-500">Active Settings</p>
                </div>
              </div>

              <div className="flex flex-col gap-5">
                <div>
                  <p className="text-sm text-gray-400 font-semibold uppercase tracking-wider mb-2">Support Mode</p>
                  <div className="flex items-center gap-3 bg-[#eef1f9] p-4 rounded-xl text-[#1d348a] font-semibold">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                    </svg>
                    Visual Support
                  </div>
                </div>

                <div>
                  <p className="text-sm text-gray-400 font-semibold uppercase tracking-wider mb-2">Learning Format</p>
                  <div className="flex items-center gap-3 bg-[#eef1f9] p-4 rounded-xl text-[#1d348a] font-semibold">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
                    </svg>
                    Simplified Text
                  </div>
                </div>
                
                <p className="mt-2 text-sm text-gray-500 leading-relaxed">
                  Your uploaded lessons will be automatically formatted according to these preferences.
                </p>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </main>
  )
}
