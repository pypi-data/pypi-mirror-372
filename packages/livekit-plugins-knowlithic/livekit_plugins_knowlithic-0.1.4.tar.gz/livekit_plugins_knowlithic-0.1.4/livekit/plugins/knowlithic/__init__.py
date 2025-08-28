"""knowlithic LiveKit plugin for TTS using Knowlithic AI."""

from .tts import TTS, SynthesizeStream, ChunkedStream
from .config import KNOWLITHIC_WEBSOCKET_URL, DEFAULT_VOICE, DEFAULT_SAMPLE_RATE
from .models import TTSRequest, TTSResponse
from .version import __version__

__all__ = [
    "TTS",
    "SynthesizeStream", 
    "ChunkedStream",
    "TTSRequest",
    "TTSResponse",
    "KNOWLITHIC_WEBSOCKET_URL",
    "DEFAULT_VOICE",
    "DEFAULT_SAMPLE_RATE",
    "__version__",
]
from livekit.agents import Plugin

class KnowlithicPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__(__name__, __version__, __package__)


Plugin.register_plugin(KnowlithicPlugin())

# Cleanup docs of unexported modules
_module = dir()
NOT_IN_ALL = [m for m in _module if m not in __all__]

__pdoc__ = {}

for n in NOT_IN_ALL:
    __pdoc__[n] = False