"""
Streamlit Web Interface for AI Text-to-Video Platform
"""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path
import tempfile
import time
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.text_processor import TextProcessor
from src.core.tts_engine import TTSEngine
from src.main import TextToVideoApp
from config.settings import settings


# Page configuration
st.set_page_config(
    page_title="AI Text-to-Video Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
    }
    
    .error-box {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
    }
    
    .processing-box {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'app' not in st.session_state:
    st.session_state.app = TextToVideoApp()
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'generated_video' not in st.session_state:
    st.session_state.generated_video = None


def main():
    """Main application interface"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎬 AI Text-to-Video Platform</h1>
        <p>Transform your text into engaging animated videos with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Language selection
        language = st.selectbox(
            "🌐 Language",
            options=["en", "hi"],
            format_func=lambda x: "English" if x == "en" else "Hindi",
            help="Select the language for text-to-speech"
        )
        
        # TTS Engine selection
        available_engines = st.session_state.app.tts_engine.get_available_engines()
        tts_engine = st.selectbox(
            "🎤 TTS Engine",
            options=available_engines,
            help="Select the text-to-speech engine"
        )
        
        # Voice style
        voice_style = st.selectbox(
            "🎵 Voice Style",
            options=["default", "formal", "casual", "energetic"],
            help="Select voice style preference"
        )
        
        # Video settings
        st.subheader("📹 Video Settings")
        
        aspect_ratio = st.selectbox(
            "📐 Aspect Ratio",
            options=["16:9", "9:16", "1:1"],
            help="Select video aspect ratio"
        )
        
        quality = st.selectbox(
            "🎯 Quality",
            options=["720p", "1080p", "4k"],
            index=1,
            help="Select output video quality"
        )
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            enable_animations = st.checkbox("Enable Character Animations", value=True)
            enable_lip_sync = st.checkbox("Enable Lip Sync", value=True)
            animation_intensity = st.slider("Animation Intensity", 0.1, 1.0, 0.8)
            
        # System info
        st.subheader("ℹ️ System Info")
        st.info(f"""
        **Available Engines:** {', '.join(available_engines)}
        
        **Supported Languages:** English, Hindi
        
        **Max Text Length:** {settings.MAX_TEXT_LENGTH:,} characters
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Text Input")
        
        # Text input methods
        input_method = st.radio(
            "Input Method",
            options=["Direct Text", "File Upload"],
            horizontal=True
        )
        
        text_input = ""
        
        if input_method == "Direct Text":
            text_input = st.text_area(
                "Enter your text here:",
                height=200,
                max_chars=settings.MAX_TEXT_LENGTH,
                placeholder="Type or paste your text here. The AI will convert it into an engaging video with animated character..."
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload text file",
                type=['txt', 'docx'],
                help="Upload a text file to convert to video"
            )
            
            if uploaded_file:
                try:
                    if uploaded_file.type == "text/plain":
                        text_input = str(uploaded_file.read(), "utf-8")
                    else:
                        st.error("Only .txt files are supported in this demo")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        # Character count
        if text_input:
            char_count = len(text_input)
            if char_count > settings.MAX_TEXT_LENGTH:
                st.error(f"Text is too long ({char_count:,} characters). Maximum allowed: {settings.MAX_TEXT_LENGTH:,}")
            else:
                st.info(f"Character count: {char_count:,} / {settings.MAX_TEXT_LENGTH:,}")
        
        # Generate button
        if st.button("🎬 Generate Video", type="primary", disabled=st.session_state.processing):
            if not text_input.strip():
                st.error("Please enter some text to generate video")
            else:
                generate_video(text_input, language, tts_engine, voice_style, aspect_ratio, quality)
    
    with col2:
        st.header("🎥 Preview & Results")
        
        if st.session_state.processing:
            show_processing_status()
        elif st.session_state.generated_video:
            show_video_result()
        else:
            show_feature_preview()


def generate_video(text: str, language: str, tts_engine: str, voice_style: str, aspect_ratio: str, quality: str):
    """Generate video from text input"""
    st.session_state.processing = True
    st.session_state.generated_video = None
    
    try:
        with st.spinner("🔄 Processing your request..."):
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Generate video using the main app
            status_text.text("🎬 Generating video...")
            progress_bar.progress(10)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Generate video with integrated pipeline
            video_path = loop.run_until_complete(
                st.session_state.app.generate_video(
                    text=text,
                    language=language,
                    voice_style=voice_style,
                    aspect_ratio=aspect_ratio,
                    quality=quality
                )
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Video generation complete!")
            
            # Store results
            st.session_state.generated_video = {
                "video_path": video_path,
                "text": text,
                "settings": {
                    "language": language,
                    "tts_engine": tts_engine,
                    "voice_style": voice_style,
                    "aspect_ratio": aspect_ratio,
                    "quality": quality
                }
            }
            
            loop.close()
            
    except Exception as e:
        st.error(f"Error generating video: {str(e)}")
        st.exception(e)
    finally:
        st.session_state.processing = False


def show_processing_status():
    """Show processing status"""
    st.markdown("""
    <div class="processing-box">
        <h3>🔄 Processing...</h3>
        <p>Your video is being generated. This may take a few minutes depending on the text length and quality settings.</p>
    </div>
    """, unsafe_allow_html=True)


def show_video_result():
    """Show generated video results"""
    result = st.session_state.generated_video
    
    st.markdown("""
    <div class="success-box">
        <h3>✅ Video Generated Successfully!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Video preview
    st.subheader("� Video Preview")
    if os.path.exists(result["video_path"]):
        # Display video
        st.video(result["video_path"])
        
        # Download button for video
        with open(result["video_path"], "rb") as video_file:
            st.download_button(
                label="📥 Download Video",
                data=video_file.read(),
                file_name=f"generated_video.mp4",
                mime="video/mp4"
            )
    else:
        st.warning("Video file not found. Only audio was generated.")
        
        # Check if it's actually an audio file
        if result["video_path"].endswith(('.wav', '.mp3', '.ogg')):
            st.subheader("🎤 Audio Preview")
            st.audio(result["video_path"])
            
            # Download button for audio
            with open(result["video_path"], "rb") as audio_file:
                st.download_button(
                    label="📥 Download Audio",
                    data=audio_file.read(),
                    file_name=f"generated_audio.wav",
                    mime="audio/wav"
                )
    
    # Generation info
    st.subheader("📊 Generation Info")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Text Length", f"{len(result['text'])} chars")
    with col2:
        st.metric("Language", result["settings"]["language"].upper())
    with col3:
        st.metric("Quality", result["settings"]["quality"])
    
    # Settings used
    with st.expander("⚙️ Generation Settings"):
        settings_used = result["settings"]
        st.json(settings_used)
    
    # Generate new video button
    if st.button("🔄 Generate Another Video"):
        st.session_state.generated_video = None
        st.experimental_rerun()
    
    # Text analysis results
    st.subheader("📊 Text Analysis")
    processed = result["processed_text"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Words", processed.metadata["word_count"])
    with col2:
        st.metric("Sentences", processed.metadata["sentence_count"])
    with col3:
        st.metric("Duration", f"{processed.metadata['estimated_duration']:.1f}s")
    
    # Language detection
    st.info(f"**Detected Language:** {processed.language.upper()} (Confidence: {processed.language_confidence:.1%})")
    
    # Emotion analysis
    if processed.emotion_cues:
        st.subheader("😊 Emotion Analysis")
        emotions = {}
        for cue in processed.emotion_cues:
            emotion = cue["emotion"]
            emotions[emotion] = emotions.get(emotion, 0) + 1
        
        for emotion, count in emotions.items():
            st.write(f"• {emotion.title()}: {count} occurrences")
    
    # Animation cues
    if processed.animation_cues:
        st.subheader("🎭 Animation Cues")
        animations = {}
        for cue in processed.animation_cues:
            anim_type = cue["animation_type"]
            animations[anim_type] = animations.get(anim_type, 0) + 1
        
        for anim_type, count in animations.items():
            st.write(f"• {anim_type.title()}: {count} triggers")
    
    # Settings used
    with st.expander("⚙️ Generation Settings"):
        settings_used = result["settings"]
        st.json(settings_used)
    
    # Generate new video button
    if st.button("🔄 Generate Another Video"):
        st.session_state.generated_video = None
        st.experimental_rerun()


def show_feature_preview():
    """Show feature preview when no video is generated"""
    st.markdown("""
    <div class="feature-box">
        <h3>🎬 AI Video Generation Features</h3>
        <ul>
            <li>🌐 Multi-language support (English & Hindi)</li>
            <li>🎤 Multiple TTS engines (gTTS, pyttsx3, Coqui)</li>
            <li>🎭 Intelligent animation cues</li>
            <li>😊 Emotion-based expressions</li>
            <li>📱 Multiple aspect ratios</li>
            <li>🎯 High-quality output (up to 4K)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📊 Sample Analytics")
    st.info("Text analysis, emotion detection, and animation cues will appear here after generation.")
    
    # Sample video preview (placeholder)
    st.subheader("🎥 Video Preview")
    st.info("Generated video will appear here. Audio preview will be available immediately after TTS generation.")


def show_examples():
    """Show example texts for different use cases"""
    st.header("💡 Example Texts")
    
    examples = {
        "Educational": "Welcome to our physics lesson today. We'll explore the fascinating world of quantum mechanics and how particles behave at the smallest scales.",
        "Motivational": "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.",
        "News": "Breaking news: Scientists have made a groundbreaking discovery that could revolutionize renewable energy technology.",
        "Hindi Example": "नमस्ते दोस्तों! आज हम एक रोचक विषय पर चर्चा करेंगे। शिक्षा हमारे जीवन में कितनी महत्वपूर्ण है।"
    }
    
    for category, text in examples.items():
        with st.expander(f"📝 {category}"):
            st.write(text)
            if st.button(f"Use {category} Example", key=f"example_{category}"):
                st.session_state.example_text = text


# Sidebar navigation
with st.sidebar:
    st.markdown("---")
    
    page = st.selectbox(
        "📱 Navigation",
        options=["Generate Video", "Examples", "Help"],
        index=0
    )

# Main content routing
if page == "Generate Video":
    main()
elif page == "Examples":
    show_examples()
elif page == "Help":
    st.header("❓ Help & Documentation")
    
    st.markdown("""
    ## 🚀 Getting Started
    
    1. **Enter Text**: Type or upload your text content
    2. **Select Settings**: Choose language, voice, and video options
    3. **Generate**: Click the generate button and wait for processing
    4. **Download**: Download your generated video
    
    ## 📋 Supported Features
    
    - **Languages**: English and Hindi
    - **TTS Engines**: gTTS, pyttsx3, Coqui TTS
    - **Video Quality**: 720p, 1080p, 4K
    - **Aspect Ratios**: 16:9, 9:16, 1:1
    
    ## 🔧 Troubleshooting
    
    - **Audio Not Playing**: Check your browser's audio settings
    - **Long Processing Time**: Large texts take more time to process
    - **Engine Not Available**: Some TTS engines may not be installed
    
    ## 📞 Support
    
    For technical support, please check the documentation or report issues on our GitHub repository.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    🎬 AI Text-to-Video Platform | Built with Streamlit | Open Source
</div>
""", unsafe_allow_html=True)
