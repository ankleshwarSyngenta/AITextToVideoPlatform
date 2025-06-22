ai-text-to-video-platform/
├── README.md
├── requirements.txt
├── setup.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── config.yaml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── text_processor.py
│   │   ├── tts_engine.py
│   │   ├── animation_engine.py
│   │   ├── video_renderer.py
│   │   └── character_controller.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── text_models.py
│   │   ├── animation_models.py
│   │   └── video_models.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── audio_utils.py
│   │   ├── video_utils.py
│   │   └── language_utils.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── dependencies.py
│   └── web/
│       ├── __init__.py
│       ├── streamlit_app.py
│       ├── templates/
│       └── static/
├── assets/
│   ├── characters/
│   │   ├── bull_character.blend
│   │   ├── animations/
│   │   ├── textures/
│   │   └── rigs/
│   ├── audio/
│   │   ├── voice_samples/
│   │   └── sound_effects/
│   ├── backgrounds/
│   │   ├── static/
│   │   └── animated/
│   └── fonts/
├── scripts/
│   ├── install_dependencies.sh
│   ├── setup_blender.py
│   ├── create_character.py
│   └── batch_process.py
├── tests/
│   ├── __init__.py
│   ├── test_text_processor.py
│   ├── test_tts_engine.py
│   ├── test_animation_engine.py
│   ├── test_video_renderer.py
│   └── test_integration.py
├── data/
│   ├── input/
│   ├── output/
│   ├── temp/
│   └── cache/
├── docs/
│   ├── installation.md
│   ├── usage.md
│   ├── api_reference.md
│   └── troubleshooting.md
└── docker/
    ├── Dockerfile
    ├── docker-compose.yml
    └── requirements-docker.txt
