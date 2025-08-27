#!/usr/bin/env python3
"""
SpaceverseAI API Wrapper - Example Usage

This script demonstrates how to use the API wrapper for various tasks:
1. Basic voice chat connection
2. Emotion detection from images
3. Session management
4. Dual emotion system testing
"""

import asyncio
import logging
import time
from pathlib import Path
from .api_wrapper import (
    SpaceverseAIClient, 
    SpaceverseAIClientSync,
    VoiceChatMessage, 
    EmotionDetectionResult,
    VoiceType,
    LanguageCode,
    EmotionType,
    ThreatLevel,
    ConnectionStatus,
    SystemHealth,
    create_client,
    sync_health_check,
    quick_health_check
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpaceverseAIDemo:
    """Demonstration class for SpaceverseAI API wrapper functionality"""

    def __init__(self, server_url=None):
        self.server_url = server_url  # None will use the default production URL
        self.client = None

    async def demo_health_check(self):
        """Demonstrate health check and basic API calls"""
        print("\n🏥 === HEALTH CHECK DEMO ===")

        # Test quick health check helper
        print("🚀 Testing quick health check...")
        is_healthy = await quick_health_check()
        print(f"✅ Quick health check: {'Healthy' if is_healthy else 'Unhealthy'}")

        # Test sync health check helper
        print("🔄 Testing sync health check...")
        is_healthy_sync = sync_health_check()
        print(f"✅ Sync health check: {'Healthy' if is_healthy_sync else 'Unhealthy'}")

        async with SpaceverseAIClient(debug=True) as client:
            try:
                # Check server health with enhanced response
                health = await client.health_check()
                print(f"✅ Server Health: {health.status}")
                print(f"📝 Message: {health.message}")
                print(f"🔗 Connections: {health.connections}")

                # Get concurrent status
                concurrent = await client.get_concurrent_status()
                print(f"📊 Concurrent Status: {concurrent}")

                # List active sessions
                sessions = await client.list_active_sessions()
                print(f"📊 Active Sessions: {sessions['total_count']}")

                # Get client statistics
                stats = client.get_statistics()
                print(f"📈 Client Stats: Messages sent={stats['messages_sent']}, Uptime={stats['uptime_string']}")

                return True

            except Exception as e:
                print(f"❌ Health check failed: {e}")
                return False

    async def demo_voice_chat(self):
        """Demonstrate voice chat WebSocket connection"""
        print("\n🎤 === VOICE CHAT DEMO ===")

        async def message_handler(data):
            """Handle incoming voice chat messages"""
            msg = VoiceChatMessage(data)

            if msg.type == "session_restored":
                print(f"🔄 Session Restored: {msg.session_id}")
            elif msg.type == "new_session_created":
                print(f"🆕 New Session Created: {msg.session_id}")
            elif msg.type == "session_ready":
                print(f"✅ {msg.message}")
            elif msg.type == "settings_saved":
                print(f"⚙️ Settings Saved: {msg.message}")
            elif msg.type == "user_transcript":
                print(f"👤 You said: {msg.transcript}")
            elif msg.type == "ai_transcript":
                print(f"🤖 AI said: {msg.transcript}")
            elif msg.type == "speech_started":
                print("🎙️ Speech detection started")
            elif msg.type == "speech_stopped":
                print("⏹️ Speech detection stopped")
            elif msg.type == "audio_chunk":
                print("🎵 Received audio chunk for playback")
            elif msg.type == "error":
                print(f"❌ Error: {msg.message}")
            else:
                print(f"📨 Message: {msg.type} - {msg.message}")

        async with SpaceverseAIClient() as client:
            try:
                # Connect to voice chat
                print("🔌 Connecting to voice chat...")
                await client.connect_voice_chat(message_handler=message_handler)

                # Wait a moment for session to be established
                await asyncio.sleep(2)

                # Set user preferences using enums
                print("⚙️ Setting user preferences...")
                await client.set_user_settings(voice=VoiceType.ALLOY, language=LanguageCode.ENGLISH)

                # Get session status
                if client.session_id:
                    print(f"📋 Session ID: {client.session_id}")
                    status = await client.get_current_session_status()
                    print(f"📊 Session Status: {status['conversation_state']}")
                    print(f"🤖 OpenAI Connected: {status['openai_connected']}")

                # Keep connection alive and demonstrate ping
                print("💓 Sending ping to keep connection alive...")
                await client.ping()

                # Wait a bit to see any incoming messages
                print("⏳ Waiting for messages (5 seconds)...")
                await asyncio.sleep(5)

                print("✅ Voice chat demo completed")

            except Exception as e:
                print(f"❌ Voice chat demo failed: {e}")

    async def demo_emotion_detection(self):
        """Demonstrate emotion detection functionality"""
        print("\n😊 === EMOTION DETECTION DEMO ===")

        async def emotion_handler(data):
            """Handle emotion detection results"""
            if data.get("type") == "error":
                print(f"❌ Emotion Error: {data.get('message', 'Unknown error')}")
            else:
                result = EmotionDetectionResult(data)
                print(f"🎭 Detected Emotion: {result.emotion}")
                print(f"👤 Client ID: {result.client_id}")
                print(f"🔄 Session Updated: {result.session_updated}")

        async with SpaceverseAIClient() as client:
            try:
                # Connect to emotion detection
                print("🔌 Connecting to emotion detection...")
                await client.connect_emotion_detection(emotion_handler=emotion_handler)

                # Test with manual emotion setting using enums
                print("🧪 Testing manual emotion setting...")
                result = await client.set_my_emotion(EmotionType.HAPPY.value)
                print(f"✅ Set emotion result: {result['emotion_set']}")

                # Get current emotion
                current_emotion = await client.get_my_emotion()
                print(f"🔍 Current emotion: {current_emotion['detected_emotion']}")

                # Test dual emotion system
                print("🔄 Testing dual emotion system...")
                dual_result = await client.test_dual_emotion_system(
                    facial_emotion=EmotionType.SURPRISE.value,
                    voice_emotion="enthusiastic",
                    test_message="This is a test of the dual emotion system!",
                )
                print(f"✅ Dual emotion test: {dual_result['message']}")

                # Wait for any emotion processing
                await asyncio.sleep(3)

                print("✅ Emotion detection demo completed")

            except Exception as e:
                print(f"❌ Emotion detection demo failed: {e}")

    async def demo_session_management(self):
        """Demonstrate session management and monitoring"""
        print("\n📊 === SESSION MANAGEMENT DEMO ===")

        async with SpaceverseAIClient() as client:
            try:
                # Create a new session by connecting
                await client.connect_voice_chat()
                await asyncio.sleep(2)  # Wait for session creation

                if client.session_id:
                    session_id = client.session_id
                    print(f"📋 Created session: {session_id}")

                    # Get detailed session status
                    status = await client.get_session_status(session_id)
                    print(f"📊 Session Details:")
                    print(f"  - Connected: {status['connected']}")
                    print(f"  - OpenAI Connected: {status['openai_connected']}")
                    print(f"  - Conversation State: {status['conversation_state']}")
                    print(f"  - Settings: {status['settings']}")

                    # Get session events
                    events = await client.get_session_events(session_id, limit=5)
                    print(f"🔖 Session Events: {len(events['openai_events'])}")

                    # Get session history info
                    history_info = await client.get_session_history_info(session_id)
                    print(
                        f"📚 History managed by: {history_info['history_managed_by']}"
                    )
                    print(
                        f"🤖 OpenAI Conversation ID: {history_info.get('openai_conversation_id', 'Not set')}"
                    )

                # List all sessions
                all_sessions = await client.list_active_sessions()
                print(f"📋 Total active sessions: {all_sessions['total_count']}")

                print("✅ Session management demo completed")

            except Exception as e:
                print(f"❌ Session management demo failed: {e}")

    async def demo_error_handling(self):
        """Demonstrate error handling"""
        print("\n⚠️ === ERROR HANDLING DEMO ===")

        async with SpaceverseAIClient() as client:
            # Test invalid session ID
            try:
                await client.get_session_status("invalid-session-id")
            except ValueError as e:
                print(f"✅ Caught expected error: {e}")

            # Test invalid client ID
            try:
                await client.get_client_emotion("invalid-client-id")
            except ValueError as e:
                print(f"✅ Caught expected error: {e}")

            # Test WebSocket operation without connection
            try:
                await client.ping()
            except RuntimeError as e:
                print(f"✅ Caught expected error: {e}")

        print("✅ Error handling demo completed")

    async def demo_synchronous_wrapper(self):
        """Demonstrate synchronous wrapper functionality"""
        print("\n🔄 === SYNCHRONOUS WRAPPER DEMO ===")

        # Test factory function
        print("🏭 Testing factory function...")
        sync_client = create_client(sync=True, debug=True)

        try:
            with sync_client:
                # Test synchronous operations
                print("🏥 Synchronous health check...")
                health = sync_client.health_check()
                print(f"✅ Server Health: {health.status}")

                # Test synchronous voice chat connection
                print("🎤 Connecting to voice chat synchronously...")
                sync_client.connect_voice_chat()

                # Set user settings
                print("⚙️ Setting user preferences...")
                sync_client.set_user_settings(voice=VoiceType.NOVA, language=LanguageCode.ENGLISH)

                # Set emotion
                print("😊 Setting emotion...")
                sync_client.set_client_emotion(EmotionType.HAPPY)

                # Get connection status
                status = sync_client.get_connection_status()
                print(f"📊 Connection Status: Voice Chat={status.voice_chat_connected}")

                # Get statistics
                stats = sync_client.get_statistics()
                print(f"📈 Statistics: {stats}")

                print("✅ Synchronous wrapper demo completed")

        except Exception as e:
            print(f"❌ Synchronous wrapper demo failed: {e}")

    async def demo_advanced_features(self):
        """Demonstrate advanced features like error handling, statistics, etc."""
        print("\n🚀 === ADVANCED FEATURES DEMO ===")

        # Create client with advanced configuration
        async with SpaceverseAIClient(
            timeout=60,
            max_retries=3,
            retry_delay=1.5,
            auto_reconnect=True,
            debug=True
        ) as client:
            try:
                # Add error handler
                async def error_handler(error_data):
                    print(f"🔔 Error Alert: {error_data['error']} in {error_data['context']}")

                client.add_error_handler("demo", error_handler)

                # Test connection status tracking
                print("📊 Testing connection status...")
                status = client.get_connection_status()
                print(f"Initial status: {status}")

                # Connect and test auto-reconnect preparation
                await client.connect_voice_chat()
                await client.connect_emotion_detection()

                # Wait for connections
                print("⏳ Waiting for connections...")
                connected = await client.wait_for_connection(timeout=10)
                print(f"🔗 Connected successfully: {connected}")

                # Test enhanced settings with different voices
                voice_tests = [VoiceType.ECHO, VoiceType.FABLE, VoiceType.SHIMMER]
                for voice in voice_tests:
                    print(f"🎵 Testing voice: {voice.value}")
                    await client.set_user_settings(voice=voice, language=LanguageCode.ENGLISH)
                    await asyncio.sleep(1)

                # Test emotion types
                emotion_tests = [EmotionType.HAPPY, EmotionType.SAD, EmotionType.SURPRISE]
                for emotion in emotion_tests:
                    print(f"😊 Testing emotion: {emotion.value}")
                    await client.set_client_emotion(emotion.value)
                    await asyncio.sleep(1)

                # Get final statistics
                final_stats = client.get_statistics()
                print(f"📈 Final Statistics:")
                print(f"  - Messages sent: {final_stats['messages_sent']}")
                print(f"  - Messages received: {final_stats['messages_received']}")
                print(f"  - Errors: {final_stats['errors']}")
                print(f"  - Uptime: {final_stats['uptime_string']}")

                print("✅ Advanced features demo completed")

            except Exception as e:
                print(f"❌ Advanced features demo failed: {e}")

    async def demo_ai_services(self):
        """Demonstrate AI service endpoints"""
        print("\n🤖 === AI SERVICES DEMO ===")

        async with SpaceverseAIClient() as client:
            try:
                # Generate onboarding questions
                print("📝 Generating onboarding questions...")
                onboarding_result = await client.generate_onboarding_questions(
                    profession="Software Engineer",
                    prompt="Generate questions about programming languages and development experience"
                )
                print(f"✅ Generated {len(onboarding_result.get('questions', []))} onboarding questions")

                # Generate user preferences from sample data
                print("🎯 Generating user preferences...")
                sample_chat = """
                User: I love working with Python and machine learning
                AI: That's interesting! What ML frameworks do you prefer?
                User: I mainly use TensorFlow and PyTorch for deep learning projects
                AI: Great choices! Do you work on any specific domains?
                User: Mostly computer vision and natural language processing
                """
                
                preferences_result = await client.generate_user_preferences(sample_chat)
                print(f"✅ Generated preferences: {preferences_result.get('preferences', 'None')[:100]}...")

                print("✅ AI services demo completed")

            except Exception as e:
                print(f"❌ AI services demo failed: {e}")

    async def run_all_demos(self):
        """Run all demonstrations in sequence"""
        print("🚀 Starting SpaceverseAI API Wrapper Demonstrations")
        print("=" * 60)

        # Check if server is accessible first
        if not await self.demo_health_check():
            print("❌ Server not accessible. Make sure the SpaceVerse AI server is running.")
            return

        # Run all demos
        await self.demo_voice_chat()
        await self.demo_emotion_detection()
        await self.demo_session_management()
        await self.demo_ai_services()
        await self.demo_synchronous_wrapper()
        await self.demo_advanced_features()
        await self.demo_error_handling()

        print("\n🎉 All demonstrations completed!")
        print("💡 Check the API_WRAPPER_README.md for more detailed usage examples.")


async def interactive_demo():
    """Interactive demo allowing user to choose which features to test"""
    demo = SpaceverseAIDemo()

    while True:
        print("\n🎮 SpaceverseAI API Wrapper - Interactive Demo")
        print("=" * 50)
        print("1. Health Check & Basic API")
        print("2. Voice Chat WebSocket")
        print("3. Emotion Detection")
        print("4. Session Management")
        print("5. AI Services")
        print("6. Synchronous Wrapper")
        print("7. Advanced Features")
        print("8. Error Handling")
        print("9. Run All Demos")
        print("0. Exit")
        print("-" * 50)

        try:
            choice = input("Select option (0-9): ").strip()

            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                await demo.demo_health_check()
            elif choice == "2":
                await demo.demo_voice_chat()
            elif choice == "3":
                await demo.demo_emotion_detection()
            elif choice == "4":
                await demo.demo_session_management()
            elif choice == "5":
                await demo.demo_ai_services()
            elif choice == "6":
                await demo.demo_synchronous_wrapper()
            elif choice == "7":
                await demo.demo_advanced_features()
            elif choice == "8":
                await demo.demo_error_handling()
            elif choice == "9":
                await demo.run_all_demos()
            else:
                print("❌ Invalid choice. Please select 0-9.")

        except KeyboardInterrupt:
            print("\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Demo error: {e}")


async def main_async():
    """Async main entry point"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_demo()
    else:
        # Run all demos automatically
        demo = SpaceverseAIDemo()
        await demo.run_all_demos()


def main():
    """Main entry point for console script"""
    print("SpaceVerse AI API Wrapper - Example Usage")
    print("Use --interactive flag for interactive mode")
    print("-" * 50)

    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n👋 Example interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
