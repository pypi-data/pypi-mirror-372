# LiveKit TTS Integration

A LiveKit agent implementation with custom Text-to-Speech (TTS) using Knowlithic AI's WebSocket API.

## Overview

This project demonstrates how to integrate a custom TTS service with LiveKit agents for real-time voice conversations. The TTS implementation uses a persistent WebSocket connection to Knowlithic AI for low-latency audio synthesis.

## Features

- Real-time streaming TTS synthesis via WebSocket
- Persistent connection management for optimal performance
- Integration with LiveKit Agents framework
- Configurable voice and sample rate
- Automatic connection recovery and error handling

## Quick Start

### 1. Environment Setup

Create a `.env` file with your configuration:

```bash
# Knowlithic TTS WebSocket URL
KNOWLITHIC_TTS_SERVER=ws://localhost:8000

# System prompt for the agent
SYSTEM_PROMPT="You are Avery, a warm, empathetic AI nurse..."

# Optional: Override default TTS settings
TTS_SERVER_URL=ws://your-tts-server:8000
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Agent

```bash
python agent.py download-files
```

```bash
python agent.py
```

## TTS Integration Pattern

The TTS is integrated into the LiveKit agent session as follows:

```python
from tts_custom.knowlithictts import TTS

# Initialize TTS with persistent connection
custom_tts = TTS()

# Create agent session with TTS
session = AgentSession(
    stt=deepgram.STT(model="nova-3", language="multi"),
    llm=groq.LLM(model="llama3-8b-8192"),
    tts=custom_tts,  # Custom TTS integration
    vad=silero.VAD.load(
        min_silence_duration=3.0,
        min_speech_duration=1.0,
        activation_threshold=20.0,
    ),
)

# Start the session
await session.start(
    room=ctx.room,
    agent=Assistant(),
    room_input_options=RoomInputOptions(
        noise_cancellation=noise_cancellation.BVC(),
    ),
)

# Clean up TTS connection
finally:
    await custom_tts.aclose()
```

## TTS Configuration

### Basic Configuration

```python
from tts_custom.knowlithictts import TTS

# Default configuration
tts = TTS()  # Uses "elise" voice, 16kHz sample rate

# Custom configuration
tts = TTS(
    voice="elise",
    sample_rate=16000,
    use_streaming=True
)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KNOWLITHIC_TTS_SERVER` | WebSocket URL for TTS service | Required |
| `TTS_SERVER_URL` | Alternative TTS server URL | Optional |

### TTS Options

- **voice**: Voice identifier (default: "elise")
- **sample_rate**: Audio sample rate in Hz (default: 16000)
- **use_streaming**: Enable streaming mode (default: True)

## Architecture

### Connection Management

The TTS implementation uses a persistent WebSocket connection:

```python
class TTS(tts.TTS):
    def __init__(self, ...):
        self._ws_connection = None
        self._ws_lock = asyncio.Lock()
    
    async def _get_ws_connection(self, timeout: float):
        # Get or create persistent connection
        async with self._ws_lock:
            if self._ws_connection is None or self._ws_connection.closed:
                self._ws_connection = await self._ensure_session().ws_connect(
                    KNOWLITHIC_WEBSOCKET_URL
                )
            return self._ws_connection
```

### Streaming Synthesis

Text is processed in real-time through the WebSocket connection:

```python
async def _run_ws(self, input_stream, output_emitter):
    # Send text chunks to TTS service
    payload = {
        "type": "text_to_speech",
        "text": data.token,
        "voice": self._opts.voice,
        "request_id": last_index,
        "sample_rate": self._opts.sample_rate,
        "output_format": "wav",
    }
    await ws.send_str(json.dumps(payload))
    
    # Receive and emit audio data
    if data.get("type") == "audio":
        b64data = base64.b64decode(data["audio_data"])
        output_emitter.push(b64data)
```

## Performance Optimization

### Connection Prewarming

```python
# Prewarm the TTS connection for faster first response
tts.prewarm()
```

### Error Handling

The implementation includes automatic connection recovery:

```python
async def _ensure_ws_connection(self, timeout: float):
    try:
        ws = await self._get_ws_connection(timeout)
        if ws.closed:
            async with self._ws_lock:
                self._ws_connection = None
            ws = await self._get_ws_connection(timeout)
        return ws
    except Exception as e:
        # Reset connection on error
        async with self._ws_lock:
            self._ws_connection = None
        raise
```

## Requirements

- Python 3.9+
- LiveKit Agents 1.2.2+
- aiohttp 3.8.0+
- python-dotenv 1.0.0+
- Knowlithic TTS WebSocket service

## Development

### Running Locally

1. Start your Knowlithic TTS WebSocket service
2. Set environment variables
3. Run the agent: `python agent.py`

### Testing TTS

```python
import asyncio
from tts_custom.knowlithictts import TTS

async def test_tts():
    tts = TTS()
    stream = tts.stream()
    
    await stream.push_text("Hello, this is a test.")
    await stream.flush()
    await stream.aclose()
    
    await tts.aclose()

asyncio.run(test_tts())
```

## Troubleshooting

### Common Issues

1. **Connection Timeout**: Ensure `KNOWLITHIC_TTS_SERVER` is accessible
2. **Audio Quality**: Verify sample rate matches TTS service (16000 Hz)
3. **Latency**: Use connection prewarming for faster first response

### Logging

Enable debug logging to troubleshoot TTS issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

MIT License - see LICENSE file for details.
