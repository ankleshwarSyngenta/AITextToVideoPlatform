"""
Setup script for AI Text-to-Video Platform
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ai-text-to-video-platform",
    version="1.0.0",
    author="AI Text-to-Video Platform Team",
    author_email="contact@ai-text-to-video.com",
    description="AI-powered platform for converting text to animated videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/ai-text-to-video-platform",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "streamlit>=1.28.1",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "gTTS>=2.4.0",
        "pyttsx3>=2.90",
        "TTS>=0.21.1",
        "librosa>=0.10.1",
        "soundfile>=0.12.1",
        "pydub>=0.25.1",
        "scipy>=1.11.4",
        "moviepy>=1.0.3",
        "opencv-python>=4.8.1.78",
        "Pillow>=10.1.0",
        "imageio>=2.31.6",
        "imageio-ffmpeg>=0.4.9",
        "spacy>=3.7.2",
        "nltk>=3.8.1",
        "transformers>=4.36.0",
        "torch>=2.1.1",
        "mediapipe>=0.10.8",
        "requests>=2.31.0",
        "aiofiles>=23.2.1",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "click>=8.1.7",
        "tqdm>=4.66.1",
        "loguru>=0.7.2",
        "sqlalchemy>=2.0.23",
        "langdetect>=1.0.9",
        "numpy>=1.24.4",
        "matplotlib>=3.8.2",
        "pandas>=2.1.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.6.0",
        ],
        "deploy": [
            "gunicorn>=21.2.0",
            "docker>=6.1.3",
        ],
        "advanced": [
            "celery>=5.3.4",
            "redis>=5.0.1",
            "bark>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ai-text-to-video=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.txt", "*.md"],
    },
    zip_safe=False,
)
