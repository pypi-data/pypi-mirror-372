"""
SpaceVerse AI - Advanced Real-Time Voice Chat System

A comprehensive Python client library for the SpaceVerse AI Voice Chat Application.
Provides both synchronous and asynchronous interfaces for real-time voice chat,
emotion detection, session management, and AI services.

Examples:
    Basic usage:
        >>> import asyncio
        >>> from spaceverseai import SpaceverseAIClient, VoiceType, LanguageCode
        >>> 
        >>> async def main():
        ...     async with SpaceverseAIClient() as client:
        ...         await client.connect_voice_chat()
        ...         await client.set_user_settings(VoiceType.ALLOY, LanguageCode.ENGLISH)
        >>> 
        >>> asyncio.run(main())

    Synchronous usage:
        >>> from spaceverseai import SpaceverseAIClientSync, EmotionType
        >>> 
        >>> with SpaceverseAIClientSync() as client:
        ...     health = client.health_check()
        ...     client.connect_voice_chat()
        ...     client.set_client_emotion(EmotionType.HAPPY)
"""

__version__ = "1.0.0"
__author__ = "SpaceVerse AI Team"
__email__ = "support@spaceverse.ai"
__license__ = "MIT"
__url__ = "https://github.com/spaceverse-ai/spaceverse-ai"

# Import main classes and functions
from .api_wrapper import (
    # Main client classes
    SpaceverseAIClient,
    SpaceverseAIClientSync,
    
    # Enums for type safety
    VoiceType,
    LanguageCode,
    EmotionType,
    ThreatLevel,
    
    # Data classes
    ConnectionStatus,
    SystemHealth,
    EmotionDetectionResult,
    VoiceChatMessage,
    OnboardingData,
    EmotionalLogic,
    UserPreferences,
    ThreatDetectionResult,
    
    # Utility functions
    create_client,
    quick_health_check,
    sync_health_check,
)

# Import example usage for console script
from . import example_usage

# Define what gets imported with "from spaceverseai import *"
__all__ = [
    # Main classes
    "SpaceverseAIClient",
    "SpaceverseAIClientSync",
    
    # Enums
    "VoiceType",
    "LanguageCode", 
    "EmotionType",
    "ThreatLevel",
    
    # Data classes
    "ConnectionStatus",
    "SystemHealth",
    "EmotionDetectionResult",
    "VoiceChatMessage",
    "OnboardingData",
    "EmotionalLogic",
    "UserPreferences",
    "ThreatDetectionResult",
    
    # Utility functions
    "create_client",
    "quick_health_check",
    "sync_health_check",
    
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
]

# Package metadata
__package_info__ = {
    "name": "spaceverseai",
    "version": __version__,
    "description": "Advanced Real-Time Voice Chat System with Emotion Detection and AI Integration",
    "author": __author__,
    "author_email": __email__,
    "license": __license__,
    "url": __url__,
    "keywords": ["ai", "voice-chat", "emotion-detection", "openai", "websocket", "real-time"],
    "python_requires": ">=3.8",
}

def get_version():
    """Get the current version of SpaceVerse AI."""
    return __version__

def get_info():
    """Get package information."""
    return __package_info__.copy()

# Print welcome message for interactive sessions
def _welcome():
    """Print welcome message."""
    print(f"""
🚀 SpaceVerse AI v{__version__} - Advanced Real-Time Voice Chat System

Quick Start:
  from spaceverseai import SpaceverseAIClient, VoiceType
  
  # Async usage
  async with SpaceverseAIClient() as client:
      await client.connect_voice_chat()
      
  # Sync usage  
  from spaceverseai import SpaceverseAIClientSync
  with SpaceverseAIClientSync() as client:
      health = client.health_check()

Documentation: {__url__}/blob/main/API_Wrapper/API_WRAPPER_README.md
""")

# Show welcome message in interactive mode
import sys
if hasattr(sys, 'ps1'):  # Interactive mode
    _welcome()
