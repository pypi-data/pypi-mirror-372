"""knowlithic TTS plugin for LiveKit using Knowlithic AI."""

from __future__ import annotations

import asyncio
import base64
import json
import time
from dataclasses import dataclass, replace
from typing import Optional
import weakref
import aiohttp
from .log import logger

from livekit.agents import (
    APIConnectionError,
    APIConnectOptions,
    APIError,
    APIStatusError,
    APITimeoutError,
    tokenize,
    tts,
    utils,
)
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS


@dataclass
class TTSOptions:
    tokenizer: tokenize.SentenceTokenizer
    voice: str = "elise"
    sample_rate: int = 16000 # fixed 16000

class TTS(tts.TTS):
    def __init__(
        self,
        *,
        voice: str | None = "elise",
        tokenizer: tokenize.SentenceTokenizer | None = None,
        sample_rate: int = 16000,
        http_session: aiohttp.ClientSession | None = None,
        use_streaming: bool = True,
        CustomWebSocketURL:str = "ws://localhost:8000"

    ) -> None:
        
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=use_streaming),
            sample_rate=sample_rate,
            num_channels=1,
        )

        self.WebSocketURL = CustomWebSocketURL

        if tokenizer is None:
            tokenizer = tokenize.blingfire.SentenceTokenizer() # ideally use blingfire


        self._opts = TTSOptions(
            voice=voice,
            sample_rate=sample_rate,
            tokenizer=tokenizer,
        )

        self._session = http_session
        self._streams = weakref.WeakSet[SynthesizeStream]()
        # Remove connection pool and use persistent websocket connection
        self._ws_connection = None
        self._ws_lock = asyncio.Lock()

    def synthesize(
        self, text: str, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS
    ) -> ChunkedStream:
        return ChunkedStream(tts=self, input_text=text, conn_options=conn_options)
        
    async def _get_ws_connection(self, timeout: float) -> aiohttp.ClientWebSocketResponse:
        """Get or create a persistent websocket connection."""
        async with self._ws_lock:
            if self._ws_connection is None or self._ws_connection.closed:
                try:
                    self._ws_connection = await asyncio.wait_for(
                        self._ensure_session().ws_connect(
                            self.WebSocketURL,
                        ),
                        timeout,
                    )
                    logger.info("Created new persistent websocket connection")
                except Exception as e:
                    logger.error(f"Failed to create websocket connection: {e}")
                    raise
            return self._ws_connection

    async def _ensure_ws_connection(self, timeout: float) -> aiohttp.ClientWebSocketResponse:
        """Ensure websocket connection is healthy and reconnect if needed."""
        try:
            ws = await self._get_ws_connection(timeout)
            # Check if connection is still healthy
            if ws.closed:
                async with self._ws_lock:
                    self._ws_connection = None
                ws = await self._get_ws_connection(timeout)
            return ws
        except Exception as e:
            logger.error(f"Websocket connection error: {e}")
            # Reset connection on error
            async with self._ws_lock:
                self._ws_connection = None
            raise

    def _ensure_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = utils.http_context.http_session()

        return self._session

    def prewarm(self) -> None:
        # Initialize the websocket connection
        asyncio.create_task(self._get_ws_connection(timeout=10.0))

    def update_options(
        self,
        *,
        voice: str | None = None,
    ) -> None:
        """
        Update the Text-to-Speech (TTS) configuration options.

        Args:
            voice_uuid (str, optional): The voice UUID for the desired voice.
        """  # noqa: E501
        self._opts.voice = voice or self._opts.voice


    def stream(
        self, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS
    ) -> SynthesizeStream:
        stream = SynthesizeStream(tts=self, conn_options=conn_options)
        self._streams.add(stream)
        return stream

    async def aclose(self) -> None:
        for stream in list(self._streams):
            await stream.aclose()

        self._streams.clear()
        

