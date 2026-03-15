import React from 'react';

export default function ExplanationCard({ supportMode }) {
  const modeInfo = {
    phonological: {
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#F97316" strokeWidth="2.5">
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
          <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
          <line x1="12" y1="19" x2="12" y2="23" />
          <line x1="8" y1="23" x2="16" y2="23" />
        </svg>
      ),
      color: '#F97316',
      bgColor: '#FFF7ED',
      borderColor: '#FED7AA',
      title: 'Phonological Mode',
      description: 'Words will be broken into syllables to help with pronunciation and reading flow.'
    },
    visual: {
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#1d348a" strokeWidth="2.5">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      ),
      color: '#1d348a',
      bgColor: '#EEF1F9',
      borderColor: '#C2D1E7',
      title: 'Visual Mode',
      description: 'Enhanced spacing and visual organization for better readability.'
    },
    'reading-speed': {
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2.5">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
          <path d="M13 7h4" />
          <path d="M13 11h4" />
        </svg>
      ),
      color: '#059669',
      bgColor: '#ECFDF5',
      borderColor: '#A7F3D0',
      title: 'Reading Speed Mode',
      description: 'Key information displayed in large, easy-to-read cards.'
    }
  };

  const mode = modeInfo[supportMode] || modeInfo.visual;

  return (
    <div
      className="bg-white flex-1 rounded-[2.5rem] shadow-xl flex flex-col items-center justify-center p-12 border-2 relative overflow-hidden"
      style={{
        boxShadow: '0 24px 80px rgba(29,52,138,0.1)',
        borderColor: mode.borderColor
      }}
    >
      {/* Decorative background */}
      <div
        className="absolute top-0 right-0 w-96 h-96 rounded-full opacity-20 blur-[100px]"
        style={{ background: mode.color }}
      />
      <div
        className="absolute bottom-0 left-0 w-80 h-80 rounded-full opacity-10 blur-[80px]"
        style={{ background: mode.color }}
      />

      {/* Content */}
      <div className="relative z-10 text-center max-w-2xl">
        {/* Mode Icon */}
        <div
          className="w-24 h-24 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-lg border-2"
          style={{
            background: mode.bgColor,
            borderColor: mode.borderColor
          }}
        >
          {mode.icon}
        </div>

        {/* Mode Title */}
        <div
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-black uppercase tracking-wider mb-6 border-2"
          style={{
            background: mode.bgColor,
            color: mode.color,
            borderColor: mode.borderColor
          }}
        >
          {mode.title}
        </div>

        {/* Main Message */}
        <h2 className="text-3xl lg:text-4xl font-black text-[#1d1f2e] mb-4 leading-tight">
          Ready to Learn
        </h2>
        <p className="text-lg text-gray-500 leading-relaxed mb-8">
          {mode.description}
        </p>

        {/* Call to Action */}
        <div
          className="p-8 rounded-2xl border-2"
          style={{
            background: mode.bgColor,
            borderColor: mode.borderColor
          }}
        >
          <p className="text-gray-600 font-semibold mb-4">
            To get started:
          </p>
          <div className="space-y-3 text-left">
            <div className="flex items-center gap-3">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm shrink-0"
                style={{ background: mode.color }}
              >
                1
              </div>
              <p className="text-gray-700 font-medium">
                Use <strong>Quick Actions</strong> on the left to get AI explanations
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm shrink-0"
                style={{ background: mode.color }}
              >
                2
              </div>
              <p className="text-gray-700 font-medium">
                Type a question in the <strong>Chat</strong> section
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm shrink-0"
                style={{ background: mode.color }}
              >
                3
              </div>
              <p className="text-gray-700 font-medium">
                Upload a lesson file from the <strong>Lesson Selection</strong> page
              </p>
            </div>
          </div>
        </div>

        {/* Helper Text */}
        <p className="text-sm text-gray-400 mt-8 italic">
          Your AI responses will appear here in {mode.title.toLowerCase()} format
        </p>
      </div>
    </div>
  );
}
