export const getAvailableVoices = () => {
  return new Promise((resolve) => {
    let voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
      resolve(voices);
      return;
    }
    window.speechSynthesis.onvoiceschanged = () => {
      voices = window.speechSynthesis.getVoices();
      resolve(voices);
    };
  });
};

export const playTextToSpeech = (text, voiceName, onEnd) => {
  if (!window.speechSynthesis) return;

  // Stop any currently playing speech
  stopTextToSpeech();

  const utterance = new SpeechSynthesisUtterance(text);
  
  // Set explicit language and adjust rate for accessibility
  utterance.lang = "en-US";
  utterance.rate = 0.85;
  utterance.pitch = 1;

  const voices = window.speechSynthesis.getVoices();
  let selectedVoice = null;
  
  // Try to use specifically passed voice
  if (voiceName) {
    selectedVoice = voices.find(v => v.name === voiceName);
  }
  
  // Fallback to the first available English voice
  if (!selectedVoice) {
    selectedVoice = voices.find(v => v.lang.startsWith("en"));
  }
  
  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }

  if (onEnd) {
    utterance.onend = onEnd;
    utterance.onerror = onEnd;
  }

  window.speechSynthesis.speak(utterance);
};

export const stopTextToSpeech = () => {
  if (window.speechSynthesis && window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
  }
};
