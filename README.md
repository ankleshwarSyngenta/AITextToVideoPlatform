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
git clone https://github.com/ankleshwarSyngenta/AITextToVideoPlatform.git
cd AITextToVideoPlatform

# Install dependencies
pip install streamlit fastapi uvicorn gtts pyttsx3 requests python-dotenv pyyaml loguru langdetect pydantic-settings

# Run the application
python src/main.py --web
```

### 2. Web Interface
```bash
# Start the web interface
python src/main.py --web
```

### 3. API Server
```bash
# Start the FastAPI server
python src/main.py --api
```

## Usage Examples

### Simple Text Input
```python
from src.core.text_processor import TextProcessor
from src.core.tts_engine import TTSEngine

# Process text
processor = TextProcessor()
result = processor.process_text("Hello, welcome to our platform!", language="en")

# Generate audio
tts_engine = TTSEngine()
audio_data = tts_engine.generate_speech(result.cleaned_text, language="en")
```

### Batch Processing
```bash
python scripts/batch_process.py --input data/input/ --output data/output/
```

## System Requirements
- Python 3.8+
- Blender 3.0+ (for 3D animation)
- FFmpeg (for video processing)
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

## Development Status

### ✅ Completed Features
- **Text Processing**: Multilingual text analysis with emotion detection
- **TTS Engine**: Multiple text-to-speech backends (gTTS, pyttsx3)
- **Web Interface**: Beautiful Streamlit-based UI
- **Audio Generation**: High-quality speech synthesis with caching
- **Configuration System**: Flexible YAML-based settings

### 🚧 In Progress
- **3D Character Animation**: Blender integration and lip-sync
- **Video Rendering**: Final video composition pipeline
- **Advanced Animation**: Gesture library and emotion expressions

### 📋 Planned Features
- **Batch Processing**: Multiple video generation
- **API Integration**: RESTful API for external systems
- **Cloud Deployment**: Docker containerization
- **Performance Optimization**: GPU acceleration and caching

## Getting Started

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements-basic.txt

# Install additional tools
# macOS:
brew install blender ffmpeg

# Ubuntu:
sudo apt install blender ffmpeg

# Windows:
# Download from official websites
```

### Running the Application
1. **Web Interface**: `python src/main.py --web`
2. **API Server**: `python src/main.py --api`
3. **CLI Tool**: `python src/main.py "Your text here"`

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
- 🐛 [Issues](https://github.com/ankleshwarSyngenta/AITextToVideoPlatform/issues)
- 💬 [Discussions](https://github.com/ankleshwarSyngenta/AITextToVideoPlatform/discussions)

## Roadmap

### Phase 1: Foundation (✅ Complete)
- Text processing and analysis
- TTS engine integration
- Web interface development
- Basic audio generation

### Phase 2: Animation (🚧 In Progress)
- 3D character modeling
- Lip-sync implementation
- Gesture animation system
- Video rendering pipeline

### Phase 3: Enhancement (📋 Planned)
- Advanced AI features
- Performance optimization
- Cloud deployment
- Mobile support

---

**Ready to create amazing videos? Let's get started!** 🚀

## Quick Demo

Try the platform with these example texts:

**English**: "Welcome to our AI-powered video platform. Transform your ideas into engaging visual stories."

**Hindi**: "नमस्ते! आज हम एक रोचक AI वीडियो प्लेटफॉर्म के बारे में जानेंगे।"

Visit the web interface at `http://localhost:8501` after starting the application!
