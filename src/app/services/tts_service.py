"""
TTSService — text-to-speech synthesis (optional component).

Uses gTTS (Google Text-to-Speech) if it is installed.
If gTTS is not available, synthesize_text() returns None and logs a warning
so the system degrades gracefully instead of crashing.

Architecture rule:
    Agents and the Accessibility Agent must NOT call gTTS directly.
    All TTS synthesis goes through TTSService (or TTSTool).

Install gTTS with:
    pip install gTTS

Voice/language note:
    gTTS does not support named voices. The `voice` parameter is accepted
    for API compatibility (e.g. a future swap to ElevenLabs) but is ignored
    by the gTTS backend.
"""

from __future__ import annotations

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TTSService:
    """
    Synthesizes speech from text.

    Usage:
        svc = TTSService()
        audio_bytes = svc.synthesize_text("Hello, welcome to NeuroLearn.")
        if audio_bytes:
            with open("output.mp3", "wb") as f:
                f.write(audio_bytes)
    """

    def __init__(self, default_lang: str = "en") -> None:
        """
        Args:
            default_lang: BCP-47 language code for synthesis (default "en").
        """
        self._lang = default_lang
        self._available = self._check_gtts()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def synthesize_text(
        self,
        text: str,
        voice: Optional[str] = None,
        lang: Optional[str] = None,
        slow: bool = False,
    ) -> Optional[bytes]:
        """
        Convert text to MP3 audio bytes.

        Args:
            text:  The text to synthesize.
            voice: Ignored by the gTTS backend (reserved for future use).
            lang:  BCP-47 language code. Overrides the service default.
            slow:  If True, uses gTTS slow mode (clearer pronunciation).

        Returns:
            MP3 audio as bytes, or None if TTS is unavailable.
        """
        if not text or not text.strip():
            return None

        if not self._available:
            logger.warning(
                "TTSService: gTTS is not installed — returning None. "
                "Install it with:  pip install gTTS"
            )
            return None

        try:
            from gtts import gTTS
            target_lang = lang or self._lang
            tts = gTTS(text=text.strip(), lang=target_lang, slow=slow)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            audio_bytes = buf.read()
            logger.info(
                "TTS synthesized %d chars → %d bytes (lang=%s)",
                len(text), len(audio_bytes), target_lang,
            )
            return audio_bytes
        except Exception as exc:
            logger.error("TTS synthesis failed: %s", exc)
            return None

    def is_available(self) -> bool:
        """Return True if gTTS is installed and synthesis is possible."""
        return self._available

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _check_gtts() -> bool:
        try:
            import gtts  # noqa: F401
            return True
        except ImportError:
            return False
