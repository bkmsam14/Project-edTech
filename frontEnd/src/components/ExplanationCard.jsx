import React from 'react';
import TextToSpeech from './TextToSpeech';
import { playTextToSpeech, stopTextToSpeech } from '../services/ttsService';

export default function ExplanationCard({ supportMode, step, setStep }) {
  let explanationText = "";

  if (supportMode === 'phonological') {
    explanationText = "Photosynthesis is how plants make food. Plants need three things: sunlight, water, and carbon dioxide.";
  } else if (supportMode === 'visual') {
    explanationText = "Photosynthesis. Plants make food using sunlight. This process happens in the leaves. They breathe in carbon dioxide and release fresh oxygen.";
  } else if (supportMode === 'reading-speed') {
    if (step === 1) explanationText = 'Plants absorb sunlight through their leaves.';
    else if (step === 2) explanationText = 'They take in water from the ground.';
    else if (step === 3) explanationText = 'Together, sunlight and water create energy for the plant.';
  }

  return (
    <div className="bg-white flex-1 rounded-3xl shadow-xl flex flex-col overflow-hidden border border-white relative" style={{ boxShadow: '0 24px 80px rgba(29,52,138,0.1)' }}>

      {/* AI Panel Header - Compact */}
      <div className="p-4 lg:p-5 border-b border-gray-200 bg-white z-10">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          {/* Left side - Title and badge */}
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <h2 className="text-lg lg:text-xl font-bold text-[#1d1f2e] truncate">
              Photosynthesis
            </h2>
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-[#ECFDF5] text-[#10B981] border border-[#6EE7B7] shrink-0">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              {supportMode === 'phonological' ? 'Phonological' :
                supportMode === 'visual' ? 'Visual' : 'Reading Speed'}
            </div>
          </div>

          {/* Right side - Source and controls */}
          <div className="flex items-center gap-3">
            {/* Source Reference Tag - Compact */}
            <div className="bg-[#f8fafc] border border-[#e8eef6] px-3 py-1.5 rounded-lg flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-[#1d348a]">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
              </svg>
              <p className="font-semibold text-gray-700 text-xs">biology_notes.pdf</p>
            </div>

            {/* Text to Speech - Compact */}
            <div>
              <TextToSpeech text={explanationText} />
            </div>
          </div>
        </div>
      </div>

      {/* AI Panel Body (Dynamic based on support mode) */}
      <div className="flex-1 overflow-y-auto p-8 lg:p-14 relative bg-gradient-to-b from-white to-[#fafbfc]" style={{ scrollbarWidth: 'thin' }}>

        {/* === Phonological Mode Mock === */}
        {supportMode === 'phonological' && (
          <div className="max-w-5xl mx-auto animate-in fade-in duration-500">
            <div className="bg-gradient-to-br from-white to-[#f8fafc] p-10 lg:p-14 rounded-[2rem] shadow-lg border-2 border-gray-100 mb-8">
              <div className="flex items-center justify-between flex-wrap gap-6 mb-10 pb-8 border-b-2 border-gray-100">
                {/* Syllable Breakdown */}
                <h3 className="text-4xl lg:text-5xl font-black tracking-widest text-[#1d348a]">
                  Pho-to-<span className="text-[#F59E0B]">syn</span>-the-sis
                </h3>

                {/* Audio Pronunciation */}
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    stopTextToSpeech();
                    playTextToSpeech("Pho... to... syn... the... sis", null);
                  }}
                  className="flex items-center gap-3 px-8 py-5 bg-gradient-to-r from-[#1d348a] to-[#2d4aa0] hover:from-[#162870] hover:to-[#1d348a] text-white rounded-2xl font-bold transition-all hover:scale-105 shadow-lg shadow-[#1d348a]/30"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
                  </svg>
                  Play pronunciation
                </button>
              </div>

              <div className="space-y-8 text-[#1d1f2e]">
                <div className="bg-white p-8 rounded-2xl border-l-[6px] border-[#1d348a] shadow-sm">
                  <p className="text-3xl lg:text-4xl font-bold leading-relaxed text-gray-800">
                    Photosynthesis is how plants make food.
                  </p>
                </div>

                <div className="bg-white p-8 rounded-2xl border-l-[6px] border-[#10B981] shadow-sm">
                  <p className="text-3xl lg:text-4xl font-bold mb-6 text-gray-800">Plants need three things:</p>
                  <ul className="text-3xl lg:text-4xl font-bold space-y-6">
                    <li className="flex items-center gap-5 p-4 bg-gradient-to-r from-[#FEF3C7] to-transparent rounded-xl">
                      <span className="text-5xl">☀️</span>
                      <span className="text-gray-800">sunlight</span>
                    </li>
                    <li className="flex items-center gap-5 p-4 bg-gradient-to-r from-[#DBEAFE] to-transparent rounded-xl">
                      <span className="text-5xl">💧</span>
                      <span className="text-gray-800">water</span>
                    </li>
                    <li className="flex items-center gap-5 p-4 bg-gradient-to-r from-[#E0E7FF] to-transparent rounded-xl">
                      <span className="text-5xl">💨</span>
                      <span className="text-gray-800">carbon dioxide</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* === Visual Support Mode Mock === */}
        {supportMode === 'visual' && (
          <div className="max-w-6xl mx-auto animate-in fade-in duration-500">
            <div className="bg-gradient-to-br from-white to-[#f8fafc] p-12 lg:p-16 rounded-[2rem] shadow-lg border-2 border-gray-100 mb-8">

              {/* Visual Support Features: Large text, wide spacing, highlighted keywords */}
              <div className="mb-16 pb-10 border-b-4 border-gray-100">
                <h3 className="text-6xl lg:text-7xl font-black text-gray-900 leading-tight" style={{ letterSpacing: '2px' }}>
                  Photosynthesis
                </h3>
              </div>

              <div className="space-y-16" style={{ fontSize: '32px', lineHeight: '2.5', letterSpacing: '1px' }}>
                <div className="bg-white p-8 rounded-2xl shadow-sm border-2 border-gray-100">
                  <p className="text-gray-800">
                    <span className="bg-gradient-to-r from-[#FEF3C7] to-[#FDE68A] text-[#D97706] font-black px-5 py-3 rounded-2xl shadow-sm border-2 border-[#FCD34D]">Plants make food</span> using <span className="text-[#10B981] font-black text-4xl">sunlight</span>.
                  </p>
                </div>

                <div className="bg-white p-8 rounded-2xl shadow-sm border-2 border-gray-100">
                  <p className="text-gray-800">
                    This process happens in the <span className="bg-gradient-to-r from-[#D1FAE5] to-[#A7F3D0] text-[#059669] font-black px-5 py-3 rounded-2xl shadow-sm border-2 border-[#6EE7B7]">leaves</span>.
                  </p>
                </div>

                <div className="bg-white p-8 rounded-2xl shadow-sm border-2 border-gray-100">
                  <p className="text-gray-800">
                    They breathe in <span className="font-black underline decoration-[6px] decoration-[#1d348a] underline-offset-[12px] text-4xl">carbon dioxide</span> and release fresh <span className="bg-gradient-to-r from-[#DBEAFE] to-[#BFDBFE] text-[#2563EB] font-black px-5 py-3 rounded-2xl shadow-sm border-2 border-[#93C5FD]">oxygen</span>.
                  </p>
                </div>
              </div>

              {/* Visual Aid - Simple Diagram */}
              <div className="mt-16 p-10 bg-white rounded-3xl border-2 border-dashed border-gray-300">
                <div className="flex items-center justify-around flex-wrap gap-10">
                  <div className="text-center">
                    <div className="text-8xl mb-4">☀️</div>
                    <p className="text-2xl font-bold text-gray-700">Sunlight</p>
                  </div>
                  <div className="text-6xl text-gray-400">+</div>
                  <div className="text-center">
                    <div className="text-8xl mb-4">💧</div>
                    <p className="text-2xl font-bold text-gray-700">Water</p>
                  </div>
                  <div className="text-6xl text-gray-400">+</div>
                  <div className="text-center">
                    <div className="text-8xl mb-4">💨</div>
                    <p className="text-2xl font-bold text-gray-700">CO₂</p>
                  </div>
                  <div className="text-6xl text-gray-400">→</div>
                  <div className="text-center">
                    <div className="text-8xl mb-4">🍃</div>
                    <p className="text-2xl font-bold text-[#10B981]">Plant Food!</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* === Reading Speed Mode Mock === */}
        {supportMode === 'reading-speed' && (
          <div className="max-w-5xl mx-auto flex flex-col items-center animate-in fade-in duration-500 py-12">

            {/* Progress indicator */}
            <div className="mb-12 flex items-center gap-3">
              {[1, 2, 3].map(i => (
                <div key={i} className={`w-4 h-4 rounded-full transition-all duration-300 ${i === step ? 'bg-[#1d348a] w-12 shadow-lg shadow-[#1d348a]/30' : i < step ? 'bg-[#10B981]' : 'bg-gray-200'}`} />
              ))}
            </div>

            {/* Step container */}
            <div className="w-full relative">
              {/* Previous step indicator */}
              {step > 1 && (
                 <div className="absolute -top-20 left-0 right-0 flex justify-center opacity-30">
                   <div className="bg-white px-8 py-4 rounded-2xl shadow-sm text-gray-400 font-bold blur-[1px] scale-90 border-2 border-gray-200">
                     Step {step - 1} completed ✓
                   </div>
                 </div>
              )}

              <div className="bg-gradient-to-br from-white to-[#f8fafc] p-14 lg:p-20 rounded-[2.5rem] shadow-2xl border-4 border-[#e8eef6] text-center transform transition-all duration-500 relative z-10 w-full">
                <span className="text-[#1d348a] font-black tracking-[3px] uppercase text-base mb-8 block bg-gradient-to-r from-[#eef1f9] to-[#e8eef6] w-fit mx-auto px-6 py-3 rounded-full border-2 border-white shadow-sm">
                  Step {step} of 3
                </span>

                {/* Progressive Content */}
                <div className="bg-white p-10 rounded-3xl shadow-lg border-2 border-gray-100 mt-8">
                  <p className="text-5xl lg:text-6xl font-black text-[#1d1f2e] leading-tight" style={{ lineHeight: '1.5', letterSpacing: '1px' }}>
                    {explanationText}
                  </p>
                </div>
              </div>

              {/* Next step hint */}
              {step < 3 && (
                <div className="absolute -bottom-20 left-0 right-0 flex justify-center opacity-20">
                  <div className="bg-white px-8 py-4 rounded-2xl shadow-sm text-gray-400 font-bold scale-90 border-2 border-gray-200 blur-[1px]">
                    Step {step + 1} ready...
                  </div>
                </div>
              )}
            </div>

            {/* Next Step Action */}
            <div className="mt-20 w-full flex justify-center gap-6">
              {step < 3 ? (
                <>
                  <button
                    onClick={() => setStep(s => s + 1)}
                    className="group flex items-center gap-4 px-12 py-7 bg-gradient-to-r from-[#10B981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-white rounded-full font-black text-2xl shadow-2xl shadow-[#10B981]/40 transition-all hover:scale-110 border-2 border-white"
                  >
                    Continue Reading
                    <svg className="w-9 h-9 group-hover:translate-x-3 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
                  </button>
                  {step > 1 && (
                    <button
                      onClick={() => setStep(s => s - 1)}
                      className="group flex items-center gap-3 px-8 py-7 bg-white hover:bg-gray-50 text-gray-700 rounded-full font-bold text-xl transition-all border-2 border-gray-200 shadow-lg"
                    >
                      <svg className="w-6 h-6 group-hover:-translate-x-2 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
                      Previous
                    </button>
                  )}
                </>
              ) : (
                <div className="flex flex-col items-center gap-6">
                  <div className="bg-gradient-to-r from-[#ECFDF5] to-[#D1FAE5] px-8 py-4 rounded-2xl border-2 border-[#6EE7B7]">
                    <p className="text-2xl font-black text-[#059669]">✓ Explanation Complete!</p>
                  </div>
                  <button
                    onClick={() => setStep(1)}
                    className="group flex items-center gap-4 px-10 py-6 bg-gradient-to-r from-[#1d348a] to-[#2d4aa0] hover:from-[#162870] hover:to-[#1d348a] text-white rounded-full font-bold text-xl transition-all shadow-xl shadow-[#1d348a]/30 hover:scale-105 border-2 border-white"
                  >
                    <svg className="w-7 h-7 group-hover:-rotate-180 transition-transform duration-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
                    Restart from Beginning
                  </button>
                </div>
              )}
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
