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
from src.core.video_renderer import create_video_renderer


class TextToVideoApp:
    """Main application class for text-to-video generation"""
    
    def __init__(self):
        self.settings = Settings()
        self.text_processor = TextProcessor()
        self.tts_engine = TTSEngine()
        
        # Initialize video renderer with default config
        self.video_renderer = create_video_renderer({
            'width': 1920,
            'height': 1080,
            'fps': 24,
            'bitrate': '5000k',
            'codec': 'h264'
        })
        
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
                processed_text.cleaned_text, language, voice_style
            )
            
            # Step 3: Create character animations (placeholder)
            logger.info("Creating character animations...")
            # animation_data = await self.animation_engine.create_animations(
            #     processed_text, audio_data
            # )
            
            # Step 4: Render final video
            logger.info("Rendering final video...")
            
            # Create a simple video with text overlay
            video_path = await self._create_simple_video(
                processed_text, audio_data, aspect_ratio, quality, output_path
            )
            
            logger.success(f"Video generated successfully: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise
    
    async def _create_simple_video(
        self, 
        processed_text, 
        audio_data: dict,
        aspect_ratio: str = "16:9",
        quality: str = "1080p",
        output_path: str = None
    ) -> str:
        """Create a simple video with text overlay"""
        import tempfile
        import cv2
        import numpy as np
        
        try:
            # Save audio to temporary file
            audio_path = f"data/output/temp_audio_{hash(processed_text.cleaned_text)}.wav"
            await self.tts_engine.save_audio(audio_data, audio_path)
            
            # Set up video dimensions based on quality and aspect ratio
            dimensions = {
                "720p": {"16:9": (1280, 720), "9:16": (720, 1280), "1:1": (720, 720)},
                "1080p": {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)},
                "4k": {"16:9": (3840, 2160), "9:16": (2160, 3840), "1:1": (2160, 2160)}
            }
            
            width, height = dimensions.get(quality, {}).get(aspect_ratio, (1920, 1080))
            
            # Create background image with gradient
            background = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Create gradient background (dark blue to black)
            for i in range(height):
                intensity = int(100 * (1 - i / height))
                background[i, :] = [intensity + 30, intensity + 20, intensity + 60]
            
            # Calculate font sizes based on resolution
            title_font_scale = width / 1920 * 2.0
            text_font_scale = width / 1920 * 0.8
            meta_font_scale = width / 1920 * 0.6
            
            # Add title
            title = "AI Text-to-Video Platform"
            title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, title_font_scale, 3)[0]
            title_x = (width - title_size[0]) // 2
            cv2.putText(background, title, (title_x, int(height * 0.1)), 
                       cv2.FONT_HERSHEY_SIMPLEX, title_font_scale, (255, 255, 255), 3)
            
            # Add processed text with word wrapping
            words = processed_text.cleaned_text.split()
            lines = []
            max_chars_per_line = int(width / (text_font_scale * 20))  # Approximate character width
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= max_chars_per_line:
                    current_line += " " + word if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # Draw text lines
            y_start = int(height * 0.2)
            line_height = int(text_font_scale * 40)
            max_lines = min(len(lines), int((height * 0.6) / line_height))
            
            for i, line in enumerate(lines[:max_lines]):
                y_pos = y_start + (i * line_height)
                cv2.putText(background, line, (50, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, text_font_scale, (255, 255, 255), 2)
            
            # Add metadata at bottom
            metadata_y = int(height * 0.9)
            metadata_info = [
                f"Language: {processed_text.language.upper()}",
                f"Words: {processed_text.metadata['word_count']}",
                f"Duration: {audio_data.duration:.1f}s"
            ]
            
            for i, info in enumerate(metadata_info):
                x_pos = 50 + (i * int(width / 3))
                cv2.putText(background, info, (x_pos, metadata_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, meta_font_scale, (200, 200, 200), 2)
            
            # Save background image
            bg_image_path = f"data/output/temp_bg_{hash(processed_text.cleaned_text)}.png"
            os.makedirs("data/output", exist_ok=True)
            
            # Use absolute path for the background image
            bg_image_path = os.path.abspath(bg_image_path)
            cv2.imwrite(bg_image_path, background)
            
            # Generate output path if not provided
            if output_path is None:
                timestamp = int(asyncio.get_event_loop().time())
                output_path = f"data/output/video_{timestamp}.mp4"
            
            # Create video using renderer
            duration = audio_data.duration
            video_file = self.video_renderer.create_slideshow_video(
                images=[bg_image_path],
                audio_file=audio_path,
                output_path=output_path,
                duration_per_image=duration
            )
            
            # Clean up temporary files
            try:
                os.unlink(bg_image_path)
                os.unlink(audio_path)
            except:
                pass
            
            return video_file
            
        except Exception as e:
            logger.error(f"Failed to create simple video: {e}")
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
        
        print(f"✅ Audio generated successfully: {video_path}")
    
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
