"""Data models for knowlithic LiveKit plugin."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class TTSRequest:
    """Model for TTS request payload."""
    type: str = "text_to_speech"
    text: str = ""
    voice: str = "elise"
    request_id: int = 0
    sample_rate: int = 16000
    output_format: str = "wav"

@dataclass
class TTSResponse:
    """Model for TTS response."""
    type: str
    audio_data: Optional[str] = None
    request_id: Optional[int] = None
    error: Optional[str] = None
