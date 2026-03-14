import React from 'react';
import TextToSpeech from './TextToSpeech';

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
      
      {/* AI Panel Header */}
      <div className="p-8 lg:p-10 border-b border-gray-100 bg-white z-10 flex flex-col md:flex-row md:items-start justify-between gap-6">
        <div>
          <h2 className="text-3xl font-extrabold text-[#1d1f2e] mb-3 leading-tight">
            Photosynthesis — Personalized Explanation
          </h2>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold bg-[#ECFDF5] text-[#10B981] border border-[#6EE7B7]">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            Adapted for: {
              supportMode === 'phonological' ? 'Phonological Support' :
              supportMode === 'visual' ? 'Visual Support' : 'Reading Speed Support'
            }
          </div>
          
          <div className="mt-6">
            <TextToSpeech text={explanationText} />
          </div>
        </div>

        {/* Source Reference Tag */}
        <div className="bg-[#f8fafc] border border-[#e8eef6] p-4 rounded-2xl flex items-center gap-3 shrink-0">
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-[#1d348a] shadow-sm">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <div>
            <p className="text-xs text-gray-500 font-semibold mb-0.5">BASED ON TRUSTED SOURCE</p>
            <p className="font-bold text-gray-800 text-sm">Photosynthesis Lesson PDF</p>
          </div>
        </div>
      </div>

      {/* AI Panel Body (Dynamic based on support mode) */}
      <div className="flex-1 overflow-y-auto p-8 lg:p-12 relative" style={{ background: '#fafbfc' }}>
        
        {/* === Phonological Mode Mock === */}
        {supportMode === 'phonological' && (
          <div className="max-w-3xl animate-in fade-in duration-500">
            <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 mb-8">
              <div className="flex items-center justify-between flex-wrap gap-4 mb-8">
                {/* Syllable Breakdown */}
                <h3 className="text-4xl font-extrabold tracking-widest text-[#1d348a]">
                  Pho-to-<span className="text-[#F59E0B]">syn</span>-the-sis
                </h3>
                
                {/* Audio Pronunciation (Visual mock inside content) */}
                <button className="flex items-center gap-3 px-6 py-4 bg-[#1d348a] hover:bg-[#162870] text-white rounded-2xl font-bold transition-transform hover:-translate-y-1 shadow-lg shadow-[#1d348a]/30">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
                  </svg>
                  Play pronunciation
                </button>
              </div>

              <div className="space-y-6 text-[#1d1f2e]">
                <p className="text-2xl font-medium leading-relaxed bg-[#f8fafc] p-6 rounded-2xl border-l-4 border-[#1d348a]">
                  Photosynthesis is how plants make food.
                </p>
                
                <div className="bg-[#f8fafc] p-6 rounded-2xl border-l-4 border-[#10B981]">
                  <p className="text-2xl font-medium mb-4">Plants need three things:</p>
                  <ul className="text-2xl font-medium space-y-4 pl-4">
                    <li className="flex items-center gap-3"><span className="text-3xl">☀️</span> sunlight</li>
                    <li className="flex items-center gap-3"><span className="text-3xl">💧</span> water</li>
                    <li className="flex items-center gap-3"><span className="text-3xl">💨</span> carbon dioxide</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* === Visual Support Mode Mock === */}
        {supportMode === 'visual' && (
          <div className="max-w-4xl animate-in fade-in duration-500">
            <div className="bg-white p-8 lg:p-12 rounded-3xl shadow-sm border border-gray-100 mb-8">
              
              {/* Visual Support Features: Large text, wide spacing, highlighted keywords */}
              <h3 className="text-5xl font-extrabold mb-12 text-gray-900 border-b-2 border-gray-100 pb-6 inline-block" style={{ lineHeight: '1.2' }}>
                Photosynthesis
              </h3>

              <div className="space-y-12" style={{ fontSize: '28px', lineHeight: '2.2', letterSpacing: '0.5px' }}>
                <p className="text-gray-800">
                  <span className="bg-[#FEF3C7] text-[#D97706] font-bold px-3 py-1 rounded-xl">Plants make food</span> using <span className="text-[#10B981] font-bold">sunlight</span>.
                </p>
                
                <p className="text-gray-800">
                  This process happens in the <span className="bg-[#D1FAE5] text-[#059669] font-bold px-3 py-1 rounded-xl">leaves</span>.
                </p>
                
                <p className="text-gray-800">
                  They breathe in <span className="font-bold underline decoration-4 decoration-[#1d348a] underline-offset-8">carbon dioxide</span> and release fresh <span className="bg-[#DBEAFE] text-[#2563EB] font-bold px-3 py-1 rounded-xl">oxygen</span>.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* === Reading Speed Mode Mock === */}
        {supportMode === 'reading-speed' && (
          <div className="max-w-3xl mx-auto flex flex-col items-center animate-in fade-in duration-500 py-10">
            
            {/* Step container */}
            <div className="w-full relative">
              {/* Previous step indicator */}
              {step > 1 && (
                 <div className="absolute -top-16 left-0 right-0 flex justify-center opacity-40">
                   <div className="bg-white px-6 py-3 rounded-2xl shadow-sm text-gray-400 font-bold blur-[1px] scale-95 border border-gray-200">
                     Step {step - 1} ...
                   </div>
                 </div>
              )}

              <div className="bg-white p-10 lg:p-14 rounded-[2rem] shadow-2xl border-2 border-[#e8eef6] text-center transform transition-all duration-500 relative z-10 w-full">
                <span className="text-[#1d348a] font-black tracking-widest uppercase text-sm mb-6 block bg-[#eef1f9] w-fit mx-auto px-5 py-2 rounded-full">
                  Step {step} of 3
                </span>
                
                {/* Progressive Content */}
                <p className="text-4xl lg:text-5xl font-extrabold text-[#1d1f2e] leading-tight mt-8 mb-6">
                  {explanationText}
                </p>
              </div>
            </div>

            {/* Next Step Action */}
            <div className="mt-14 w-full flex justify-center">
              {step < 3 ? (
                <button 
                  onClick={() => setStep(s => s + 1)}
                  className="group flex items-center gap-4 px-10 py-6 bg-[#10B981] hover:bg-[#059669] text-white rounded-full font-black text-2xl shadow-xl shadow-[#10B981]/30 transition-all hover:scale-105"
                >
                  Next
                  <svg className="w-8 h-8 group-hover:translate-x-2 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
                </button>
              ) : (
                <button 
                  onClick={() => setStep(1)}
                  className="group flex items-center gap-3 px-8 py-5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-full font-bold text-xl transition-all"
                >
                  <svg className="w-6 h-6 group-hover:-rotate-180 transition-transform duration-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
                  Restart Explanation
                </button>
              )}
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
