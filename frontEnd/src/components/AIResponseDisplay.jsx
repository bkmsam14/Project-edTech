import { useState } from 'react'
import TextToSpeech from './TextToSpeech'

// Clean up common AI response prefixes
function cleanAIResponse(text) {
  if (!text) return text

  // Remove common AI pleasantries and prefixes
  const prefixPatterns = [
    /^Sure,?\s*let me\s*/i,
    /^Let me\s*/i,
    /^I'll\s*/i,
    /^I will\s*/i,
    /^I'd be happy to\s*/i,
    /^Of course,?\s*/i,
    /^Certainly,?\s*/i,
    /^Absolutely,?\s*/i,
    /^Sure,?\s*/i,
  ]

  let cleaned = text.trim()

  for (const pattern of prefixPatterns) {
    cleaned = cleaned.replace(pattern, '')
  }

  // Capitalize first letter after cleanup
  if (cleaned.length > 0) {
    cleaned = cleaned.charAt(0).toUpperCase() + cleaned.slice(1)
  }

  return cleaned
}

// Extract key points from text (simple implementation)
function extractKeyPoints(text) {
  if (!text) return []

  // Split by common sentence endings and filter for substantial sentences
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 20)

  // Take first 3-5 most important sentences (heuristic: longer sentences often contain more info)
  const scored = sentences.map(s => ({ text: s.trim(), score: s.trim().length }))
  scored.sort((a, b) => b.score - a.score)

  return scored.slice(0, Math.min(5, scored.length)).map(s => s.text)
}

// Break text into syllables (simple approximation)
function syllabify(word) {
  if (!word || word.length < 3) return [word]

  // Simple syllable splitting based on vowels (basic heuristic)
  const vowels = 'aeiouAEIOU'
  const parts = []
  let current = ''

  for (let i = 0; i < word.length; i++) {
    current += word[i]
    if (vowels.includes(word[i]) && i < word.length - 1 && !vowels.includes(word[i + 1])) {
      // Found vowel followed by consonant - potential syllable break
      if (i < word.length - 2) {
        current += word[i + 1]
        parts.push(current)
        current = ''
        i++
      }
    }
  }

  if (current) parts.push(current)
  return parts.length > 0 ? parts : [word]
}

function PhonologicalView({ text }) {
  const words = text.split(/\s+/)

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-[#FFF7ED] to-[#FFEDD5] border-2 border-[#FED7AA] rounded-3xl p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-sm">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F97316" strokeWidth="2.5">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            </svg>
          </div>
          <h3 className="font-black text-[#C2410C] text-lg">Phonological View</h3>
        </div>
        <p className="text-sm text-[#9A3412] mb-6 leading-relaxed">
          Words are broken into syllables to help with pronunciation and reading flow.
        </p>

        <div className="bg-white rounded-2xl p-6 leading-loose" style={{ fontSize: 'calc(var(--user-font-size) * 1.1)' }}>
          {words.map((word, idx) => {
            const syllables = syllabify(word)
            return (
              <span key={idx} className="inline-block mr-3 mb-3">
                {syllables.map((syl, i) => (
                  <span key={i} className="inline-block">
                    <span className="px-1.5 py-0.5 bg-[#FFF7ED] border border-[#FED7AA] rounded-lg font-medium text-[#C2410C] mr-0.5">
                      {syl}
                    </span>
                    {i < syllables.length - 1 && <span className="text-[#F97316] mx-0.5">·</span>}
                  </span>
                ))}
              </span>
            )
          })}
        </div>
      </div>

      <div className="bg-white rounded-2xl p-6 border border-[#e8eef6]">
        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Full Text</h4>
        <p className="text-gray-700 leading-relaxed" style={{ fontSize: 'var(--user-font-size)', lineHeight: 1.8 }}>
          {text}
        </p>
      </div>
    </div>
  )
}

