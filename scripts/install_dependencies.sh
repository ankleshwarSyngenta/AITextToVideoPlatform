#!/bin/bash

# AI Text-to-Video Platform - Installation Script
# This script installs all required dependencies for the platform

echo "🎬 AI Text-to-Video Platform - Installation Script"
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📍 Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python requirements
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Install spaCy models
echo "🧠 Installing spaCy language models..."
python -m spacy download en_core_web_sm

# Check if Blender is installed
echo "🎨 Checking Blender installation..."
if command -v blender &> /dev/null; then
    echo "✅ Blender found: $(blender --version | head -n 1)"
else
    echo "⚠️ Blender not found. Please install Blender 3.0+ from https://www.blender.org/"
    echo "   macOS: brew install --cask blender"
    echo "   Ubuntu: sudo snap install blender --classic"
    echo "   Windows: Download from https://www.blender.org/download/"
fi

# Check if FFmpeg is installed
echo "🎞️ Checking FFmpeg installation..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg found: $(ffmpeg -version | head -n 1)"
else
    echo "⚠️ FFmpeg not found. Installing FFmpeg..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "Please install Homebrew first: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt update && sudo apt install -y ffmpeg
    else
        echo "Please install FFmpeg manually from https://ffmpeg.org/"
    fi
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/{input,output,temp,cache}
mkdir -p assets/{characters,audio,backgrounds,fonts}
mkdir -p logs
mkdir -p assets/characters/{animations,textures,rigs}
mkdir -p assets/audio/{voice_samples,sound_effects}
mkdir -p assets/backgrounds/{static,animated}

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.py
chmod +x scripts/*.sh

# Download Coqui TTS models (optional)
echo "🎤 Setting up Coqui TTS models..."
python -c "
try:
    from TTS.api import TTS
    print('Downloading TTS model...')
    tts = TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')
    print('✅ Coqui TTS model downloaded successfully')
except Exception as e:
    print(f'⚠️ Coqui TTS setup failed: {e}')
    print('You can still use gTTS and pyttsx3 engines')
"

# Test installation
echo "🧪 Testing installation..."
python -c "
import sys
import importlib

required_modules = [
    'fastapi', 'streamlit', 'gtts', 'pyttsx3', 'librosa', 
    'moviepy', 'opencv', 'spacy', 'transformers', 'PIL'
]

missing_modules = []
for module in required_modules:
    try:
        if module == 'opencv':
            importlib.import_module('cv2')
        elif module == 'PIL':
            importlib.import_module('PIL')
        else:
            importlib.import_module(module)
        print(f'✅ {module}')
    except ImportError:
        missing_modules.append(module)
        print(f'❌ {module}')

if missing_modules:
    print(f'\\n⚠️ Missing modules: {missing_modules}')
    sys.exit(1)
else:
    print('\\n🎉 All required modules installed successfully!')
"

echo ""
echo "🎉 Installation completed!"
echo ""
echo "🚀 Quick Start Commands:"
echo "  source venv/bin/activate          # Activate virtual environment"
echo "  python src/main.py --web          # Start web interface"
echo "  python src/main.py --api          # Start API server"
echo "  python src/main.py 'Hello World'  # Generate video via CLI"
echo ""
echo "🌐 Web Interface: http://localhost:8501"
echo "🔗 API Documentation: http://localhost:8000/docs"
echo ""
echo "📚 For more information, check README.md and docs/"
