"""
Text-to-Speech Engine
Handles multilingual speech generation with multiple TTS backends
"""

import os
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import io
import tempfile

# TTS Libraries
import gtts
import pyttsx3
try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False

# Audio processing
import librosa
import soundfile as sf
from pydub import AudioSegment
import numpy as np
from loguru import logger

from config.settings import settings


@dataclass
class AudioData:
    """Data class for audio information"""
    audio_array: np.ndarray
    sample_rate: int
    duration: float
    file_path: Optional[str] = None
    phonemes: Optional[List[Dict]] = None
    emotions: Optional[List[Dict]] = None
    metadata: Optional[Dict[str, Any]] = None


class TTSEngine:
    """Advanced Text-to-Speech engine with multiple backends"""
    
    def __init__(self):
        self.cache_dir = settings.TTS_CACHE_DIR
        self.cache_enabled = settings.TTS_CACHE_ENABLED
        self.supported_engines = ["gtts", "pyttsx3"]
        
        if COQUI_AVAILABLE:
            self.supported_engines.append("coqui")
            
        self._initialize_engines()
        logger.info(f"TTS Engine initialized with backends: {self.supported_engines}")
    
    def _initialize_engines(self):
        """Initialize TTS engines"""
        self.engines = {}
        
        # Initialize gTTS (always available)
        self.engines["gtts"] = {"initialized": True}
        
        # Initialize pyttsx3
        try:
            engine = pyttsx3.init()
            self.engines["pyttsx3"] = {
                "initialized": True,
                "engine": engine
            }
            self._configure_pyttsx3(engine)
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3: {e}")
            self.engines["pyttsx3"] = {"initialized": False}
        
        # Initialize Coqui TTS if available
        if COQUI_AVAILABLE:
            try:
                # Use a lightweight multilingual model
                tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
                self.engines["coqui"] = {
                    "initialized": True,
                    "model": tts
                }
            except Exception as e:
                logger.warning(f"Failed to initialize Coqui TTS: {e}")
                self.engines["coqui"] = {"initialized": False}
    
    def _configure_pyttsx3(self, engine):
        """Configure pyttsx3 engine settings"""
        try:
            # Set speech rate
            rate = engine.getProperty('rate')
            engine.setProperty('rate', settings.VOICE_CONFIGS["pyttsx3"]["rate"])
            
            # Set volume
            volume = engine.getProperty('volume')
            engine.setProperty('volume', settings.VOICE_CONFIGS["pyttsx3"]["volume"])
            
            # Get available voices
            voices = engine.getProperty('voices')
            if voices:
                # Try to set a good default voice
                for voice in voices:
                    if 'english' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                        
        except Exception as e:
            logger.warning(f"Failed to configure pyttsx3: {e}")
    
    async def generate_speech(
        self,
        text: str,
        language: str = "en",
        voice_style: str = "default",
        engine: str = "gtts"
    ) -> AudioData:
        """
        Generate speech from text using specified engine
        
        Args:
            text: Text to convert to speech
            language: Language code (en/hi)
            voice_style: Voice style preference
            engine: TTS engine to use
            
        Returns:
            AudioData object with generated speech
        """
        try:
            logger.info(f"Generating speech with {engine} for language {language}")
            
            # Check cache first
            if self.cache_enabled:
                cached_audio = await self._check_cache(text, language, voice_style, engine)
                if cached_audio:
                    logger.info("Using cached audio")
                    return cached_audio
            
            # Generate speech based on engine
            if engine == "gtts":
                audio_data = await self._generate_with_gtts(text, language)
            elif engine == "pyttsx3":
                audio_data = await self._generate_with_pyttsx3(text, language)
            elif engine == "coqui" and COQUI_AVAILABLE:
                audio_data = await self._generate_with_coqui(text, language)
            else:
                logger.warning(f"Engine {engine} not available, falling back to gTTS")
                audio_data = await self._generate_with_gtts(text, language)
            
            # Post-process audio
            audio_data = await self._post_process_audio(audio_data)
            
            # Cache the result
            if self.cache_enabled:
                await self._cache_audio(audio_data, text, language, voice_style, engine)
            
            logger.success(f"Speech generated successfully, duration: {audio_data.duration:.2f}s")
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise
    
    async def _generate_with_gtts(self, text: str, language: str) -> AudioData:
        """Generate speech using Google Text-to-Speech"""
        try:
            # Map language codes
            lang_map = {"en": "en", "hi": "hi"}
            gtts_lang = lang_map.get(language, "en")
            
            # Get TLD for better pronunciation
            tld = settings.VOICE_CONFIGS["gtts"][language].get("tld", "com")
            slow = settings.VOICE_CONFIGS["gtts"][language].get("slow", False)
            
            # Generate speech
            tts = gtts.gTTS(text=text, lang=gtts_lang, tld=tld, slow=slow)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                tts.save(temp_file.name)
                temp_path = temp_file.name
            
            # Load audio data
            audio_array, sample_rate = librosa.load(temp_path, sr=settings.AUDIO_SETTINGS["sample_rate"])
            duration = len(audio_array) / sample_rate
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return AudioData(
                audio_array=audio_array,
                sample_rate=sample_rate,
                duration=duration,
                metadata={"engine": "gtts", "language": language}
            )
            
        except Exception as e:
            logger.error(f"gTTS generation failed: {e}")
            raise
    
    async def _generate_with_pyttsx3(self, text: str, language: str) -> AudioData:
        """Generate speech using pyttsx3"""
        if not self.engines["pyttsx3"]["initialized"]:
            raise RuntimeError("pyttsx3 engine not initialized")
        
        try:
            engine = self.engines["pyttsx3"]["engine"]
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            # Load audio data
            audio_array, sample_rate = librosa.load(temp_path, sr=settings.AUDIO_SETTINGS["sample_rate"])
            duration = len(audio_array) / sample_rate
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return AudioData(
                audio_array=audio_array,
                sample_rate=sample_rate,
                duration=duration,
                metadata={"engine": "pyttsx3", "language": language}
            )
            
        except Exception as e:
            logger.error(f"pyttsx3 generation failed: {e}")
            raise
    
    async def _generate_with_coqui(self, text: str, language: str) -> AudioData:
        """Generate speech using Coqui TTS"""
        if not COQUI_AVAILABLE or not self.engines["coqui"]["initialized"]:
            raise RuntimeError("Coqui TTS not available")
        
        try:
            tts = self.engines["coqui"]["model"]
            
            # Generate speech
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Coqui TTS generation (simplified)
            tts.tts_to_file(text=text, file_path=temp_path)
            
            # Load audio data
            audio_array, sample_rate = librosa.load(temp_path, sr=settings.AUDIO_SETTINGS["sample_rate"])
            duration = len(audio_array) / sample_rate
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return AudioData(
                audio_array=audio_array,
                sample_rate=sample_rate,
                duration=duration,
                metadata={"engine": "coqui", "language": language}
            )
            
        except Exception as e:
            logger.error(f"Coqui TTS generation failed: {e}")
            raise
    
    async def _post_process_audio(self, audio_data: AudioData) -> AudioData:
        """Post-process generated audio for better quality"""
        try:
            audio = audio_data.audio_array
            
            # Normalize audio levels
            audio = librosa.util.normalize(audio)
            
            # Apply gentle noise reduction (basic)
            # For more advanced noise reduction, consider using noisereduce library
            
            # Trim silence from beginning and end
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Add small fade-in and fade-out
            fade_samples = int(0.1 * audio_data.sample_rate)  # 100ms fade
            if len(audio) > fade_samples * 2:
                # Fade in
                audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
                # Fade out
                audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Extract phoneme information for lip-sync
            phonemes = await self._extract_phonemes(audio, audio_data.sample_rate)
            
            return AudioData(
                audio_array=audio,
                sample_rate=audio_data.sample_rate,
                duration=len(audio) / audio_data.sample_rate,
                phonemes=phonemes,
                metadata=audio_data.metadata
            )
            
        except Exception as e:
            logger.warning(f"Audio post-processing failed: {e}")
            return audio_data  # Return original if post-processing fails
    
    async def _extract_phonemes(self, audio: np.ndarray, sample_rate: int) -> List[Dict]:
        """Extract phoneme information for lip-sync animation"""
        try:
            # This is a simplified phoneme extraction
            # For production, consider using more advanced libraries like:
            # - Rhubarb Lip Sync
            # - Festival Speech Synthesis System
            # - MaryTTS
            
            # Basic onset detection as a placeholder
            onset_frames = librosa.onset.onset_detect(
                y=audio,
                sr=sample_rate,
                units='time'
            )
            
            # Convert to phoneme-like data structure
            phonemes = []
            for i, onset_time in enumerate(onset_frames):
                # Simplified phoneme mapping (placeholder)
                phoneme_types = ['A', 'E', 'I', 'O', 'U', 'M', 'B', 'P']
                phoneme = phoneme_types[i % len(phoneme_types)]
                
                duration = 0.2  # Default phoneme duration
                if i < len(onset_frames) - 1:
                    duration = onset_frames[i + 1] - onset_time
                
                phonemes.append({
                    "phoneme": phoneme,
                    "start_time": float(onset_time),
                    "duration": float(duration),
                    "intensity": 0.8
                })
            
            return phonemes
            
        except Exception as e:
            logger.warning(f"Phoneme extraction failed: {e}")
            return []
    
    async def _check_cache(self, text: str, language: str, voice_style: str, engine: str) -> Optional[AudioData]:
        """Check if audio is cached"""
        try:
            cache_key = self._generate_cache_key(text, language, voice_style, engine)
            cache_file = self.cache_dir / f"{cache_key}.npz"
            
            if cache_file.exists():
                # Load cached audio
                data = np.load(cache_file, allow_pickle=True)
                return AudioData(
                    audio_array=data['audio_array'],
                    sample_rate=int(data['sample_rate']),
                    duration=float(data['duration']),
                    phonemes=data.get('phonemes', []).tolist() if 'phonemes' in data else [],
                    metadata=data.get('metadata', {}).item() if 'metadata' in data else {}
                )
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        
        return None
    
    async def _cache_audio(self, audio_data: AudioData, text: str, language: str, voice_style: str, engine: str):
        """Cache generated audio"""
        try:
            cache_key = self._generate_cache_key(text, language, voice_style, engine)
            cache_file = self.cache_dir / f"{cache_key}.npz"
            
            # Save audio data
            np.savez_compressed(
                cache_file,
                audio_array=audio_data.audio_array,
                sample_rate=audio_data.sample_rate,
                duration=audio_data.duration,
                phonemes=audio_data.phonemes or [],
                metadata=audio_data.metadata or {}
            )
            
            logger.debug(f"Audio cached: {cache_file}")
            
        except Exception as e:
            logger.warning(f"Audio caching failed: {e}")
    
    def _generate_cache_key(self, text: str, language: str, voice_style: str, engine: str) -> str:
        """Generate cache key for audio"""
        cache_string = f"{text}_{language}_{voice_style}_{engine}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    async def save_audio(self, audio_data: AudioData, output_path: str, format: str = "wav") -> str:
        """Save audio data to file"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "wav":
                sf.write(
                    output_path,
                    audio_data.audio_array,
                    audio_data.sample_rate,
                    format='WAV'
                )
            elif format.lower() == "mp3":
                # Convert to AudioSegment for MP3 export
                audio_segment = AudioSegment(
                    audio_data.audio_array.tobytes(),
                    frame_rate=audio_data.sample_rate,
                    sample_width=2,
                    channels=1
                )
                audio_segment.export(output_path, format="mp3")
            else:
                raise ValueError(f"Unsupported audio format: {format}")
            
            logger.info(f"Audio saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise
    
    def get_available_engines(self) -> List[str]:
        """Get list of available TTS engines"""
        return [engine for engine, config in self.engines.items() if config["initialized"]]
    
    def get_supported_languages(self, engine: str = None) -> List[str]:
        """Get supported languages for an engine"""
        if engine is None:
            return list(settings.SUPPORTED_LANGUAGES.keys())
        
        # Engine-specific language support
        engine_languages = {
            "gtts": ["en", "hi"],
            "pyttsx3": ["en"],  # Primarily English
            "coqui": ["en", "hi"]  # Depends on model
        }
        
        return engine_languages.get(engine, ["en"])
