import React, { useState, useEffect } from 'react';
import { playTextToSpeech, stopTextToSpeech, getAvailableVoices } from '../services/ttsService';

const TextToSpeech = ({ text }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [voices, setVoices] = useState([]);
  const [selectedVoiceName, setSelectedVoiceName] = useState('');

  useEffect(() => {
    const fetchVoices = async () => {
      const availableVoices = await getAvailableVoices();
      const englishVoices = availableVoices.filter(v => v.lang.startsWith('en'));

      const voicesToUse = englishVoices.length > 0 ? englishVoices : availableVoices;
      setVoices(voicesToUse);

      if (voicesToUse.length > 0) {
        setSelectedVoiceName(voicesToUse[0].name);
      }
    };
    fetchVoices();
  }, []);

  useEffect(() => {
    // When the component unmounts or text changes, stop speech
    stopTextToSpeech();
    setIsPlaying(false);
    return () => stopTextToSpeech();
  }, [text]);

  const handleListen = () => {
    setIsPlaying(true);
    playTextToSpeech(text, selectedVoiceName, () => setIsPlaying(false));
  };

  const handleStop = () => {
    setIsPlaying(false);
    stopTextToSpeech();
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleListen}
        disabled={isPlaying}
        className={`flex items-center gap-1.5 px-3 py-1.5 text-sm ${isPlaying ? 'bg-gray-400 cursor-not-allowed' : 'bg-[#1d348a] hover:bg-[#162870]'
          } text-white rounded-lg font-semibold transition-all shadow-sm`}
        title="Listen to explanation"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
        </svg>
        Listen
      </button>

      <button
        onClick={handleStop}
        disabled={!isPlaying}
        className={`flex items-center gap-1.5 px-3 py-1.5 text-sm ${!isPlaying ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-red-100 hover:bg-red-200 text-red-700'
          } rounded-lg font-semibold transition-all`}
        title="Stop playback"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        </svg>
        Stop
      </button>
    </div>
  );
};

export default TextToSpeech;