function VisualView({ text }) {
  // Split into paragraphs
  const paragraphs = text.split('\n').filter(p => p.trim())

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-[#EEF1F9] to-[#E0E7F7] border-2 border-[#C2D1E7] rounded-3xl p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-sm">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1d348a" strokeWidth="2.5">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </div>
          <h3 className="font-black text-[#1d348a] text-lg">Visual Mode</h3>
        </div>
        <p className="text-sm text-[#162870] mb-6 leading-relaxed">
          Enhanced spacing and visual organization for better readability.
        </p>

        <div className="space-y-8">
          {paragraphs.map((para, idx) => (
            <div key={idx} className="bg-white rounded-2xl p-8 shadow-sm border border-[#e8eef6]">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-[#1d348a] text-white rounded-xl flex items-center justify-center font-black text-lg shrink-0">
                  {idx + 1}
                </div>
                <p
                  className="text-gray-800 flex-1 font-medium"
                  style={{
                    fontSize: 'calc(var(--user-font-size) * 1.15)',
                    lineHeight: 2.2,
                    letterSpacing: '0.02em',
                    wordSpacing: '0.15em'
                  }}
                >
                  {para}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ReadingSpeedView({ text }) {
  const keyPoints = extractKeyPoints(text)

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-[#ECFDF5] to-[#D1FAE5] border-2 border-[#A7F3D0] rounded-3xl p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-sm">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2.5">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
              <polyline points="8 7 8 13 12 13" />
            </svg>
          </div>
          <h3 className="font-black text-[#059669] text-lg">Reading Speed Mode</h3>
        </div>
        <p className="text-sm text-[#047857] mb-6 leading-relaxed">
          Key information displayed in large, easy-to-read cards to help you grasp the main points quickly.
        </p>

        <div className="space-y-6">
          {keyPoints.length > 0 ? keyPoints.map((point, idx) => (
            <div
              key={idx}
              className="bg-white rounded-3xl p-10 shadow-lg border-2 border-[#6EE7B7] hover:scale-[1.02] transition-transform"
            >
              <div className="flex items-start gap-6">
                <div className="w-16 h-16 bg-gradient-to-br from-[#10B981] to-[#059669] text-white rounded-2xl flex items-center justify-center font-black text-2xl shrink-0 shadow-lg">
                  {idx + 1}
                </div>
                <p
                  className="text-gray-900 flex-1 font-bold leading-relaxed"
                  style={{
                    fontSize: 'calc(var(--user-font-size) * 1.5)',
                    lineHeight: 1.6,
                    letterSpacing: '0.02em'
                  }}
                >
                  {point}
                </p>
              </div>
            </div>
          )) : (
            <div className="bg-white rounded-3xl p-10 shadow-lg">
              <p
                className="text-gray-900 font-bold leading-relaxed"
                style={{
                  fontSize: 'calc(var(--user-font-size) * 1.5)',
                  lineHeight: 1.6,
                  letterSpacing: '0.02em'
                }}
              >
                {text}
              </p>
            </div>
          )}
        </div>
      </div>

      {keyPoints.length > 0 && (
        <details className="bg-white rounded-2xl p-6 border border-[#e8eef6]">
          <summary className="text-sm font-bold text-gray-500 uppercase tracking-widest cursor-pointer hover:text-gray-700 transition-colors">
            View Full Text
          </summary>
          <p className="text-gray-700 leading-relaxed mt-4" style={{ fontSize: 'var(--user-font-size)', lineHeight: 1.8 }}>
            {text}
          </p>
        </details>
      )}
    </div>
  )
}

export default function AIResponseDisplay({ response, supportMode }) {
  const [activeTab, setActiveTab] = useState('main')

  // Get the main text content to display and clean it
  const rawText = response.explanation || response.adapted_text || response.answer || ''
  const mainText = cleanAIResponse(rawText)
  const hasMultipleSections = response.explanation && response.adapted_text

  if (!mainText) {
    return (
      <div className="bg-white rounded-[2.5rem] p-8 shadow-lg">
        <div className="text-gray-500">
          <p>Response received but no content was generated.</p>
          <pre className="mt-4 text-xs bg-gray-50 p-4 rounded-xl overflow-auto">
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-[2.5rem] p-6 lg:p-8 shadow-lg overflow-y-auto" style={{ boxShadow: '0 12px 40px rgba(29,52,138,0.06)' }}>
      {/* Header with TTS */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-[#e8eef6]">
        <h2 className="text-2xl font-black text-[#1d1f2e] tracking-tight">AI Response</h2>
        <TextToSpeech text={mainText} />
      </div>

      {/* Tabs if multiple sections */}
      {hasMultipleSections && (
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('main')}
            className={`px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${
              activeTab === 'main'
                ? 'bg-[#1d348a] text-white shadow-md'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Explanation
          </button>
          <button
            onClick={() => setActiveTab('adapted')}
            className={`px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${
              activeTab === 'adapted'
                ? 'bg-[#1d348a] text-white shadow-md'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Adapted Content
          </button>
        </div>
      )}

      {/* Render based on support mode */}
      <div className="mt-4">
        {activeTab === 'main' && (
          <>
            {supportMode === 'phonological' ? (
              <PhonologicalView text={cleanAIResponse(response.explanation || rawText)} />
            ) : supportMode === 'visual' ? (
              <VisualView text={cleanAIResponse(response.explanation || rawText)} />
            ) : supportMode === 'reading-speed' ? (
              <ReadingSpeedView text={cleanAIResponse(response.explanation || rawText)} />
            ) : (
              // Fallback to visual view for any other mode
              <VisualView text={cleanAIResponse(response.explanation || rawText)} />
            )}
          </>
        )}

        {activeTab === 'adapted' && response.adapted_text && (
          <>
            {supportMode === 'phonological' ? (
              <PhonologicalView text={cleanAIResponse(response.adapted_text)} />
            ) : supportMode === 'visual' ? (
              <VisualView text={cleanAIResponse(response.adapted_text)} />
            ) : supportMode === 'reading-speed' ? (
              <ReadingSpeedView text={cleanAIResponse(response.adapted_text)} />
            ) : (
              // Fallback to visual view for any other mode
              <VisualView text={cleanAIResponse(response.adapted_text)} />
            )}
          </>
        )}
      </div>

      {/* Metadata footer */}
      {response.workflow_steps_executed?.length > 0 && (
        <div className="mt-8 pt-4 border-t border-[#e8eef6]">
          <p className="text-xs text-gray-400">
            Pipeline: {response.workflow_steps_executed.join(' → ')}
          </p>
        </div>
      )}
    </div>
  )
}
