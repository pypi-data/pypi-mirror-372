"""Configuration for knowlithic LiveKit plugin."""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Knowlithic WebSocket URL - can be overridden via environment variable
KNOWLITHIC_WEBSOCKET_URL = os.getenv("TTS_SERVER_URL", "ws://localhost:8000")

# Default voice configuration
DEFAULT_VOICE = "elise"
DEFAULT_SAMPLE_RATE = 16000 