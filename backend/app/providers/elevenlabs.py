import os
import io
import logging
from typing import Optional
import requests
from app.providers.base import VoiceProvider

logger = logging.getLogger(__name__)

# Supported languages mapping (ISO 639-1 codes)
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ru": "Russian",
    "ja": "Japanese",
    "zh": "Chinese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "tr": "Turkish",
    "pl": "Polish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "fa": "Persian",
    "ur": "Urdu",
    "sv": "Swedish",
    "da": "Danish",
    "no": "Norwegian",
    "fi": "Finnish",
    "cs": "Czech",
    "hu": "Hungarian",
    "ro": "Romanian",
    "el": "Greek",
    "uk": "Ukrainian",
    "he": "Hebrew",
}


class ElevenLabsVoiceProvider(VoiceProvider):
    """ElevenLabs Voice Provider with TTS and STT capabilities."""

    provider_name = "elevenlabs"

    def __init__(self):
        """Initialize the ElevenLabs provider."""
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY environment variable not set")

        self.base_url = "https://api.elevenlabs.io/v1"
        self.tts_model = "eleven_multilingual_v2"  # Supports 29 languages
        self.stt_model = "scribe_v2"  # Supports 90+ languages
        self.default_voice_id = os.getenv("ELEVENLABS_DEFAULT_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        self.output_format = "mp3_44100_128"

    def synthesize(self, text: str, language: str = "en", voice_id: Optional[str] = None) -> bytes:
        """
        Convert text to speech in the specified language.

        Args:
            text: The input text to synthesize
            language: ISO 639-1 language code (default: "en")
            voice_id: Optional voice ID (uses default if not provided)

        Returns:
            Audio bytes in MP3 format
        """
        if not self.api_key:
            logger.error("ELEVENLABS_API_KEY not configured")
            return b""

        if not text or not text.strip():
            logger.warning("Empty text provided for synthesis")
            return b""

        voice_id = voice_id or self.default_voice_id

        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "text": text,
                "model_id": self.tts_model,
                "language_code": language,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                logger.info(f"Successfully synthesized text in {language}")
                return response.content
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
                return b""

        except requests.exceptions.Timeout:
            logger.error("TTS request timeout")
            return b""
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS request failed: {str(e)}")
            return b""
        except Exception as e:
            logger.error(f"Unexpected error in synthesize: {str(e)}")
            return b""

    def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
        """
        Convert speech to text from audio bytes.

        Args:
            audio_bytes: The audio data as bytes
            language: Optional ISO 639-1 language code for hint (auto-detected if not provided)

        Returns:
            Transcribed text
        """
        if not self.api_key:
            logger.error("ELEVENLABS_API_KEY not configured")
            return ""

        if not audio_bytes:
            logger.warning("Empty audio provided for transcription")
            return ""

        try:
            url = f"{self.base_url}/speech-to-text"
            headers = {
                "xi-api-key": self.api_key
            }

            files = {
                "file": ("audio.mp3", io.BytesIO(audio_bytes), "audio/mpeg")
            }

            data = {
                "model_id": self.stt_model,
                "language": language if language and language in SUPPORTED_LANGUAGES else "auto"
            }

            response = requests.post(url, files=files, data=data, headers=headers, timeout=60)

            if response.status_code == 200:
                result = response.json()
                transcribed_text = result.get("text", "")
                detected_language = result.get("language", "unknown")
                logger.info(f"Successfully transcribed audio (detected: {detected_language})")
                return transcribed_text
            else:
                logger.error(f"STT API error: {response.status_code} - {response.text}")
                return ""

        except requests.exceptions.Timeout:
            logger.error("STT request timeout")
            return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"STT request failed: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error in transcribe: {str(e)}")
            return ""

    def process_input(self, input_data, input_type: str = "text", input_language: str = "en") -> tuple[str, bytes]:
        """
        Process user input (text or audio) and return both text and audio output.

        Args:
            input_data: Either text (str) or audio bytes
            input_type: "text" or "audio"
            input_language: Language code of the input

        Returns:
            Tuple of (transcribed_text, synthesized_audio_bytes)
        """
        try:
            # Step 1: Extract text from input
            if input_type == "audio":
                if not isinstance(input_data, bytes):
                    logger.error("Audio input must be bytes")
                    return "", b""
                extracted_text = self.transcribe(input_data, input_language)
            elif input_type == "text":
                if not isinstance(input_data, str):
                    logger.error("Text input must be string")
                    return "", b""
                extracted_text = input_data.strip()
            else:
                logger.error(f"Unknown input type: {input_type}")
                return "", b""

            if not extracted_text:
                logger.warning(f"No text extracted from {input_type} input")
                return "", b""

            # Step 2: Generate audio output from extracted text
            audio_output = self.synthesize(extracted_text, language=input_language)

            return extracted_text, audio_output

        except Exception as e:
            logger.error(f"Error in process_input: {str(e)}")
            return "", b""

    def get_supported_languages(self) -> dict[str, str]:
        """Return dictionary of supported language codes and names."""
        return SUPPORTED_LANGUAGES.copy()

    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language code is supported."""
        return language_code in SUPPORTED_LANGUAGES


# Example usage and direct output generation
if __name__ == "__main__":
    import sys

    # Initialize provider
    provider = ElevenLabsVoiceProvider()

    print("=== ElevenLabs Voice Provider Demo ===\n")

    # Display supported languages
    print("Supported Languages:")
    for code, name in sorted(provider.get_supported_languages().items()):
        print(f"  {code}: {name}")

    print("\n--- Text-to-Speech Example ---")
    test_text = "Hello, this is a test of the ElevenLabs text to speech system."
    print(f"Input Text: {test_text}")
    audio = provider.synthesize(test_text, language="en")
    print(f"Audio Generated: {len(audio)} bytes")

    # Save example output if audio was generated
    if audio:
        output_file = "output_demo.mp3"
        with open(output_file, "wb") as f:
            f.write(audio)
        print(f"Audio saved to {output_file}")

    print("\n--- Speech-to-Text Example ---")
    if audio:
        text_result = provider.transcribe(audio, language="en")
        print(f"Transcribed Text: {text_result}")

    print("\n--- Full Process Example (Text Input) ---")
    extracted, audio_out = provider.process_input("How are you today?", input_type="text", input_language="en")
    print(f"Extracted Text: {extracted}")
    print(f"Audio Output: {len(audio_out)} bytes")