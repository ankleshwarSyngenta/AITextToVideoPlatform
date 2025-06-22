# 🚀 Quick Start Guide

## Installation

1. **Install Dependencies**
   ```bash
   chmod +x scripts/install_dependencies.sh
   ./scripts/install_dependencies.sh
   ```

2. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

3. **Setup Blender (Optional)**
   ```bash
   python scripts/setup_blender.py
   ```

## Usage

### 1. Web Interface (Recommended)
```bash
python src/main.py --web
```
Then open: http://localhost:8501

### 2. Command Line
```bash
python src/main.py "Hello, welcome to our AI platform!"
```

### 3. API Server
```bash
python src/main.py --api
```
API docs: http://localhost:8000/docs

## Features Available

✅ **Text Processing** - Multilingual text analysis
✅ **Text-to-Speech** - Multiple TTS engines (gTTS, pyttsx3)
✅ **Audio Generation** - High-quality speech synthesis
✅ **Web Interface** - User-friendly Streamlit app
✅ **API Server** - RESTful API for integration

🚧 **In Development** - 3D Character animation, Video rendering

## Example Usage

```python
from src.core.text_processor import TextProcessor
from src.core.tts_engine import TTSEngine

# Process text
processor = TextProcessor()
result = await processor.process_text("Hello world!", language="en")

# Generate speech
tts = TTSEngine()
audio = await tts.generate_speech(result.cleaned_text, language="en")
```

## Next Steps

1. Complete the animation engine
2. Implement video rendering
3. Add more TTS engines
4. Enhance character animations

For full documentation, see `TECHNICAL_DOCUMENTATION.md`
