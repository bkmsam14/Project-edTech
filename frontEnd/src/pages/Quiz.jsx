import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Button from '../components/Button'

export default function Quiz() {
  const navigate = useNavigate()
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [showHint, setShowHint] = useState(false)
  const [hintLevel, setHintLevel] = useState(0)
  const [answeredQuestions, setAnsweredQuestions] = useState([])
  const [showFeedback, setShowFeedback] = useState(false)

  // Mock quiz data - in real app, this would come from backend based on uploaded course
  const quizData = {
    title: "Photosynthesis Quiz",
    course: "biology_notes.pdf",
    questions: [
      {
        id: 1,
        question: "What is the main purpose of photosynthesis?",
        options: [
          "To make plants grow taller",
          "To create food/energy for the plant",
          "To make flowers bloom",
          "To produce carbon dioxide"
        ],
        correctAnswer: 1,
        hints: [
          "Think about what plants need to survive and grow...",
          "Plants need energy just like humans need food for energy...",
          "The word 'synthesis' means to make or create something..."
        ],
        explanation: "Photosynthesis is how plants make their own food (glucose) using sunlight, water, and carbon dioxide. This food gives them energy to grow and survive!"
      },
      {
        id: 2,
        question: "Which THREE things do plants need for photosynthesis?",
        options: [
          "Sunlight, water, carbon dioxide",
          "Sunlight, soil, oxygen",
          "Water, fertilizer, shade",
          "Rain, wind, darkness"
        ],
        correctAnswer: 0,
        hints: [
          "Think about what you learned in the lesson...",
          "One comes from the sky, one from the ground, and one from the air...",
          "Remember the three items with emojis: ☀️💧💨"
        ],
        explanation: "Plants need sunlight (☀️), water (💧), and carbon dioxide (💨) to make food through photosynthesis. These three ingredients combine to create glucose and oxygen!"
      },
      {
        id: 3,
        question: "Where does photosynthesis happen in a plant?",
        options: [
          "In the roots",
          "In the leaves",
          "In the stem",
          "In the flowers"
        ],
        correctAnswer: 1,
        hints: [
          "Think about which part of the plant is green and faces the sun...",
          "This part contains something called chlorophyll...",
          "It's the part that's usually flat and wide to catch sunlight..."
        ],
        explanation: "Photosynthesis happens in the leaves! Leaves contain chlorophyll (which makes them green) and are designed to capture sunlight efficiently."
      }
    ]
  }

  const currentQ = quizData.questions[currentQuestion]
  const isLastQuestion = currentQuestion === quizData.questions.length - 1
  const progress = ((currentQuestion) / quizData.questions.length) * 100

  const handleAnswerSelect = (answerIndex) => {
    if (showFeedback) return // Prevent changing answer after submission
    setSelectedAnswer(answerIndex)
  }

  const handleSubmitAnswer = () => {
    if (selectedAnswer === null) return

    setShowFeedback(true)

    const isCorrect = selectedAnswer === currentQ.correctAnswer
    setAnsweredQuestions([...answeredQuestions, {
      questionId: currentQ.id,
      selectedAnswer,
      isCorrect,
      hintsUsed: hintLevel
    }])
  }

  const handleNextQuestion = () => {
    if (isLastQuestion) {
      // Navigate to results page
      navigate('/quiz-results')
    } else {
      setCurrentQuestion(currentQuestion + 1)
      setSelectedAnswer(null)
      setShowHint(false)
      setHintLevel(0)
      setShowFeedback(false)
    }
  }

  const handleGetHint = () => {
    if (hintLevel < currentQ.hints.length) {
      setShowHint(true)
      setHintLevel(hintLevel + 1)
    }
  }

  const isCorrect = selectedAnswer === currentQ.correctAnswer
  const score = answeredQuestions.filter(q => q.isCorrect).length

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#efefee' }}>
      {/* Header */}
      <header className="bg-white px-6 lg:px-10 py-4 shadow-sm flex items-center justify-between border-b border-[#e8eef6] sticky top-0 z-20">
        <div className="flex items-center gap-6">
          <Link to="/workspace" className="text-gray-500 hover:text-[#1d348a] font-medium flex items-center gap-2 transition-colors">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5" /><polyline points="12 19 5 12 12 5" />
            </svg>
            Back to Workspace
          </Link>
          <div className="h-6 w-px bg-gray-200 hidden sm:block"></div>
          <div className="flex items-center gap-3">
            <div className="bg-[#1d348a] text-white p-2 rounded-xl">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
            </div>
            <div>
              <h1 className="font-extrabold text-[#1d1f2e] text-xl tracking-tight">{quizData.title}</h1>
              <p className="text-xs text-gray-500 font-medium">Based on: {quizData.course}</p>
            </div>
          </div>
        </div>

        {/* Score */}
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-xs text-gray-500 font-semibold">SCORE</p>
            <p className="text-2xl font-black text-[#1d348a]">{score}/{quizData.questions.length}</p>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="bg-white border-b border-gray-200">
        <div className="h-2 bg-gray-100">
          <div
            className="h-full bg-gradient-to-r from-[#1d348a] to-[#10B981] transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Decorative background blobs */}
      <div aria-hidden="true" className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-40 left-10 w-[25rem] h-[25rem] rounded-full opacity-20" style={{ background: '#10B981', filter: 'blur(100px)' }} />
        <div className="absolute bottom-20 right-10 w-[30rem] h-[30rem] rounded-full opacity-20" style={{ background: '#1d348a', filter: 'blur(120px)' }} />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[35rem] h-[35rem] rounded-full opacity-10" style={{ background: '#F59E0B', filter: 'blur(150px)' }} />
      </div>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-6 lg:p-10 relative z-10">
        <div className="w-full max-w-4xl">

          {/* Question Card */}
          <div className="bg-white rounded-3xl shadow-2xl border-2 border-gray-100 overflow-hidden mb-6">

            {/* Question Header */}
            <div className="bg-gradient-to-br from-[#1d348a] to-[#2d4aa0] p-8 lg:p-10">
              <div className="flex items-center justify-between mb-4">
                <span className="bg-white/20 text-white px-4 py-2 rounded-full text-sm font-bold backdrop-blur-sm">
                  Question {currentQuestion + 1} of {quizData.questions.length}
                </span>
                {answeredQuestions.length > 0 && (
                  <div className="flex items-center gap-2">
                    {answeredQuestions.map((q, idx) => (
                      <div
                        key={idx}
                        className={`w-3 h-3 rounded-full ${q.isCorrect ? 'bg-[#10B981]' : 'bg-red-400'}`}
                      />
                    ))}
                    {Array.from({ length: quizData.questions.length - answeredQuestions.length }).map((_, idx) => (
                      <div key={`pending-${idx}`} className="w-3 h-3 rounded-full bg-white/30" />
                    ))}
                  </div>
                )}
              </div>

              <h2 className="text-3xl lg:text-4xl font-black text-white leading-tight">
                {currentQ.question}
              </h2>
            </div>

            {/* Answer Options */}
            <div className="p-8 lg:p-10 space-y-4">
              {currentQ.options.map((option, index) => {
                const isSelected = selectedAnswer === index
                const isCorrectOption = index === currentQ.correctAnswer

                let borderColor = 'border-gray-200'
                let bgColor = 'bg-white hover:bg-[#f8fafc]'

                if (showFeedback) {
                  if (isCorrectOption) {
                    borderColor = 'border-[#10B981]'
                    bgColor = 'bg-[#ECFDF5]'
                  } else if (isSelected && !isCorrect) {
                    borderColor = 'border-red-400'
                    bgColor = 'bg-red-50'
                  }
                } else if (isSelected) {
                  borderColor = 'border-[#1d348a]'
                  bgColor = 'bg-[#eef1f9]'
                }

                return (
                  <button
                    key={index}
                    onClick={() => handleAnswerSelect(index)}
                    disabled={showFeedback}
                    className={`w-full text-left p-6 rounded-2xl border-2 ${borderColor} ${bgColor} transition-all flex items-center gap-4 group ${!showFeedback && 'hover:border-[#1d348a]/50 cursor-pointer'}`}
                  >
                    <div className={`w-12 h-12 rounded-full border-2 flex items-center justify-center font-bold text-lg shrink-0 ${
                      showFeedback && isCorrectOption
                        ? 'bg-[#10B981] border-[#10B981] text-white'
                        : showFeedback && isSelected && !isCorrect
                        ? 'bg-red-400 border-red-400 text-white'
                        : isSelected
                        ? 'bg-[#1d348a] border-[#1d348a] text-white'
                        : 'bg-gray-100 border-gray-200 text-gray-600'
                    }`}>
                      {String.fromCharCode(65 + index)}
                    </div>
                    <p className="text-xl lg:text-2xl font-bold text-gray-800 flex-1">
                      {option}
                    </p>
                    {showFeedback && isCorrectOption && (
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-[#10B981]">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                    )}
                    {showFeedback && isSelected && !isCorrect && (
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-red-400">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    )}
                  </button>
                )
              })}
            </div>

            {/* Feedback Section */}
            {showFeedback && (
              <div className={`mx-8 lg:mx-10 mb-8 lg:mb-10 p-6 rounded-2xl border-2 ${
                isCorrect
                  ? 'bg-[#ECFDF5] border-[#10B981]'
                  : 'bg-[#FEF2F2] border-red-300'
              }`}>
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 ${
                    isCorrect ? 'bg-[#10B981]' : 'bg-red-400'
                  }`}>
                    {isCorrect ? (
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                    ) : (
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className={`text-xl font-black mb-2 ${isCorrect ? 'text-[#059669]' : 'text-red-600'}`}>
                      {isCorrect ? '✓ Correct!' : '✗ Not quite right'}
                    </h3>
                    <p className="text-lg text-gray-700 leading-relaxed">
                      {currentQ.explanation}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">

            {/* Hint Button */}
            {!showFeedback && (
              <button
                onClick={handleGetHint}
                disabled={hintLevel >= currentQ.hints.length}
                className={`flex items-center gap-3 px-6 py-4 rounded-2xl font-bold transition-all ${
                  hintLevel >= currentQ.hints.length
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-[#F59E0B] hover:bg-[#D97706] text-white shadow-lg hover:scale-105'
                }`}
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                {hintLevel === 0 ? 'Need a Hint?' : hintLevel >= currentQ.hints.length ? 'No More Hints' : `Get Another Hint (${hintLevel}/${currentQ.hints.length})`}
              </button>
            )}

            {!showFeedback ? (
              <button
                onClick={handleSubmitAnswer}
                disabled={selectedAnswer === null}
                className={`px-10 py-4 rounded-2xl font-black text-xl transition-all ${
                  selectedAnswer === null
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-[#1d348a] to-[#2d4aa0] hover:from-[#162870] hover:to-[#1d348a] text-white shadow-xl hover:scale-105'
                }`}
              >
                Check Answer
              </button>
            ) : (
              <button
                onClick={handleNextQuestion}
                className="px-10 py-4 bg-gradient-to-r from-[#10B981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-white rounded-2xl font-black text-xl shadow-xl hover:scale-105 transition-all flex items-center gap-3"
              >
                {isLastQuestion ? 'Finish Quiz' : 'Next Question'}
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </button>
            )}
          </div>

          {/* Hint Display */}
          {showHint && hintLevel > 0 && !showFeedback && (
            <div className="mt-6 bg-gradient-to-r from-[#FEF3C7] to-[#FDE68A] p-6 rounded-2xl border-2 border-[#FCD34D] animate-in fade-in duration-300">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-[#F59E0B] rounded-full flex items-center justify-center shrink-0">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2v20M2 12h20"/>
                  </svg>
                </div>
                <div className="flex-1">
                  <h4 className="font-black text-[#D97706] mb-2 text-lg">Hint {hintLevel}:</h4>
                  <p className="text-lg text-gray-800 leading-relaxed font-medium">
                    {currentQ.hints[hintLevel - 1]}
                  </p>
                </div>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  )
}
