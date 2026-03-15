"""
TTS MCP tools — thin wrappers exposing TTSService to agents.

Architecture rule:
    The Accessibility Agent must NOT call gTTS or any TTS library directly.
    All audio synthesis goes through TTSService via these functions.

The service gracefully returns None if gTTS is not installed, so agents
can check the return value and fall back to text-only output.

Install gTTS to enable synthesis:
    pip install gTTS
"""

from __future__ import annotations

from typing import Optional

from src.app.services.tts_service import TTSService

_service = TTSService()


def tts_synthesize(
    text: str,
    voice: Optional[str] = None,
    lang: str = "en",
    slow: bool = False,
) -> Optional[bytes]:
    """
    Convert text to MP3 audio bytes.

    Called by the Accessibility Agent when a learner's profile has
    use_tts=True (e.g. dyslexia or visual impairment support modes).

    Args:
        text:  Text to synthesize.
        voice: Voice identifier (reserved; ignored by gTTS backend).
        lang:  BCP-47 language code (default "en").
        slow:  Use slower speech for clearer pronunciation.

    Returns:
        MP3 audio as bytes, or None if TTS is unavailable.
    """
    return _service.synthesize_text(text, voice=voice, lang=lang, slow=slow)


def tts_is_available() -> bool:
    """
    Check whether TTS synthesis is available in this environment.

    Returns:
        True if gTTS is installed and can produce audio.
    """
    return _service.is_available()
