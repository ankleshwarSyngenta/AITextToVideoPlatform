"""
AI Text-to-Video Platform
Main entry point for the application
"""

import sys
import os
from pathlib import Path
import argparse
import asyncio
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from src.core.text_processor import TextProcessor
from src.core.tts_engine import TTSEngine
from src.core.animation_engine import AnimationEngine
from src.core.video_renderer import VideoRenderer


class TextToVideoApp:
    """Main application class for text-to-video generation"""
    
    def __init__(self):
        self.settings = Settings()
        self.text_processor = TextProcessor()
        self.tts_engine = TTSEngine()
        self.animation_engine = AnimationEngine()
        self.video_renderer = VideoRenderer()
        
        # Setup logging
        logger.add(
            "logs/app.log",
            rotation="10 MB",
            retention="10 days",
            level="INFO"
        )
    
    async def generate_video(
        self,
        text: str,
        language: str = "en",
        voice_style: str = "default",
        aspect_ratio: str = "16:9",
        quality: str = "1080p",
        output_path: str = None
    ) -> str:
        """
        Generate video from text input
        
        Args:
            text: Input text to convert to video
            language: Language code (en/hi)
            voice_style: Voice style preference
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
            quality: Output quality (720p, 1080p, 4k)
            output_path: Custom output path
            
        Returns:
            Path to generated video file
        """
        try:
            logger.info(f"Starting video generation for text: {text[:50]}...")
            
            # Step 1: Process text
            logger.info("Processing text input...")
            processed_text = await self.text_processor.process_text(
                text, language
            )
            
            # Step 2: Generate audio with TTS
            logger.info("Generating audio with TTS...")
            audio_data = await self.tts_engine.generate_speech(
                processed_text, language, voice_style
            )
            
            # Step 3: Create character animations
            logger.info("Creating character animations...")
            animation_data = await self.animation_engine.create_animations(
                processed_text, audio_data
            )
            
            # Step 4: Render final video
            logger.info("Rendering final video...")
            video_path = await self.video_renderer.render_video(
                animation_data, audio_data, aspect_ratio, quality, output_path
            )
            
            logger.success(f"Video generated successfully: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise
    
    def run_cli(self):
        """Run the command-line interface"""
        parser = argparse.ArgumentParser(
            description="AI Text-to-Video Generation Platform"
        )
        parser.add_argument(
            "text", 
            help="Text to convert to video"
        )
        parser.add_argument(
            "--language", "-l",
            choices=["en", "hi"],
            default="en",
            help="Language for text-to-speech"
        )
        parser.add_argument(
            "--aspect-ratio", "-ar",
            choices=["16:9", "9:16", "1:1"],
            default="16:9",
            help="Video aspect ratio"
        )
        parser.add_argument(
            "--quality", "-q",
            choices=["720p", "1080p", "4k"],
            default="1080p",
            help="Output video quality"
        )
        parser.add_argument(
            "--output", "-o",
            help="Output file path"
        )
        parser.add_argument(
            "--voice-style", "-vs",
            default="default",
            help="Voice style preference"
        )
        
        args = parser.parse_args()
        
        # Generate video
        video_path = asyncio.run(
            self.generate_video(
                text=args.text,
                language=args.language,
                voice_style=args.voice_style,
                aspect_ratio=args.aspect_ratio,
                quality=args.quality,
                output_path=args.output
            )
        )
        
        print(f"✅ Video generated successfully: {video_path}")
    
    def run_web_interface(self):
        """Launch the web interface"""
        import subprocess
        import sys
        
        logger.info("Starting web interface...")
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                "src/web/streamlit_app.py",
                "--server.port=8501",
                "--server.address=0.0.0.0"
            ])
        except KeyboardInterrupt:
            logger.info("Web interface stopped by user")
    
    def run_api_server(self):
        """Launch the API server"""
        import subprocess
        import sys
        
        logger.info("Starting API server...")
        try:
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "src.api.routes:app",
                "--host=0.0.0.0",
                "--port=8000",
                "--reload"
            ])
        except KeyboardInterrupt:
            logger.info("API server stopped by user")


def main():
    """Main entry point"""
    app = TextToVideoApp()
    
    if len(sys.argv) == 1:
        # No arguments provided, show help
        print("🎬 AI Text-to-Video Generation Platform")
        print()
        print("Usage:")
        print("  python src/main.py 'Your text here'  # CLI mode")
        print("  python src/main.py --web              # Web interface")
        print("  python src/main.py --api              # API server")
        print()
        print("For more options: python src/main.py --help")
        return
    
    if "--web" in sys.argv:
        app.run_web_interface()
    elif "--api" in sys.argv:
        app.run_api_server()
    else:
        app.run_cli()


if __name__ == "__main__":
    main()
