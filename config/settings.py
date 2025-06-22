"""
Configuration settings for the AI Text-to-Video Platform
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import yaml


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    ASSETS_DIR: Path = PROJECT_ROOT / "assets"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    CACHE_DIR: Path = DATA_DIR / "cache"
    TEMP_DIR: Path = DATA_DIR / "temp"
    INPUT_DIR: Path = DATA_DIR / "input"
    OUTPUT_DIR: Path = DATA_DIR / "output"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Web Interface Configuration
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 8501
    
    # Text-to-Speech Configuration
    TTS_ENGINE: str = "gtts"  # gtts, coqui, pyttsx3
    TTS_CACHE_ENABLED: bool = True
    TTS_CACHE_DIR: Path = CACHE_DIR / "tts"
    
    # Supported languages
    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "en": "English",
        "hi": "Hindi"
    }
    
    # Voice configuration
    VOICE_CONFIGS: Dict[str, Dict[str, Any]] = {
        "gtts": {
            "en": {"tld": "com", "slow": False},
            "hi": {"tld": "co.in", "slow": False}
        },
        "pyttsx3": {
            "rate": 150,
            "volume": 0.9
        }
    }
    
    # Animation Configuration
    BLENDER_PATH: Optional[str] = None  # Auto-detect if None
    CHARACTER_MODEL_PATH: Path = ASSETS_DIR / "characters" / "bull_character.blend"
    ANIMATION_CACHE_ENABLED: bool = True
    ANIMATION_CACHE_DIR: Path = CACHE_DIR / "animations"
    
    # Animation settings
    ANIMATION_SETTINGS: Dict[str, Any] = {
        "frame_rate": 24,
        "lip_sync_threshold": 0.1,
        "gesture_intensity": 0.8,
        "idle_animation_loop": True,
        "breathing_amplitude": 0.02
    }
    
    # Video Rendering Configuration
    VIDEO_SETTINGS: Dict[str, Dict[str, Any]] = {
        "720p": {
            "width": 1280,
            "height": 720,
            "bitrate": "2M",
            "fps": 24
        },
        "1080p": {
            "width": 1920,
            "height": 1080,
            "bitrate": "5M",
            "fps": 24
        },
        "4k": {
            "width": 3840,
            "height": 2160,
            "bitrate": "15M",
            "fps": 24
        }
    }
    
    # Aspect ratio configurations
    ASPECT_RATIOS: Dict[str, Dict[str, float]] = {
        "16:9": {"width": 16, "height": 9},
        "9:16": {"width": 9, "height": 16},
        "1:1": {"width": 1, "height": 1}
    }
    
    # Audio settings
    AUDIO_SETTINGS: Dict[str, Any] = {
        "sample_rate": 44100,
        "bit_depth": 16,
        "channels": 1,
        "format": "wav"
    }
    
    # Performance settings
    MAX_WORKERS: int = 4
    MEMORY_LIMIT_GB: int = 8
    ENABLE_GPU: bool = True
    BATCH_SIZE: int = 1
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_SIZE: str = "10 MB"
    LOG_FILE_RETENTION: str = "10 days"
    
    # Cache settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_HOURS: int = 24
    MAX_CACHE_SIZE_GB: int = 5
    
    # File upload limits
    MAX_TEXT_LENGTH: int = 10000
    MAX_FILE_SIZE_MB: int = 10
    
    # Development settings
    DEBUG: bool = False
    RELOAD_ON_CHANGE: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._create_directories()
        self._load_config_file()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.DATA_DIR, self.LOGS_DIR, self.CACHE_DIR,
            self.TEMP_DIR, self.INPUT_DIR, self.OUTPUT_DIR,
            self.TTS_CACHE_DIR, self.ANIMATION_CACHE_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config_file(self):
        """Load additional configuration from YAML file"""
        config_file = self.PROJECT_ROOT / "config" / "config.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    if config_data:
                        # Update settings with config file data
                        for key, value in config_data.items():
                            if hasattr(self, key.upper()):
                                setattr(self, key.upper(), value)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
    
    def get_video_dimensions(self, quality: str, aspect_ratio: str) -> tuple:
        """Get video dimensions based on quality and aspect ratio"""
        base_settings = self.VIDEO_SETTINGS[quality]
        ratio_settings = self.ASPECT_RATIOS[aspect_ratio]
        
        # Calculate dimensions maintaining aspect ratio
        base_width = base_settings["width"]
        base_height = base_settings["height"]
        
        if aspect_ratio == "16:9":
            return base_width, base_height
        elif aspect_ratio == "9:16":
            return base_height, base_width
        elif aspect_ratio == "1:1":
            size = min(base_width, base_height)
            return size, size
        
        return base_width, base_height
    
    def get_blender_executable(self) -> Optional[str]:
        """Auto-detect Blender executable path"""
        if self.BLENDER_PATH:
            return self.BLENDER_PATH
        
        # Common Blender installation paths
        common_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",  # macOS
            "/usr/bin/blender",  # Linux
            "/snap/bin/blender",  # Linux Snap
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",  # Windows
            "blender"  # System PATH
        ]
        
        for path in common_paths:
            if os.path.exists(path) or self._command_exists(path):
                return path
        
        return None
    
    def _command_exists(self, command: str) -> bool:
        """Check if command exists in system PATH"""
        import shutil
        return shutil.which(command) is not None


# Global settings instance
settings = Settings()
