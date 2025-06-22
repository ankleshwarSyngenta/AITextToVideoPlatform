"""
Text Processing Module
Handles text input preprocessing, language detection, and content analysis
"""

import re
import string
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from langdetect import detect, DetectorFactory
from loguru import logger

# Set seed for consistent language detection
DetectorFactory.seed = 0


@dataclass
class ProcessedText:
    """Data class for processed text information"""
    original_text: str
    cleaned_text: str
    language: str
    language_confidence: float
    sentences: List[str]
    words: List[str]
    emotion_cues: List[Dict[str, Any]]
    animation_cues: List[Dict[str, Any]]
    timing_info: Dict[str, Any]
    metadata: Dict[str, Any]


class TextProcessor:
    """Advanced text processing for multilingual text-to-video conversion"""
    
    def __init__(self):
        self.supported_languages = ["en", "hi"]
        self.nlp_models = {"en": None, "hi": None}  # Initialize nlp_models
        self._setup_emotion_keywords()
        self._setup_animation_triggers()
    
    def _load_nlp_models(self):
        """Load spaCy NLP models for supported languages"""
        self.nlp_models = {}
        
        try:
            # English model
            self.nlp_models["en"] = spacy.load("en_core_web_sm")
            logger.info("Loaded English NLP model")
        except OSError:
            logger.warning("English spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp_models["en"] = None
        
        # Note: Hindi spaCy model can be added when available
        # For now, we'll use basic processing for Hindi
        self.nlp_models["hi"] = None
        
    def _setup_emotion_keywords(self):
        """Setup emotion detection keywords for different languages"""
        self.emotion_keywords = {
            "en": {
                "happy": ["happy", "joy", "excited", "cheerful", "delighted", "pleased"],
                "sad": ["sad", "depressed", "unhappy", "sorrow", "grief", "melancholy"],
                "angry": ["angry", "furious", "mad", "rage", "annoyed", "frustrated"],
                "surprised": ["surprised", "amazed", "shocked", "astonished", "stunned"],
                "fear": ["afraid", "scared", "terrified", "worried", "anxious", "nervous"],
                "neutral": ["said", "stated", "mentioned", "explained", "described"]
            },
            "hi": {
                "happy": ["खुश", "प्रसन्न", "आनंदित", "हर्षित"],
                "sad": ["दुखी", "उदास", "शोकित", "परेशान"],
                "angry": ["गुस्सा", "क्रोधित", "नाराज"],
                "surprised": ["हैरान", "आश्चर्यचकित", "चकित"],
                "fear": ["डर", "भयभीत", "चिंतित"],
                "neutral": ["कहा", "बताया", "समझाया"]
            }
        }
    
    def _setup_animation_triggers(self):
        """Setup keywords that trigger specific animations"""
        self.animation_triggers = {
            "en": {
                "pointing": ["this", "that", "here", "there", "look", "see"],
                "emphasis": ["important", "remember", "listen", "attention", "focus"],
                "questioning": ["what", "how", "why", "when", "where", "who"],
                "explaining": ["because", "therefore", "so", "thus", "hence"],
                "greeting": ["hello", "hi", "welcome", "greetings"],
                "thinking": ["think", "consider", "ponder", "reflect", "hmm"]
            },
            "hi": {
                "pointing": ["यह", "वह", "यहाँ", "वहाँ", "देखो", "देखिए"],
                "emphasis": ["महत्वपूर्ण", "याद रखें", "सुनिए", "ध्यान"],
                "questioning": ["क्या", "कैसे", "क्यों", "कब", "कहाँ", "कौन"],
                "explaining": ["क्योंकि", "इसलिए", "अतः"],
                "greeting": ["नमस्ते", "हैलो", "स्वागत"],
                "thinking": ["सोचना", "विचार", "हम्म"]
            }
        }
    
    async def process_text(
        self, 
        text: str, 
        language: Optional[str] = None
    ) -> ProcessedText:
        """
        Process input text for video generation
        
        Args:
            text: Input text to process
            language: Language code (auto-detect if None)
            
        Returns:
            ProcessedText object with analysis results
        """
        try:
            logger.info(f"Processing text: {text[:100]}...")
            
            # Basic text cleaning
            cleaned_text = self._clean_text(text)
            
            # Language detection
            if language is None:
                detected_lang, confidence = self._detect_language(cleaned_text)
            else:
                detected_lang = language
                confidence = 1.0
            
            # Validate language support
            if detected_lang not in self.supported_languages:
                logger.warning(f"Language {detected_lang} not fully supported, using English")
                detected_lang = "en"
            
            # Sentence and word segmentation
            sentences = self._segment_sentences(cleaned_text, detected_lang)
            words = self._extract_words(cleaned_text, detected_lang)
            
            # Emotion analysis
            emotion_cues = self._analyze_emotions(cleaned_text, detected_lang)
            
            # Animation cue generation
            animation_cues = self._generate_animation_cues(cleaned_text, detected_lang)
            
            # Timing information
            timing_info = self._calculate_timing(sentences, words)
            
            # Additional metadata
            metadata = {
                "word_count": len(words),
                "sentence_count": len(sentences),
                "estimated_duration": timing_info.get("total_duration", 0),
                "complexity_score": self._calculate_complexity(cleaned_text, detected_lang)
            }
            
            return ProcessedText(
                original_text=text,
                cleaned_text=cleaned_text,
                language=detected_lang,
                language_confidence=confidence,
                sentences=sentences,
                words=words,
                emotion_cues=emotion_cues,
                animation_cues=animation_cues,
                timing_info=timing_info,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Handle special characters
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text
    
    def _detect_language(self, text: str) -> Tuple[str, float]:
        """Detect text language with confidence score"""
        try:
            detected = detect(text)
            # Map detected language to supported languages
            lang_mapping = {
                'en': 'en',
                'hi': 'hi',
                'mr': 'hi',  # Marathi -> Hindi
                'ne': 'hi',  # Nepali -> Hindi
                'ur': 'hi'   # Urdu -> Hindi
            }
            
            mapped_lang = lang_mapping.get(detected, 'en')
            confidence = 0.8  # Basic confidence score
            
            logger.info(f"Detected language: {detected} -> {mapped_lang}")
            return mapped_lang, confidence
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}, defaulting to English")
            return "en", 0.5
    
    def _segment_sentences(self, text: str, language: str) -> List[str]:
        """Segment text into sentences"""
        # Basic sentence segmentation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_words(self, text: str, language: str) -> List[str]:
        """Extract words from text"""
        if language == "en" and self.nlp_models["en"]:
            # Use spaCy for English
            doc = self.nlp_models["en"](text)
            return [token.text for token in doc if not token.is_space]
        else:
            # Basic word extraction
            words = re.findall(r'\b\w+\b', text)
            return words
    
    def _analyze_emotions(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Analyze emotional content of text"""
        emotions = []
        text_lower = text.lower()
        
        if language in self.emotion_keywords:
            keywords = self.emotion_keywords[language]
            
            for emotion, words in keywords.items():
                for word in words:
                    if word in text_lower:
                        # Find position of the word
                        positions = [m.start() for m in re.finditer(re.escape(word), text_lower)]
                        for pos in positions:
                            emotions.append({
                                "emotion": emotion,
                                "word": word,
                                "position": pos,
                                "confidence": 0.7
                            })
        
        return emotions
    
    def _generate_animation_cues(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Generate animation cues based on text content"""
        cues = []
        text_lower = text.lower()
        
        if language in self.animation_triggers:
            triggers = self.animation_triggers[language]
            
            for animation_type, words in triggers.items():
                for word in words:
                    if word in text_lower:
                        positions = [m.start() for m in re.finditer(re.escape(word), text_lower)]
                        for pos in positions:
                            cues.append({
                                "animation_type": animation_type,
                                "trigger_word": word,
                                "position": pos,
                                "duration": 2.0,  # Default 2 seconds
                                "intensity": 0.8
                            })
        
        return cues
    
    def _calculate_timing(self, sentences: List[str], words: List[str]) -> Dict[str, Any]:
        """Calculate timing information for speech"""
        # Average speaking rates (words per minute)
        speaking_rates = {
            "en": 150,  # English: ~150 WPM
            "hi": 120   # Hindi: ~120 WPM (slower due to complexity)
        }
        
        total_words = len(words)
        wpm = speaking_rates.get("en", 150)  # Default to English
        
        # Calculate duration in seconds
        duration_minutes = total_words / wpm
        duration_seconds = duration_minutes * 60
        
        # Add pause time for punctuation
        pause_time = len(sentences) * 0.5  # 0.5 seconds per sentence
        total_duration = duration_seconds + pause_time
        
        return {
            "total_words": total_words,
            "estimated_wpm": wpm,
            "base_duration": duration_seconds,
            "pause_duration": pause_time,
            "total_duration": total_duration,
            "sentences": len(sentences)
        }
    
    def _calculate_complexity(self, text: str, language: str) -> float:
        """Calculate text complexity score (0-1)"""
        if language == "en" and self.nlp_models["en"]:
            doc = self.nlp_models["en"](text)
            
            # Factors for complexity
            avg_word_length = sum(len(token.text) for token in doc if token.is_alpha) / max(1, len([t for t in doc if t.is_alpha]))
            sentence_count = len(list(doc.sents))
            word_count = len([t for t in doc if t.is_alpha])
            avg_sentence_length = word_count / max(1, sentence_count)
            
            # Normalize complexity (0-1 scale)
            complexity = min(1.0, (avg_word_length * avg_sentence_length) / 100)
            return complexity
        else:
            # Basic complexity for other languages
            words = self._extract_words(text, language)
            sentences = self._segment_sentences(text, language)
            
            avg_word_length = sum(len(word) for word in words) / max(1, len(words))
            avg_sentence_length = len(words) / max(1, len(sentences))
            
            complexity = min(1.0, (avg_word_length * avg_sentence_length) / 80)
            return complexity
