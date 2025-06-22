# AI-Powered Text-to-Video Generation Platform

🎯 **Transform Text into Engaging Animated Videos with AI**

## Overview
This platform automatically converts text (English/Hindi) into high-quality animated videos featuring a custom 3D bull character with synchronized voiceover and cinematic animations.

## Features
- ✅ **Multilingual Support**: English and Hindi text-to-speech
- ✅ **Custom 3D Character**: Bull character inspired by General Kai
- ✅ **Lip-Sync Animation**: Natural speaking animations
- ✅ **Multiple Formats**: 16:9, 9:16, and 1:1 aspect ratios  
- ✅ **4K Quality**: High-resolution video output
- ✅ **Free & Open Source**: No licensing costs

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd ai-text-to-video-platform

# Install dependencies
pip install -r requirements.txt

# Setup Blender integration
python scripts/setup_blender.py

# Run the application
python src/main.py
```

### 2. Web Interface
```bash
# Start the web interface
streamlit run src/web/streamlit_app.py
```

### 3. API Server
```bash
# Start the FastAPI server
uvicorn src.api.routes:app --reload
```

## Usage Examples

### Simple Text Input
```python
from src.core.text_processor import TextProcessor
from src.core.video_renderer import VideoRenderer

# Process text
processor = TextProcessor()
result = processor.process_text("Hello, welcome to our platform!", language="en")

# Generate video
renderer = VideoRenderer()
video_path = renderer.create_video(result, aspect_ratio="16:9")
```

### Batch Processing
```bash
python scripts/batch_process.py --input data/input/ --output data/output/
```

## System Requirements
- Python 3.8+
- Blender 3.0+
- FFmpeg
- 8GB RAM (16GB recommended)
- 50GB free storage

## Technology Stack
- **TTS**: gTTS, Coqui TTS, pyttsx3
- **3D Animation**: Blender, Rhubarb Lip-Sync
- **Video Processing**: MoviePy, OpenCV, FFmpeg
- **Web Interface**: FastAPI, Streamlit
- **AI/ML**: spaCy, transformers, MediaPipe

## Project Structure
```
src/
├── core/           # Core processing engines
├── models/         # Data models
├── utils/          # Utility functions
├── api/           # REST API
└── web/           # Web interface

assets/
├── characters/     # 3D character files
├── audio/         # Audio resources
└── backgrounds/   # Background assets
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License
This project is open source and available under the MIT License.

## Support
- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)

---

**Ready to create amazing videos? Let's get started!** 🚀