class SynthesizeStream(tts.SynthesizeStream):
    """Stream-based text-to-speech synthesis using Knowlithic WebSocket API.


    This implementation connects to Knowlithic's WebSocket API for real-time streaming
    synthesis. Note that this requires web socket connection in the environment variables.
    """

    def __init__(self, *, tts: TTS, conn_options: APIConnectOptions):
        super().__init__(tts=tts, conn_options=conn_options)
        self._tts: TTS = tts
        self._opts = replace(tts._opts)
        self._segments_ch = utils.aio.Chan[tokenize.SentenceStream]()

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        request_id = utils.shortuuid()
        output_emitter.initialize(
            request_id=request_id,
            sample_rate=self._opts.sample_rate,
            num_channels=1,
            stream=True,
            mime_type="audio/pcm",
        )

        async def _tokenize_input() -> None:
            """tokenize text from the input_ch to words"""
            input_stream = None
            async for text in self._input_ch:
                if isinstance(text, str):
                    if input_stream is None:
                        # new segment (after flush for e.g)
                        input_stream = self._opts.tokenizer.stream()
                        self._segments_ch.send_nowait(input_stream)
                    input_stream.push_text(text)
                elif isinstance(text, self._FlushSentinel):
                    if input_stream is not None:
                        input_stream.end_input()
                    input_stream = None

            if input_stream is not None:
                input_stream.end_input()

            self._segments_ch.close()

        async def _process_segments() -> None:
            async for input_stream in self._segments_ch:
                await self._run_ws(input_stream, output_emitter)

        tasks = [
            asyncio.create_task(_tokenize_input()),
            asyncio.create_task(_process_segments()),
        ]
        try:
            await asyncio.gather(*tasks)
        except asyncio.TimeoutError:
            raise APITimeoutError() from None
        except aiohttp.ClientResponseError as e:
            raise APIStatusError(
                message=e.message, status_code=e.status, request_id=request_id, body=None
            ) from None
        except Exception as e:
            raise APIConnectionError() from e
        finally:
            await utils.aio.gracefully_cancel(*tasks)

    async def _run_ws(
        self, input_stream: tokenize.SentenceStream, output_emitter: tts.AudioEmitter
    ) -> None:
        segment_id = utils.shortuuid()
        output_emitter.start_segment(segment_id=segment_id)

        last_index = 0
        input_ended = False
        first_send_time = None

        async def _send_task(ws: aiohttp.ClientWebSocketResponse) -> None:
            nonlocal input_ended, last_index, first_send_time
            async for data in input_stream:
                last_index += 1
                payload = {
                    "type": "text_to_speech",
                    "text": data.token,
                    "voice": self._opts.voice,
                    "request_id": last_index,
                    "sample_rate": self._opts.sample_rate, 
                    "output_format": "wav",
                }
                self._mark_started()
                logger.info( f"Sent :{payload['text']}")
                if first_send_time is None:
                    first_send_time = time.time()
                await ws.send_str(json.dumps(payload))

            input_ended = True

        async def _recv_task(ws: aiohttp.ClientWebSocketResponse) -> None:
            nonlocal first_send_time
            first_response_received = False
            while True:
                msg = await ws.receive()
                if msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                ):
                    raise APIStatusError("Knowlithic connection closed unexpectedly")

                if msg.type != aiohttp.WSMsgType.TEXT:
                    logger.warning("Unexpected Knowlithic message type")
                    continue

                data = json.loads(msg.data)
                if data.get("type") == "audio":
                    if data.get("audio_data", None):
                        b64data = base64.b64decode(data["audio_data"])
                        
                        # Log time to first byte on first audio response
                        if not first_response_received:
                            first_response_time = time.time()
                            if first_send_time is not None:
                                time_to_first_byte = first_response_time - first_send_time
                                logger.info(f"LLM Response + Audio time: {time_to_first_byte:.3f} seconds")
                            first_response_received = True

                        output_emitter.push(b64data)

                elif data.get("type") == "audio_end":
                    index = data["request_id"]
                    if index == last_index and input_ended:
                        output_emitter.end_segment()
                        break
                else:
                    logger.error("Unexpected Knowlithic message ")

        ws = await self._tts._ensure_ws_connection(timeout=self._conn_options.timeout)
        tasks = [
            asyncio.create_task(_send_task(ws)),
            asyncio.create_task(_recv_task(ws)),
        ]
        try:
            await asyncio.gather(*tasks)
        finally:
            await utils.aio.gracefully_cancel(*tasks)

class ChunkedStream(tts.ChunkedStream):
    """Synthesize text into speech in one go using Knowlithic AI's REST API."""
    """Knowlithic currently only supports websocket conneciton and ChunkedStream (streaming = False) for tts will  not work"""

    def __init__(self, *, tts: TTS, input_text: str, conn_options: APIConnectOptions) -> None:
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts: TTS = tts
        self._opts = replace(tts._opts)

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        print("Chunked stream run not implemented")