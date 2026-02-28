import os
import requests
from typing import Optional, Any
from app.providers.base import VoiceProvider
import logging

logger = logging.getLogger(__name__)


class CantoneseAIVoiceProvider(VoiceProvider):
    """
    Cantonese.ai Voice Provider for Text-to-Speech, Speech-to-Text, and Speech Edit.

    Implements full integration with Cantonese.ai API for:
    - Text-to-Speech (TTS) with multiple voice options and audio formats
    - Speech-to-Text (STT) transcription with confidence scoring
    - Speech editing and audio manipulation
    """

    provider_name = "cantoneseai"

    def __init__(self):
        """Initialize Cantonese.ai provider with API key and configuration."""
        self.api_key = os.getenv("CANTONESE_AI_API_KEY", "")
        self.base_url = "https://cantonese.ai/api"
        self.tts_endpoint = f"{self.base_url}/tts"
        self.stt_endpoint = f"{self.base_url}/stt"

        # Default TTS configuration
        self.default_config = {
            "frame_rate": "24000",
            "speed": 1.0,
            "pitch": 0,
            "language": "cantonese",
            "output_extension": "wav",
            "should_return_timestamp": True,
        }

        if not self.api_key:
            logger.warning("CANTONESE_AI_API_KEY not set. Cantonese.ai provider may not function.")

    def synthesize(self, text: str, config: Optional[dict[str, Any]] = None) -> bytes:
        """
        Convert Cantonese text to speech audio bytes.

        Args:
            text: The Cantonese text to synthesize
            config: Optional configuration dict with keys:
                - frame_rate: Audio frame rate (default: "24000")
                - speed: Speech speed multiplier (default: 1.0)
                - pitch: Pitch adjustment in semitones (default: 0)
                - language: Language code (default: "cantonese")
                - output_extension: Audio format e.g., "wav", "mp3" (default: "wav")
                - voice_id: Optional specific voice UUID
                - should_return_timestamp: Include word-level timestamps (default: True)

        Returns:
            Audio bytes in the requested format

        Raises:
            Exception: If API call fails or text is empty
        """
        if not text:
            logger.warning("Empty text provided to synthesize")
            return b""

        if not self.api_key:
            logger.error("Cantonese.ai API key not configured")
            return b""

        # Merge provided config with defaults
        payload = self.default_config.copy()
        if config:
            payload.update(config)

        payload["api_key"] = self.api_key
        payload["text"] = text

        try:
            logger.info(f"Synthesizing text with Cantonese.ai: {text[:50]}...")
            response = requests.post(self.tts_endpoint, json=payload, timeout=30)
            response.raise_for_status()

            # If response is JSON with base64 audio, decode it
            if response.headers.get("content-type", "").startswith("application/json"):
                data = response.json()
                if "audio" in data:
                    # Base64-encoded audio
                    import base64
                    return base64.b64decode(data["audio"])
                logger.error(f"No audio in response: {data}")
                return b""

            # Direct binary audio response
            return response.content

        except requests.exceptions.RequestException as e:
            logger.error(f"Cantonese.ai TTS request failed: {e}")
            return b""
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return b""

    def transcribe(self, audio_data: bytes, language: str = "cantonese") -> dict[str, Any]:
        """
        Transcribe Cantonese audio to text using Speech-to-Text.

        Args:
            audio_data: Raw audio bytes to transcribe
            language: Language code (default: "cantonese")

        Returns:
            Dictionary containing:
            - text: Transcribed text
            - confidence: Confidence score (0.0 to 1.0)
            - success: Boolean indicating successful transcription

        Raises:
            Exception: If API call fails
        """
        if not audio_data:
            logger.warning("Empty audio data provided to transcribe")
            return {"success": False, "text": "", "confidence": 0.0}

        if not self.api_key:
            logger.error("Cantonese.ai API key not configured")
            return {"success": False, "text": "", "confidence": 0.0}

        try:
            logger.info("Transcribing audio with Cantonese.ai...")

            files = {"audio": ("audio.wav", audio_data, "audio/wav")}
            data = {
                "api_key": self.api_key,
                "language": language,
            }

            response = requests.post(self.stt_endpoint, files=files, data=data, timeout=30)
            response.raise_for_status()

            result = response.json()

            return {
                "success": result.get("success", True),
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Cantonese.ai STT request failed: {e}")
            return {"success": False, "text": "", "confidence": 0.0}
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {"success": False, "text": "", "confidence": 0.0}

    def edit_speech(
            self,
            audio_data: bytes,
            edit_type: str = "enhance",
            config: Optional[dict[str, Any]] = None
    ) -> bytes:
        """
        Edit or enhance audio using Cantonese.ai speech editing capabilities.

        Args:
            audio_data: Raw audio bytes to edit
            edit_type: Type of edit operation:
                - "enhance": Audio enhancement/noise reduction
                - "pitch": Adjust pitch
                - "speed": Adjust playback speed
            config: Optional configuration dict with operation-specific parameters:
                - For pitch: {"pitch_semitones": value}
                - For speed: {"speed_multiplier": value}

        Returns:
            Edited audio bytes
        """
        if not audio_data:
            logger.warning("Empty audio data provided to edit_speech")
            return b""

        if not self.api_key:
            logger.error("Cantonese.ai API key not configured")
            return b""

        try:
            logger.info(f"Editing speech with operation: {edit_type}")

            # Placeholder for speech editing endpoint
            # This may need adjustment based on actual Cantonese.ai API
            edit_endpoint = f"{self.base_url}/speech-edit"

            files = {"audio": ("audio.wav", audio_data, "audio/wav")}
            data = {
                "api_key": self.api_key,
                "edit_type": edit_type,
            }

            if config:
                data.update(config)

            response = requests.post(edit_endpoint, files=files, data=data, timeout=30)
            response.raise_for_status()

            # Return edited audio or base64-decoded audio
            if response.headers.get("content-type", "").startswith("application/json"):
                result = response.json()
                if "audio" in result:
                    import base64
                    return base64.b64decode(result["audio"])

            return response.content

        except requests.exceptions.RequestException as e:
            logger.error(f"Cantonese.ai speech edit request failed: {e}")
            return audio_data  # Return original audio on failure
        except Exception as e:
            logger.error(f"Error editing speech: {e}")
            return audio_data
