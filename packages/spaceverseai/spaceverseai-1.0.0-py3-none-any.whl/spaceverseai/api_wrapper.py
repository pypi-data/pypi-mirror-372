import asyncio
import json
import base64
import logging
import time
import os
from typing import Dict, List, Optional, Callable, Any, Union
import aiohttp
import websockets
from datetime import datetime
import uuid
from pathlib import Path
import threading
from dataclasses import dataclass
from enum import Enum
import inspect
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat detection levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EmotionType(Enum):
    """Supported emotion types"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"


class VoiceType(Enum):
    """Supported OpenAI voice types"""
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"


class LanguageCode(Enum):
    """Supported language codes"""
    ENGLISH = "en"
    ITALIAN = "it"
    # Add more languages as supported by the system


@dataclass
class ConnectionStatus:
    """Connection status information"""
    voice_chat_connected: bool = False
    emotion_detection_connected: bool = False
    openai_connected: bool = False
    session_established: bool = False
    session_id: Optional[str] = None
    client_id: str = ""
    last_ping: Optional[datetime] = None


@dataclass
class SystemHealth:
    """System health information"""
    status: str
    message: str
    connections: Dict[str, int]
    uptime: Optional[str] = None


class SpaceverseAIClient:
    """
    Comprehensive API wrapper for Spaceverse AI Voice Chat Application

    This client provides both synchronous and asynchronous interfaces for:
    - Session management
    - Real-time voice chat via WebSocket
    - Image-based emotion detection
    - Client emotion management
    - Session monitoring and debugging
    """

    def __init__(
        self, 
        base_url: str = "https://spaceverse-python-1051344022089.us-east1.run.app/", 
        client_id: str = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        auto_reconnect: bool = True,
        debug: bool = False
    ):
        """
        Initialize the API client

        Args:
            base_url: Base URL of the FastAPI application
            client_id: Unique client identifier (auto-generated if not provided)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            auto_reconnect: Whether to automatically reconnect WebSockets
            debug: Enable debug logging
        """
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id or str(uuid.uuid4())
        self.session_id = None
        self.chat_websocket = None
        self.emotion_websocket = None
        self.session = None
        
        # Configuration
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.auto_reconnect = auto_reconnect
        self.debug = debug
        
        # Status tracking
        self.connection_status = ConnectionStatus(client_id=self.client_id)
        self.last_activity = datetime.now()
        
        # Event handlers for WebSocket messages
        self.message_handlers = {}
        self.emotion_handlers = {}
        self.error_handlers = {}
        
        # Internal state
        self._is_closing = False
        self._reconnect_tasks = set()
        self._event_loop = None
        
        # Thread pool for synchronous operations
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "reconnects": 0,
            "uptime": datetime.now()
        }

        if debug:
            logging.getLogger(__name__).setLevel(logging.DEBUG)

        logger.info(f"Initialized SpaceverseAI client with ID: {self.client_id}")
        logger.debug(f"Configuration: timeout={timeout}, max_retries={max_retries}, auto_reconnect={auto_reconnect}")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self._is_closing = True
        await self.disconnect_all()
        if self.session:
            await self.session.close()
        if self._thread_pool:
            self._thread_pool.shutdown(wait=True)

    # ================================
    # Enhanced Utility Methods
    # ================================

    async def _retry_request(self, request_func, *args, **kwargs):
        """Retry mechanism for HTTP requests"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await request_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.stats["errors"] += 1
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
        
        raise last_exception

    def get_connection_status(self) -> ConnectionStatus:
        """Get current connection status"""
        self.connection_status.voice_chat_connected = self.is_voice_chat_connected()
        self.connection_status.emotion_detection_connected = self.is_emotion_detection_connected()
        self.connection_status.session_id = self.session_id
        return self.connection_status

    def get_statistics(self) -> Dict[str, Any]:
        """Get client statistics"""
        uptime = datetime.now() - self.stats["uptime"]
        return {
            **self.stats,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_string": str(uptime),
            "connection_status": self.get_connection_status().__dict__
        }

    async def wait_for_connection(self, timeout: float = 30.0) -> bool:
        """Wait for voice chat connection to be established"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_voice_chat_connected() and self.session_id:
                return True
            await asyncio.sleep(0.1)
        return False

    def add_error_handler(self, handler_name: str, handler: Callable):
        """Add an error handler"""
        self.error_handlers[handler_name] = handler
        logger.info(f"Added error handler: {handler_name}")

    def remove_error_handler(self, handler_name: str):
        """Remove an error handler"""
        if handler_name in self.error_handlers:
            del self.error_handlers[handler_name]
            logger.info(f"Removed error handler: {handler_name}")

    async def _handle_error(self, error: Exception, context: str = ""):
        """Handle errors and call error handlers"""
        error_data = {
            "error": str(error),
            "type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "client_id": self.client_id
        }

        for handler_name, handler in self.error_handlers.items():
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error_data)
                else:
                    handler(error_data)
            except Exception as handler_error:
                logger.error(f"Error in error handler {handler_name}: {handler_error}")

    async def _auto_reconnect_websocket(self, websocket_type: str):
        """Auto-reconnect WebSocket connections"""
        if not self.auto_reconnect or self._is_closing:
            return

        self.stats["reconnects"] += 1
        logger.info(f"Auto-reconnecting {websocket_type} WebSocket...")

        try:
            if websocket_type == "voice_chat":
                await self.connect_voice_chat()
            elif websocket_type == "emotion_detection":
                await self.connect_emotion_detection()
        except Exception as e:
            logger.error(f"Failed to auto-reconnect {websocket_type}: {e}")
            await self._handle_error(e, f"auto_reconnect_{websocket_type}")

    # ================================
    # REST API Methods
    # ================================

    async def health_check(self) -> SystemHealth:
        """Check if the API server is healthy"""
        async def _request():
            async with self.session.get(f"{self.base_url}/health", timeout=self.timeout) as response:
                response.raise_for_status()
                data = await response.json()
                return SystemHealth(
                    status=data.get("status", "unknown"),
                    message=data.get("message", ""),
                    connections=data.get("connections", {}),
                    uptime=data.get("uptime")
                )
        
        return await self._retry_request(_request)

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session status"""
        async with self.session.get(
            f"{self.base_url}/api/session/{session_id}/status"
        ) as response:
            if response.status == 404:
                raise ValueError(f"Session {session_id} not found")
            response.raise_for_status()
            return await response.json()

    async def list_active_sessions(self) -> Dict[str, Any]:
        """List all active sessions"""
        async with self.session.get(f"{self.base_url}/api/sessions") as response:
            response.raise_for_status()
            return await response.json()

    async def get_session_history_info(
        self, session_id: str, limit: int = 50
    ) -> Dict[str, Any]:
        """Get session history information (OpenAI manages actual history)"""
        params = {"limit": limit} if limit else {}
        async with self.session.get(
            f"{self.base_url}/api/session/{session_id}/history", params=params
        ) as response:
            if response.status == 404:
                raise ValueError(f"Session {session_id} not found")
            response.raise_for_status()
            return await response.json()

    async def get_session_events(
        self, session_id: str, limit: int = 50
    ) -> Dict[str, Any]:
        """Get OpenAI event IDs tracked for a session"""
        params = {"limit": limit} if limit else {}
        async with self.session.get(
            f"{self.base_url}/api/session/{session_id}/events", params=params
        ) as response:
            if response.status == 404:
                raise ValueError(f"Session {session_id} not found")
            response.raise_for_status()
            return await response.json()

    async def get_client_emotion(self, client_id: str = None) -> Dict[str, Any]:
        """Get current detected emotion for a client"""
        client_id = client_id or self.client_id
        async with self.session.get(
            f"{self.base_url}/api/client/{client_id}/emotion"
        ) as response:
            if response.status == 404:
                raise ValueError(f"Client {client_id} not found")
            response.raise_for_status()
            return await response.json()

    async def set_client_emotion(
        self, emotion: str, client_id: str = None
    ) -> Dict[str, Any]:
        """Manually set detected emotion for a client"""
        client_id = client_id or self.client_id
        data = {"emotion": emotion}
        async with self.session.post(
            f"{self.base_url}/api/client/{client_id}/emotion", json=data
        ) as response:
            if response.status == 404:
                raise ValueError(f"Client {client_id} not found")
            response.raise_for_status()
            return await response.json()

    async def test_dual_emotion_system(
        self,
        facial_emotion: str,
        voice_emotion: str,
        test_message: str = "How are you doing today?",
        client_id: str = None,
    ) -> Dict[str, Any]:
        """Test the dual emotion system with both facial and voice emotions"""
        client_id = client_id or self.client_id
        data = {
            "facial_emotion": facial_emotion,
            "voice_emotion": voice_emotion,
            "test_message": test_message,
        }
        async with self.session.post(
            f"{self.base_url}/api/client/{client_id}/test-dual-emotion", json=data
        ) as response:
            if response.status == 404:
                raise ValueError(f"Client {client_id} not found")
            response.raise_for_status()
            return await response.json()

    # ================================
    # Onboarding Data Management
    # ================================

    async def get_onboarding_data(self, client_id: str = None) -> Dict[str, Any]:
        """Get current onboarding data for a client"""
        client_id = client_id or self.client_id
        async with self.session.get(
            f"{self.base_url}/api/client/{client_id}/onboarding-data"
        ) as response:
            if response.status == 404:
                raise ValueError(f"Client {client_id} not found")
            response.raise_for_status()
            return await response.json()

    async def set_onboarding_data(
        self, onboarding_data: List[Dict], client_id: str = None
    ) -> Dict[str, Any]:
        """Set onboarding data for a client"""
        client_id = client_id or self.client_id
        data = {"onboarding_data": onboarding_data}
        async with self.session.post(
            f"{self.base_url}/api/client/{client_id}/onboarding-data", json=data
        ) as response:
            if response.status == 404:
                raise ValueError(f"Client {client_id} not found")
            response.raise_for_status()
            return await response.json()

    # ================================
    # Emotional Logic Management
    # ================================

    async def get_emotional_logic(self, client_id: str = None) -> Dict[str, Any]:
        """Get current emotional logic for a client"""
        client_id = client_id or self.client_id
        async with self.session.get(
            f"{self.base_url}/api/client/{client_id}/emotional-logic"
        ) as response:
            if response.status == 404:
                raise ValueError(f"Client {client_id} not found")
            response.raise_for_status()
            return await response.json()

    async def set_emotional_logic(
        self, emotional_logic: List[Dict], client_id: str = None
    ) -> Dict[str, Any]:
        """Set emotional logic for a client"""
        client_id = client_id or self.client_id
        data = {"emotional_logic": emotional_logic}
        async with self.session.post(
            f"{self.base_url}/api/client/{client_id}/emotional-logic", json=data
        ) as response:
            if response.status == 404:
                raise ValueError(f"Client {client_id} not found")
            response.raise_for_status()
            return await response.json()

    # ================================
    # User Preferences Management
    # ================================

    async def get_user_preferences(self, client_id: str = None) -> Dict[str, Any]:
        """Get current user preferences for a client"""
        client_id = client_id or self.client_id
        async with self.session.get(
            f"{self.base_url}/api/client/{client_id}/user-preferences"
        ) as response:
            if response.status == 404:
                raise ValueError(f"Client {client_id} not found")
            response.raise_for_status()
            return await response.json()

    async def set_user_preferences(
        self, preferences: str, client_id: str = None
    ) -> Dict[str, Any]:
        """Set user preferences for a client"""
        client_id = client_id or self.client_id
        data = {"preferences": preferences}
        async with self.session.post(
            f"{self.base_url}/api/client/{client_id}/user-preferences", json=data
        ) as response:
            if response.status == 404:
                raise ValueError(f"Client {client_id} not found")
            response.raise_for_status()
            return await response.json()

    # ================================
    # AI Service Endpoints
    # ================================

    async def generate_onboarding_questions(
        self, profession: str, prompt: str
    ) -> Dict[str, Any]:
        """Generate dynamic onboarding questions based on profession and prompt"""
        data = {"profession": profession, "prompt": prompt}
        async with self.session.post(
            f"{self.base_url}/generate_onboarding_questions", json=data
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def generate_transcription(self, audio_url: str) -> Dict[str, Any]:
        """Generate transcription for an audio file from URL"""
        data = {"audio_url": audio_url}
        async with self.session.post(
            f"{self.base_url}/generate_transcription", json=data
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def generate_summary(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI agent summary from provided data"""
        data = {"agent_data": agent_data}
        async with self.session.post(
            f"{self.base_url}/generate_summary", json=data
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def generate_user_preferences(self, user_data: str) -> Dict[str, Any]:
        """Generate user preferences from chat history"""
        data = {"user_data": user_data}
        async with self.session.post(
            f"{self.base_url}/generate_user_preferences", json=data
        ) as response:
            response.raise_for_status()
            return await response.json()

    # ================================
    # Threat Detection and Safety
    # ================================

    async def test_threat_detection(
        self, message: str, threat_detected: bool = False
    ) -> Dict[str, Any]:
        """Test threat detection system with a specific message"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        data = {
            "type": "test_threat_detection",
            "message": message,
            "threat_detected": threat_detected,
        }

        await self.chat_websocket.send(json.dumps(data))
        logger.info(
            f"Sent threat detection test: message='{message}', threat_detected={threat_detected}"
        )

    async def reset_threat_status(self) -> Dict[str, Any]:
        """Reset threat detection status for this client"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        data = {"type": "reset_threat_status"}
        await self.chat_websocket.send(json.dumps(data))
        logger.info("Sent threat status reset request")

    # ================================
    # Concurrent Status and Monitoring
    # ================================

    async def get_concurrent_status(self) -> Dict[str, Any]:
        """Get detailed status of all active WebSocket connections"""
        async with self.session.get(
            f"{self.base_url}/api/concurrent-status"
        ) as response:
            response.raise_for_status()
            return await response.json()

    # ================================
    # WebSocket Methods - Voice Chat
    # ================================

    async def connect_voice_chat(
        self, session_id: str = None, message_handler: Callable = None
    ) -> str:
        """
        Connect to voice chat WebSocket

        Args:
            session_id: Optional session ID to restore previous conversation
            message_handler: Callback function for handling incoming messages

        Returns:
            Session ID (new or restored)
        """
        try:
            # Build WebSocket URL
            base_domain = self.base_url.split('://', 1)[1]
            ws_protocol = "wss" if self.base_url.startswith("https") else "ws"
            ws_url = f"{ws_protocol}://{base_domain}/ws/{self.client_id}"
            if session_id:
                ws_url += f"?session_id={session_id}"

            logger.info(f"Connecting to voice chat WebSocket: {ws_url}")

            # Connect to WebSocket
            self.chat_websocket = await websockets.connect(ws_url)

            # Set message handler
            if message_handler:
                self.message_handlers["default"] = message_handler

            # Start message listener
            asyncio.create_task(self._listen_voice_chat())

            logger.info(
                f"Connected to voice chat WebSocket for client: {self.client_id}"
            )
            return self.client_id

        except Exception as e:
            logger.error(f"Failed to connect to voice chat WebSocket: {e}")
            raise

    async def _listen_voice_chat(self):
        """Listen for messages from voice chat WebSocket"""
        try:
            async for message in self.chat_websocket:
                try:
                    self.stats["messages_received"] += 1
                    self.last_activity = datetime.now()
                    
                    data = json.loads(message)
                    message_type = data.get("type")

                    logger.debug(f"Received voice chat message: {message_type}")

                    # Handle session-related messages
                    if message_type in ["session_restored", "new_session_created"]:
                        self.session_id = data.get("session_id")
                        self.connection_status.session_established = True
                        self.connection_status.session_id = self.session_id
                        logger.info(f"Session established: {self.session_id}")

                    # Handle configuration response messages
                    if message_type in [
                        "onboarding_data_response",
                        "emotional_logic_response",
                        "user_preferences_response",
                    ]:
                        logger.info(
                            f"Received {message_type}: {data.get('count', 0)} items"
                        )

                    # Handle success/error messages
                    if message_type in [
                        "settings_saved",
                        "onboarding_data_saved",
                        "emotional_logic_saved",
                        "user_preferences_saved",
                    ]:
                        logger.info(f"Configuration saved: {message_type}")
                    elif message_type == "error":
                        error_msg = data.get('message', 'Unknown error')
                        logger.error(f"WebSocket error: {error_msg}")
                        await self._handle_error(Exception(error_msg), "websocket_error")

                    # Handle threat detection messages
                    if message_type == "threat_detection":
                        threat_level = data.get("threat_level", "none")
                        threat_detected = data.get("threat_detected", False)
                        logger.warning(
                            f"Threat detection: level={threat_level}, detected={threat_detected}"
                        )

                    # Handle pong messages
                    if message_type == "pong":
                        self.connection_status.last_ping = datetime.now()

                    # Call appropriate handlers
                    for handler_name, handler in self.message_handlers.items():
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(data)
                            else:
                                handler(data)
                        except Exception as handler_error:
                            logger.error(
                                f"Error in message handler {handler_name}: {handler_error}"
                            )
                            await self._handle_error(handler_error, f"message_handler_{handler_name}")

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse voice chat message: {e}")
                    await self._handle_error(e, "json_decode_voice_chat")
                except Exception as e:
                    logger.error(f"Error processing voice chat message: {e}")
                    await self._handle_error(e, "process_voice_chat_message")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Voice chat WebSocket connection closed")
            self.connection_status.voice_chat_connected = False
            if self.auto_reconnect and not self._is_closing:
                asyncio.create_task(self._auto_reconnect_websocket("voice_chat"))
        except Exception as e:
            logger.error(f"Error in voice chat message listener: {e}")
            await self._handle_error(e, "voice_chat_listener")
            if self.auto_reconnect and not self._is_closing:
                asyncio.create_task(self._auto_reconnect_websocket("voice_chat"))

    async def set_user_settings(
        self, 
        voice: Union[str, VoiceType] = VoiceType.ALLOY, 
        language: Union[str, LanguageCode] = LanguageCode.ENGLISH
    ):
        """Set user voice and language preferences"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        # Convert enums to strings if needed
        voice_str = voice.value if isinstance(voice, VoiceType) else voice
        language_str = language.value if isinstance(language, LanguageCode) else language

        message = {"type": "user_settings", "voice": voice_str, "language": language_str}

        await self._send_websocket_message(self.chat_websocket, message)
        logger.info(f"Sent user settings: voice={voice_str}, language={language_str}")

    async def _send_websocket_message(self, websocket, message: dict):
        """Send message to WebSocket with error handling and statistics"""
        try:
            await websocket.send(json.dumps(message))
            self.stats["messages_sent"] += 1
            self.last_activity = datetime.now()
        except Exception as e:
            self.stats["errors"] += 1
            await self._handle_error(e, "send_websocket_message")
            raise

    async def send_audio_chunk(self, audio_data: bytes, sample_rate: int = 48000):
        """Send audio chunk for processing"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        # Encode audio data to base64
        base64_audio = base64.b64encode(audio_data).decode("utf-8")

        message = {
            "type": "audio_chunk",
            "audio_data": base64_audio,
            "sample_rate": sample_rate,
        }

        await self.chat_websocket.send(json.dumps(message))
        logger.debug("Sent audio chunk")

    async def stop_recording(self):
        """Signal that recording has stopped"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        message = {"type": "stop_recording"}
        await self.chat_websocket.send(json.dumps(message))
        logger.info("Sent stop recording signal")

    async def ping(self):
        """Send ping to keep connection alive"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        message = {"type": "ping"}
        await self.chat_websocket.send(json.dumps(message))
        logger.debug("Sent ping")

    async def cancel_response(self, event_id: str = None):
        """Cancel current AI response"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        message = {"type": "cancel_response", "cancel": True}
        if event_id:
            message["event_id"] = event_id

        await self.chat_websocket.send(json.dumps(message))
        logger.info("Sent response cancellation request")

    # ================================
    # WebSocket Configuration Messages
    # ================================

    async def set_onboarding_data_ws(self, onboarding_data: List[Dict]):
        """Set onboarding data via WebSocket"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        message = {"type": "set_onboarding_data", "onboarding_data": onboarding_data}

        await self.chat_websocket.send(json.dumps(message))
        logger.info(
            f"Sent onboarding data via WebSocket: {len(onboarding_data)} questions"
        )

    async def set_emotional_logic_ws(self, emotional_logic: List[Dict]):
        """Set emotional logic via WebSocket"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        message = {"type": "set_emotional_logic", "emotional_logic": emotional_logic}

        await self.chat_websocket.send(json.dumps(message))
        logger.info(
            f"Sent emotional logic via WebSocket: {len(emotional_logic)} mappings"
        )

    async def set_user_preferences_ws(self, preferences: str):
        """Set user preferences via WebSocket"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        message = {"type": "set_user_preferences", "preferences": preferences}

        await self.chat_websocket.send(json.dumps(message))
        logger.info("Sent user preferences via WebSocket")

    async def get_onboarding_data_ws(self):
        """Get onboarding data via WebSocket"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        message = {"type": "get_onboarding_data"}
        await self.chat_websocket.send(json.dumps(message))
        logger.debug("Requested onboarding data via WebSocket")

    async def get_emotional_logic_ws(self):
        """Get emotional logic via WebSocket"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        message = {"type": "get_emotional_logic"}
        await self.chat_websocket.send(json.dumps(message))
        logger.debug("Requested emotional logic via WebSocket")

    async def get_user_preferences_ws(self):
        """Get user preferences via WebSocket"""
        if not self.chat_websocket:
            raise RuntimeError("Voice chat WebSocket not connected")

        message = {"type": "get_user_preferences"}
        await self.chat_websocket.send(json.dumps(message))
        logger.debug("Requested user preferences via WebSocket")

    def add_message_handler(self, handler_name: str, handler: Callable):
        """Add a message handler for voice chat messages"""
        self.message_handlers[handler_name] = handler
        logger.info(f"Added message handler: {handler_name}")

    def remove_message_handler(self, handler_name: str):
        """Remove a message handler"""
        if handler_name in self.message_handlers:
            del self.message_handlers[handler_name]
            logger.info(f"Removed message handler: {handler_name}")

    # ================================
    # WebSocket Methods - Emotion Detection
    # ================================

    async def connect_emotion_detection(self, emotion_handler: Callable = None):
        """
        Connect to emotion detection WebSocket

        Args:
            emotion_handler: Callback function for handling emotion detection results
        """
        try:
            # Build WebSocket URL
            base_domain = self.base_url.split('://', 1)[1]
            ws_protocol = "wss" if self.base_url.startswith("https") else "ws"
            ws_url = f"{ws_protocol}://{base_domain}/ws/image_emotion/{self.client_id}"

            logger.info(f"Connecting to emotion detection WebSocket: {ws_url}")

            # Connect to WebSocket
            self.emotion_websocket = await websockets.connect(ws_url)

            # Set emotion handler
            if emotion_handler:
                self.emotion_handlers["default"] = emotion_handler

            # Start message listener
            asyncio.create_task(self._listen_emotion_detection())

            logger.info(
                f"Connected to emotion detection WebSocket for client: {self.client_id}"
            )

        except Exception as e:
            logger.error(f"Failed to connect to emotion detection WebSocket: {e}")
            raise

    async def _listen_emotion_detection(self):
        """Listen for messages from emotion detection WebSocket"""
        try:
            async for message in self.emotion_websocket:
                try:
                    data = json.loads(message)

                    logger.debug(f"Received emotion detection result: {data}")

                    # Call appropriate handlers
                    for handler_name, handler in self.emotion_handlers.items():
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(data)
                            else:
                                handler(data)
                        except Exception as handler_error:
                            logger.error(
                                f"Error in emotion handler {handler_name}: {handler_error}"
                            )

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse emotion detection message: {e}")
                except Exception as e:
                    logger.error(f"Error processing emotion detection message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Emotion detection WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error in emotion detection message listener: {e}")

    async def send_image_for_emotion_detection(
        self, image_data: bytes, image_format: str = "PNG"
    ):
        """
        Send image for emotion detection

        Args:
            image_data: Raw image bytes
            image_format: Image format (PNG, JPEG, etc.)
        """
        if not self.emotion_websocket:
            raise RuntimeError("Emotion detection WebSocket not connected")

        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode("utf-8")

        # Add data URL prefix
        data_url = f"data:image/{image_format.lower()};base64,{base64_image}"

        message = {"image_bytes": data_url}

        await self.emotion_websocket.send(json.dumps(message))
        logger.info("Sent image for emotion detection")

    async def send_image_file_for_emotion_detection(self, image_path: str):
        """
        Send image file for emotion detection

        Args:
            image_path: Path to image file
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Read image file
        with open(image_path, "rb") as f:
            image_data = f.read()

        # Determine format from file extension
        image_format = image_path.suffix.upper().lstrip(".")
        if image_format == "JPG":
            image_format = "JPEG"

        await self.send_image_for_emotion_detection(image_data, image_format)

    def add_emotion_handler(self, handler_name: str, handler: Callable):
        """Add an emotion detection handler"""
        self.emotion_handlers[handler_name] = handler
        logger.info(f"Added emotion handler: {handler_name}")

    def remove_emotion_handler(self, handler_name: str):
        """Remove an emotion detection handler"""
        if handler_name in self.emotion_handlers:
            del self.emotion_handlers[handler_name]
            logger.info(f"Removed emotion handler: {handler_name}")

    # ================================
    # Connection Management
    # ================================

    async def disconnect_voice_chat(self):
        """Disconnect from voice chat WebSocket"""
        if self.chat_websocket:
            try:
                await self.chat_websocket.close()
                logger.info("Disconnected from voice chat WebSocket")
            except Exception as e:
                logger.error(f"Error disconnecting from voice chat WebSocket: {e}")
            finally:
                self.chat_websocket = None

    async def disconnect_emotion_detection(self):
        """Disconnect from emotion detection WebSocket"""
        if self.emotion_websocket:
            try:
                await self.emotion_websocket.close()
                logger.info("Disconnected from emotion detection WebSocket")
            except Exception as e:
                logger.error(
                    f"Error disconnecting from emotion detection WebSocket: {e}"
                )
            finally:
                self.emotion_websocket = None

    async def disconnect_all(self):
        """Disconnect from all WebSocket connections"""
        await self.disconnect_voice_chat()
        await self.disconnect_emotion_detection()

    # ================================
    # Utility Methods
    # ================================

    def is_voice_chat_connected(self) -> bool:
        """Check if voice chat WebSocket is connected"""
        return self.chat_websocket is not None and not self.chat_websocket.closed

    def is_emotion_detection_connected(self) -> bool:
        """Check if emotion detection WebSocket is connected"""
        return self.emotion_websocket is not None and not self.emotion_websocket.closed

    async def get_current_session_status(self) -> Dict[str, Any]:
        """Get status of current session"""
        if not self.session_id:
            raise RuntimeError("No active session")
        return await self.get_session_status(self.session_id)

    async def get_my_emotion(self) -> Dict[str, Any]:
        """Get current detected emotion for this client"""
        return await self.get_client_emotion(self.client_id)

    async def set_my_emotion(self, emotion: str) -> Dict[str, Any]:
        """Set detected emotion for this client"""
        return await self.set_client_emotion(emotion, self.client_id)


# ================================
# Convenience Classes and Functions
# ================================


class EmotionDetectionResult:
    """Container for emotion detection results"""

    def __init__(self, data: Dict[str, Any]):
        self.predicted_label = data.get("predicted_label")
        self.emotion = data.get("emotion")
        self.client_id = data.get("client_id")
        self.session_updated = data.get("session_updated", False)
        self.raw_data = data

    def __str__(self):
        return f"EmotionDetectionResult(emotion='{self.emotion}', client_id='{self.client_id}')"


class VoiceChatMessage:
    """Container for voice chat messages"""

    def __init__(self, data: Dict[str, Any]):
        self.type = data.get("type")
        self.message = data.get("message")
        self.transcript = data.get("transcript")
        self.event_id = data.get("event_id")
        self.audio_data = data.get("audio_data")
        self.session_id = data.get("session_id")
        self.is_threat = data.get("is_threat", False)
        self.threat_level = data.get("threat_level", "none")
        self.raw_data = data

    def __str__(self):
        return f"VoiceChatMessage(type='{self.type}', message='{self.message}', is_threat={self.is_threat})"


class OnboardingData:
    """Container for onboarding data"""

    def __init__(self, data: Dict[str, Any]):
        self.onboarding_data = data.get("onboarding_data", [])
        self.count = data.get("count", 0)
        self.client_id = data.get("client_id")
        self.session_id = data.get("session_id")
        self.raw_data = data

    def __str__(self):
        return f"OnboardingData(count={self.count}, client_id='{self.client_id}')"


class EmotionalLogic:
    """Container for emotional logic data"""

    def __init__(self, data: Dict[str, Any]):
        self.emotional_logic = data.get("emotional_logic", [])
        self.count = data.get("count", 0)
        self.client_id = data.get("client_id")
        self.session_id = data.get("session_id")
        self.raw_data = data

    def __str__(self):
        return f"EmotionalLogic(count={self.count}, client_id='{self.client_id}')"


class UserPreferences:
    """Container for user preferences data"""

    def __init__(self, data: Dict[str, Any]):
        self.preferences = data.get("preferences", "")
        self.client_id = data.get("client_id")
        self.session_id = data.get("session_id")
        self.raw_data = data

    def __str__(self):
        return f"UserPreferences(client_id='{self.client_id}', preferences_length={len(self.preferences)})"


class ThreatDetectionResult:
    """Container for threat detection results"""

    def __init__(self, data: Dict[str, Any]):
        self.threat_detected = data.get("threat_detected", False)
        self.threat_level = data.get("threat_level", "none")
        self.analysis = data.get("analysis", "")
        self.timestamp = data.get("timestamp", "")
        self.message = data.get("message", "")
        self.raw_data = data

    def __str__(self):
        return f"ThreatDetectionResult(detected={self.threat_detected}, level='{self.threat_level}')"


# ================================
# Synchronous Wrapper
# ================================


class SpaceverseAIClientSync:
    """
    Synchronous wrapper for SpaceverseAIClient
    
    This provides a synchronous interface for scenarios where async/await syntax
    is not preferred or possible.
    """

    def __init__(self, **kwargs):
        """Initialize synchronous client with same parameters as async client"""
        self._client = SpaceverseAIClient(**kwargs)
        self._loop = None
        self._thread = None
        self._started = False

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

    def start(self):
        """Start the event loop in a separate thread"""
        if self._started:
            return

        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        
        # Wait for loop to be ready
        while self._loop is None:
            time.sleep(0.01)
        
        self._started = True

    def stop(self):
        """Stop the event loop and thread"""
        if not self._started:
            return

        if self._loop and self._loop.is_running():
            # Schedule cleanup and stop
            future = asyncio.run_coroutine_threadsafe(self._client.disconnect_all(), self._loop)
            try:
                future.result(timeout=5)
            except:
                pass
            
            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

        self._started = False

    def _run_async(self, coro, timeout=30):
        """Run an async coroutine synchronously"""
        if not self._started:
            raise RuntimeError("Client not started. Call start() or use as context manager.")
        
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    # Synchronous versions of main methods
    def health_check(self, timeout=30) -> SystemHealth:
        """Synchronous health check"""
        return self._run_async(self._client.health_check(), timeout)

    def connect_voice_chat(self, session_id=None, message_handler=None, timeout=30):
        """Synchronous voice chat connection"""
        return self._run_async(self._client.connect_voice_chat(session_id, message_handler), timeout)

    def connect_emotion_detection(self, emotion_handler=None, timeout=30):
        """Synchronous emotion detection connection"""
        return self._run_async(self._client.connect_emotion_detection(emotion_handler), timeout)

    def set_user_settings(self, voice=VoiceType.ALLOY, language=LanguageCode.ENGLISH, timeout=10):
        """Synchronous user settings"""
        return self._run_async(self._client.set_user_settings(voice, language), timeout)

    def send_image_for_emotion_detection(self, image_data: bytes, image_format="PNG", timeout=30):
        """Synchronous image emotion detection"""
        return self._run_async(
            self._client.send_image_for_emotion_detection(image_data, image_format), 
            timeout
        )

    def get_session_status(self, session_id: str, timeout=10):
        """Synchronous session status"""
        return self._run_async(self._client.get_session_status(session_id), timeout)

    def set_client_emotion(self, emotion: Union[str, EmotionType], client_id=None, timeout=10):
        """Synchronous set client emotion"""
        emotion_str = emotion.value if isinstance(emotion, EmotionType) else emotion
        return self._run_async(self._client.set_client_emotion(emotion_str, client_id), timeout)

    def generate_onboarding_questions(self, profession: str, prompt: str, timeout=30):
        """Synchronous onboarding questions generation"""
        return self._run_async(
            self._client.generate_onboarding_questions(profession, prompt), 
            timeout
        )

    def get_connection_status(self) -> ConnectionStatus:
        """Get connection status (synchronous)"""
        return self._client.get_connection_status()

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics (synchronous)"""
        return self._client.get_statistics()

    # Properties for easy access
    @property
    def client_id(self) -> str:
        return self._client.client_id

    @property
    def session_id(self) -> Optional[str]:
        return self._client.session_id


# ================================
# Enhanced Helper Functions
# ================================


def create_client(
    base_url: str = "https://spaceverse-python-1051344022089.us-east1.run.app/",
    client_id: str = None,
    sync: bool = False,
    **kwargs
) -> Union[SpaceverseAIClient, SpaceverseAIClientSync]:
    """
    Factory function to create appropriate client type
    
    Args:
        base_url: Server base URL
        client_id: Client identifier
        sync: Whether to return synchronous client
        **kwargs: Additional client parameters
    
    Returns:
        SpaceverseAIClient or SpaceverseAIClientSync instance
    """
    client_kwargs = {"base_url": base_url, "client_id": client_id, **kwargs}
    
    if sync:
        return SpaceverseAIClientSync(**client_kwargs)
    else:
        return SpaceverseAIClient(**client_kwargs)


async def quick_health_check(base_url: str = "https://spaceverse-python-1051344022089.us-east1.run.app/") -> bool:
    """Quick health check without creating persistent client"""
    try:
        async with SpaceverseAIClient(base_url=base_url) as client:
            health = await client.health_check()
            return health.status == "healthy"
    except:
        return False


def sync_health_check(base_url: str = "https://spaceverse-python-1051344022089.us-east1.run.app/") -> bool:
    """Synchronous health check"""
    try:
        with SpaceverseAIClientSync(base_url=base_url) as client:
            health = client.health_check()
            return health.status == "healthy"
    except:
        return False


# ================================
# Usage Examples
# ================================


async def example_voice_chat():
    """Example usage of voice chat functionality"""

    async def message_handler(message_data):
        """Handle incoming voice chat messages"""
        msg = VoiceChatMessage(message_data)
        print(f"Received: {msg}")

        if msg.type == "user_transcript":
            print(f"You said: {msg.transcript}")
        elif msg.type == "ai_transcript":
            print(f"AI said: {msg.transcript}")
        elif msg.type == "session_ready":
            print("Session is ready for voice chat")

    async with SpaceverseAIClient() as client:
        # Connect to voice chat
        await client.connect_voice_chat(message_handler=message_handler)

        # Set user preferences
        await client.set_user_settings(voice="alloy", language="en")

        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            await client.ping()


async def example_emotion_detection():
    """Example usage of emotion detection functionality"""

    async def emotion_handler(emotion_data):
        """Handle emotion detection results"""
        result = EmotionDetectionResult(emotion_data)
        print(f"Detected emotion: {result}")

    async with SpaceverseAIClient() as client:
        # Connect to emotion detection
        await client.connect_emotion_detection(emotion_handler=emotion_handler)

        # Send an image for emotion detection
        await client.send_image_file_for_emotion_detection("path/to/image.jpg")

        # Keep connection alive
        await asyncio.sleep(10)


async def example_session_management():
    """Example usage of session management"""

    async with SpaceverseAIClient() as client:
        # Check server health
        health = await client.health_check()
        print(f"Server health: {health}")

        # List active sessions
        sessions = await client.list_active_sessions()
        print(f"Active sessions: {sessions['total_count']}")

        # Connect to voice chat and get session ID
        await client.connect_voice_chat()
        await asyncio.sleep(2)  # Wait for session to be established

        # Get current session status
        if client.session_id:
            status = await client.get_current_session_status()
            print(f"Current session status: {status}")

            # Get session events
            events = await client.get_session_events(client.session_id, limit=10)
            print(f"Session events: {len(events['openai_events'])}")

        # Test emotion system
        emotion_result = await client.test_dual_emotion_system(
            facial_emotion="happy",
            voice_emotion="enthusiastic",
            test_message="Tell me about your day!",
        )
        print(f"Dual emotion test result: {emotion_result}")


async def example_comprehensive_voice_chat():
    """Comprehensive example of voice chat with all features"""

    async def message_handler(message_data):
        """Handle incoming voice chat messages"""
        msg = VoiceChatMessage(message_data)
        print(f"📨 Received: {msg}")

        if msg.type == "user_transcript":
            print(f"🎤 You said: {msg.transcript}")
        elif msg.type == "ai_transcript":
            print(f"🤖 AI said: {msg.transcript}")
            if msg.is_threat:
                print(f"⚠️  Threat detected: {msg.threat_level}")
        elif msg.type == "session_ready":
            print("✅ Session is ready for voice chat")
        elif msg.type == "threat_detection":
            threat = ThreatDetectionResult(message_data)
            print(f"🚨 Threat detection: {threat}")

    async with SpaceverseAIClient() as client:
        # Connect to voice chat
        await client.connect_voice_chat(message_handler=message_handler)

        # Set user preferences
        await client.set_user_settings(voice="alloy", language="en")

        # Set onboarding data
        onboarding_data = [
            {
                "question": "What is your passion?",
                "voiceEmotion": "enthusiastic",
                "facialEmotion": "happy",
                "askOnce": True,
            },
            {
                "question": "How do you usually spend your weekends?",
                "voiceEmotion": "neutral",
                "facialEmotion": "neutral",
                "askOnce": False,
            },
        ]
        await client.set_onboarding_data_ws(onboarding_data)

        # Set emotional logic
        emotional_logic = [
            {
                "emotion": "cheerful",
                "tone": "joyful",
                "speak": "quickly",
                "compliance": "MANDATORY",
            },
            {
                "emotion": "sad",
                "tone": "empathetic",
                "speak": "softly",
                "compliance": "MANDATORY",
            },
        ]
        await client.set_emotional_logic_ws(emotional_logic)

        # Set user preferences
        user_prefs = "The user prefers formal, professional communication with technical details. They appreciate when responses include relevant examples."
        await client.set_user_preferences_ws(user_prefs)

        # Test threat detection
        await client.test_threat_detection(
            "I'm feeling really down today", threat_detected=False
        )

        # Keep connection alive
        for i in range(10):
            await asyncio.sleep(30)
            await client.ping()
            print(f"💓 Ping {i+1}/10")


async def example_ai_services():
    """Example usage of AI service endpoints"""

    async with SpaceverseAIClient() as client:
        # Generate onboarding questions
        onboarding_result = await client.generate_onboarding_questions(
            profession="Software Engineer",
            prompt="Generate questions about technical interests and work preferences",
        )
        print(f"Generated onboarding questions: {onboarding_result}")

        # Generate user preferences from chat history
        chat_history = """
        User: I love working with Python and machine learning
        AI: That's great! What specific areas of ML interest you?
        User: I'm particularly interested in computer vision and NLP
        AI: Excellent choices! Have you worked with any specific frameworks?
        User: Yes, I use TensorFlow and PyTorch regularly
        """

        preferences_result = await client.generate_user_preferences(chat_history)
        print(f"Generated user preferences: {preferences_result}")

        # Generate transcription (if you have an audio URL)
        # transcription_result = await client.generate_transcription("https://example.com/audio.mp3")
        # print(f"Generated transcription: {transcription_result}")


async def example_emotion_detection_advanced():
    """Advanced example of emotion detection with configuration"""

    async def emotion_handler(emotion_data):
        """Handle emotion detection results"""
        result = EmotionDetectionResult(emotion_data)
        print(f"😊 Detected emotion: {result}")

        # Set the detected emotion for the client
        if result.emotion:
            try:
                await client.set_my_emotion(result.emotion)
                print(f"✅ Set client emotion to: {result.emotion}")
            except Exception as e:
                print(f"❌ Failed to set emotion: {e}")

    async with SpaceverseAIClient() as client:
        # Connect to emotion detection
        await client.connect_emotion_detection(emotion_handler=emotion_handler)

        # Test different emotions
        emotions_to_test = ["happy", "sad", "angry", "neutral"]

        for emotion in emotions_to_test:
            print(f"🧪 Testing emotion: {emotion}")
            await client.set_my_emotion(emotion)
            await asyncio.sleep(2)

        # Send an image for emotion detection (if you have one)
        # await client.send_image_file_for_emotion_detection("path/to/image.jpg")

        # Keep connection alive
        await asyncio.sleep(10)


async def example_monitoring_and_debugging():
    """Example of monitoring and debugging features"""

    async with SpaceverseAIClient() as client:
        # Get concurrent status
        concurrent_status = await client.get_concurrent_status()
        print(f"📊 Concurrent status: {concurrent_status}")

        # Connect to voice chat
        await client.connect_voice_chat()
        await asyncio.sleep(2)

        # Get current session status
        if client.session_id:
            session_status = await client.get_current_session_status()
            print(f"📋 Session status: {session_status}")

            # Get session events
            events = await client.get_session_events(client.session_id, limit=5)
            print(f"📝 Session events: {len(events['openai_events'])}")

            # Get session history info
            history = await client.get_session_history_info(client.session_id)
            print(f"📚 Session history: {history}")

        # Test dual emotion system
        dual_result = await client.test_dual_emotion_system(
            facial_emotion="surprised",
            voice_emotion="excited",
            test_message="Wow, that's amazing!",
        )
        print(f"🎭 Dual emotion test: {dual_result}")


async def example_synchronous_wrapper():
    """Example usage of synchronous wrapper"""
    print("🔄 Testing Synchronous Wrapper")
    
    # Using synchronous client with context manager
    with SpaceverseAIClientSync() as client:
        # Check health
        health = client.health_check()
        print(f"🏥 Server health: {health.status}")
        
        # Connect to voice chat
        client.connect_voice_chat()
        
        # Set user settings using enums
        client.set_user_settings(voice=VoiceType.NOVA, language=LanguageCode.ENGLISH)
        
        # Set emotion
        client.set_client_emotion(EmotionType.HAPPY)
        
        # Get connection status
        status = client.get_connection_status()
        print(f"📊 Connection status: voice_chat={status.voice_chat_connected}")
        
        # Get statistics
        stats = client.get_statistics()
        print(f"📈 Messages sent: {stats['messages_sent']}")


async def example_factory_function():
    """Example using factory function"""
    print("🏭 Testing Factory Function")
    
    # Create async client
    async_client = create_client(sync=False, debug=True)
    async with async_client:
        health = await async_client.health_check()
        print(f"🏥 Async health check: {health.status}")
    
    # Create sync client
    sync_client = create_client(sync=True, auto_reconnect=True)
    with sync_client:
        health = sync_client.health_check()
        print(f"🏥 Sync health check: {health.status}")


async def example_error_handling():
    """Example with comprehensive error handling"""
    print("⚠️ Testing Error Handling")
    
    async def error_handler(error_data):
        print(f"❌ Error occurred: {error_data['error']} in context: {error_data['context']}")
    
    async with SpaceverseAIClient(debug=True, max_retries=2) as client:
        # Add error handler
        client.add_error_handler("main", error_handler)
        
        try:
            # Test with invalid URL
            health = await client.health_check()
            print(f"✅ Health check successful: {health.status}")
        except Exception as e:
            print(f"❌ Expected error: {e}")
        
        # Get error statistics
        stats = client.get_statistics()
        print(f"📊 Error count: {stats['errors']}")


async def example_advanced_features():
    """Example showcasing advanced features"""
    print("🚀 Testing Advanced Features")
    
    async with SpaceverseAIClient(
        timeout=60,
        max_retries=5,
        retry_delay=2.0,
        auto_reconnect=True,
        debug=True
    ) as client:
        # Add multiple handlers
        async def message_handler(msg):
            print(f"📨 Message: {msg.get('type', 'unknown')}")
        
        async def emotion_handler(emotion):
            print(f"😊 Emotion detected: {emotion.get('emotion', 'unknown')}")
        
        async def error_handler(error):
            print(f"❌ Error: {error['error']}")
        
        client.add_message_handler("example", message_handler)
        client.add_emotion_handler("example", emotion_handler)
        client.add_error_handler("example", error_handler)
        
        # Connect with advanced features
        await client.connect_voice_chat()
        await client.connect_emotion_detection()
        
        # Wait for connections
        connected = await client.wait_for_connection(timeout=10)
        print(f"🔗 Connected: {connected}")
        
        # Test various settings with enums
        await client.set_user_settings(VoiceType.SHIMMER, LanguageCode.ITALIAN)
        
        # Test dual emotion system
        result = await client.test_dual_emotion_system(
            facial_emotion=EmotionType.HAPPY.value,
            voice_emotion="enthusiastic",
            test_message="Testing enhanced API wrapper!"
        )
        print(f"🎭 Dual emotion test: {result}")
        
        # Get comprehensive statistics
        stats = client.get_statistics()
        print(f"📈 Statistics: {stats}")


if __name__ == "__main__":
    # Run example
    print("🚀 SpaceverseAI Enhanced API Wrapper Examples")
    print("1. Basic Voice Chat Example")
    print("2. Emotion Detection Example")
    print("3. Session Management Example")
    print("4. Comprehensive Voice Chat Example")
    print("5. AI Services Example")
    print("6. Advanced Emotion Detection Example")
    print("7. Monitoring and Debugging Example")
    print("8. Synchronous Wrapper Example")
    print("9. Factory Function Example")
    print("10. Error Handling Example")
    print("11. Advanced Features Example")

    choice = input("Enter choice (1-11): ")

    if choice == "1":
        asyncio.run(example_voice_chat())
    elif choice == "2":
        asyncio.run(example_emotion_detection())
    elif choice == "3":
        asyncio.run(example_session_management())
    elif choice == "4":
        asyncio.run(example_comprehensive_voice_chat())
    elif choice == "5":
        asyncio.run(example_ai_services())
    elif choice == "6":
        asyncio.run(example_emotion_detection_advanced())
    elif choice == "7":
        asyncio.run(example_monitoring_and_debugging())
    elif choice == "8":
        asyncio.run(example_synchronous_wrapper())
    elif choice == "9":
        asyncio.run(example_factory_function())
    elif choice == "10":
        asyncio.run(example_error_handling())
    elif choice == "11":
        asyncio.run(example_advanced_features())
    else:
        print("❌ Invalid choice")
