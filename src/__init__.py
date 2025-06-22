"""
AI Text-to-Video Platform
"""

__version__ = "1.0.0"
__author__ = "AI Text-to-Video Platform Team"
__description__ = "AI-powered platform for converting text to animated videos"

from .core import TextProcessor, TTSEngine
from .config.settings import settings

__all__ = ["TextProcessor", "TTSEngine", "settings"]
