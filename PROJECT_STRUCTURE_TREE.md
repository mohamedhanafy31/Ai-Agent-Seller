# AI Agent Seller Backend - Project Structure Tree

```
backend/
├── 📁 app/                                    # Main application package
│   ├── __init__.py                           # Package initialization
│   ├── main.py                               # FastAPI application entry point (18KB, 479 lines)
│   │
│   ├── 📁 api/                               # API layer
│   │   ├── __init__.py                       # API package init
│   │   ├── deps.py                           # Dependency injection utilities (2.7KB, 79 lines)
│   │   └── 📁 v1/                            # API version 1
│   │       ├── __init__.py                   # v1 package init
│   │       ├── api.py                        # API router configuration (710B, 40 lines)
│   │       └── 📁 endpoints/                 # API endpoints
│   │           ├── __init__.py               # Endpoints package init
│   │           ├── chat.py                   # Chat API endpoints (16KB, 405 lines)
│   │           ├── status.py                 # Status/health endpoints (28KB, 750 lines)
│   │           ├── stt.py                    # Speech-to-Text endpoints (17KB, 461 lines)
│   │           ├── tts.py                    # Text-to-Speech endpoints (18KB, 510 lines)
│   │           └── tracking.py               # Object tracking endpoints (24KB, 641 lines)
│   │
│   ├── 📁 core/                              # Core application components
│   │   ├── __init__.py                       # Core package init
│   │   ├── config.py                         # Configuration management (3.4KB, 104 lines)
│   │   ├── exceptions.py                     # Custom exception classes (5.4KB, 163 lines)
│   │   └── logging.py                        # Logging configuration (2.7KB, 94 lines)
│   │
│   ├── 📁 db/                                # Database layer
│   │   ├── __init__.py                       # Database package init
│   │   ├── base.py                           # Base database configuration (427B, 12 lines)
│   │   ├── base_class.py                     # Base model class (397B, 19 lines)
│   │   └── session.py                        # Database session management (501B, 21 lines)
│   │
│   ├── 📁 models/                            # Database models
│   │   ├── __init__.py                       # Models package init (311B, 18 lines)
│   │   ├── category.py                       # Category model (460B, 18 lines)
│   │   ├── clothes.py                        # Clothes/Product model (851B, 24 lines)
│   │   ├── customer.py                       # Customer model (529B, 20 lines)
│   │   ├── order.py                          # Order model (1.2KB, 37 lines)
│   │   └── store.py                          # Store model (478B, 19 lines)
│   │
│   ├── 📁 schemas/                           # Pydantic schemas
│   │   ├── __init__.py                       # Schemas package init (60B, 3 lines)
│   │   ├── chat.py                           # Chat request/response schemas (2.6KB, 83 lines)
│   │   ├── status.py                         # Status schemas (3.5KB, 94 lines)
│   │   ├── stt.py                            # STT schemas (1.6KB, 50 lines)
│   │   ├── tts.py                            # TTS schemas (2.3KB, 58 lines)
│   │   └── tracking.py                       # Tracking schemas (3.5KB, 92 lines)
│   │
│   ├── 📁 services/                          # Business logic services
│   │   ├── __init__.py                       # Services package init (63B, 3 lines)
│   │   ├── chat_service.py                   # Chat service logic (10KB, 273 lines)
│   │   ├── model_manager.py                  # AI model management (7.2KB, 195 lines)
│   │   ├── status_service.py                 # Status monitoring service (14KB, 397 lines)
│   │   ├── stt_service.py                    # Speech-to-Text service (7.5KB, 194 lines)
│   │   ├── tts_service.py                    # Text-to-Speech service (7.7KB, 211 lines)
│   │   └── tracking_service.py               # Object tracking service (11KB, 290 lines)
│   │
│   └── 📁 utils/                             # Utility functions
│       ├── __init__.py                       # Utils package init (61B, 3 lines)
│       ├── audio.py                          # Audio processing utilities (7.8KB, 283 lines)
│       ├── file_utils.py                     # File handling utilities (9.7KB, 364 lines)
│       └── image.py                          # Image processing utilities (9.1KB, 331 lines)
│
├── 📁 assets/                                # Static assets and models
│   ├── 📁 audio/                             # Audio assets (empty)
│   ├── 📁 cache/                             # Cache directory
│   │   └── 📁 embeddings/                    # AI model embeddings cache
│   └── 📁 models/                            # AI model files
│       └── fine_tuned_model_epoch_32.pth     # ReID model weights (34MB)
│
├── 📁 docker/                                # Docker configuration files
│   ├── .dockerignore                         # Docker ignore patterns (1.1KB, 120 lines)
│   ├── docker-entrypoint.sh                  # Docker entrypoint script (5.3KB, 220 lines)
│   ├── Dockerfile                            # Main Dockerfile (2.8KB, 100 lines)
│   ├── Dockerfile.hybrid                     # Hybrid Dockerfile (4.0KB, 140 lines)
│   ├── Dockerfile.minimal                    # Minimal Dockerfile (2.7KB, 81 lines)
│   ├── Dockerfile.optimized                  # Optimized Dockerfile (3.4KB, 122 lines)
│   └── Dockerfile.test                       # Test Dockerfile (1.7KB, 62 lines)
│
├── 📁 models/                                # Model storage directory (empty)
│
├── 📁 requirements/                          # Python dependencies
│   ├── base.txt                              # Base requirements (749B, 47 lines)
│   ├── development.txt                       # Development requirements (513B, 32 lines)
│   └── production.txt                        # Production requirements (915B, 57 lines)
│
├── 📁 uploads/                               # User uploaded files
│   ├── 📁 audio/                             # Uploaded audio files
│   │   ├── tts_20154bc8.wav                  # TTS output files (128KB-3.4MB each)
│   │   ├── tts_70108ad9.wav
│   │   ├── tts_7c7e0f63.wav
│   │   ├── tts_8d19fcf9.wav
│   │   ├── tts_9cbf44fc.wav
│   │   ├── tts_a9f852c6.wav
│   │   ├── tts_bd8b6c33.wav
│   │   ├── tts_befebcdb.wav
│   │   ├── tts_e3c87539.wav
│   │   ├── tts_effa7bf3.wav
│   │   ├── tts_f1dc1d8a.wav
│   │   ├── tts_f27f82ac.wav
│   │   └── tts_fd4598ba.wav
│   ├── 📁 images/                            # Uploaded images (empty)
│   └── 📁 videos/                            # Uploaded videos
│       ├── 062b4971-dc0b-4118-a277-a61049f299bb_security_monitor.mp4
│       ├── 6f9b0aec-653a-4e52-a5df-24aae77fd790_test_video.mp4
│       ├── 8a9a60b6-5532-4369-afc7-fc40151f336d_camera_video.mp4
│       ├── bb081d82-9a5e-4e5a-a0ba-8e2299645ff5_camera_video.mp4
│       └── ce7555f4-6e15-492c-b568-afd8b3c03330_security_monitor.mp4
│
├── 📁 tracker/                               # Object tracking module (expanded separately)
│   └── [TRACKER MODULE CONTENTS - SEE SEPARATE DOCUMENTATION]
│
├── 📄 .git/                                  # Git repository data
├── 📄 .gitignore                             # Git ignore patterns (1.4KB, 133 lines)
├── 📄 __pycache__/                           # Python cache directory
├── 📄 backend.log                            # Application log file (40KB, 329 lines)
├── 📄 conda-environment-docker.yml           # Docker conda environment (1.1KB, 61 lines)
├── 📄 conda-environment-production.yml       # Production conda environment (1.9KB, 95 lines)
├── 📄 conda-environment-export.yml           # Exported conda environment (8.5KB, 322 lines)
├── 📄 conda-environment.yml                  # Base conda environment (8.5KB, 322 lines)
├── 📄 CONDA_ENVIRONMENT_README.md            # Conda environment documentation (5.7KB, 222 lines)
├── 📄 docker-compose.yml                     # Docker Compose configuration (5.2KB, 211 lines)
├── 📄 docker-env.conf                        # Docker environment configuration (2.4KB, 93 lines)
├── 📄 environment.yml                        # Environment configuration (8.5KB, 322 lines)
├── 📄 export_conda_env.py                    # Conda environment export script (3.9KB, 122 lines)
├── 📄 fine_tuned_model_epoch_32.pth          # ReID model weights (34MB)
├── 📄 README.md                              # Project documentation (9.7KB, 390 lines)
├── 📄 run.py                                 # Application runner script (1.0KB, 36 lines)
├── 📄 yolov11x-person-mot20val-crowdhuman.pt # YOLO model weights (218MB)
└── 📄 _7JpEjF2Vyk.wav                        # TTS speaker reference audio (2.7MB)
```

## 📊 **Project Statistics**

### **File Count by Type:**
- **Python Files:** 35+ (excluding __pycache__)
- **Configuration Files:** 15+
- **Model Files:** 3 (218MB total)
- **Audio Files:** 14+ (TTS outputs)
- **Video Files:** 5 (test videos)
- **Documentation:** 3 markdown files

### **Key Directories:**
- **`app/`** - Main application code (35+ files)
- **`docker/`** - Containerization (6 files)
- **`uploads/`** - User content storage
- **`assets/`** - Static assets and AI models
- **`requirements/`** - Python dependencies (3 files)

### **External Model Files:**
1. **`yolov11x-person-mot20val-crowdhuman.pt`** (218MB) - YOLO person detection
2. **`fine_tuned_model_epoch_32.pth`** (34MB) - Person re-identification
3. **`_7JpEjF2Vyk.wav`** (2.7MB) - TTS speaker reference

### **Application Structure:**
- **API Layer:** FastAPI with versioned endpoints (v1)
- **Service Layer:** Business logic for AI services
- **Data Layer:** SQLAlchemy models and schemas
- **Utility Layer:** Helper functions for audio/image processing

### **Docker Support:**
- Multiple Dockerfile variants for different deployment scenarios
- Docker Compose for multi-service orchestration
- Conda environment integration for AI/ML dependencies

This structure follows a clean, modular architecture with clear separation of concerns between API, business logic, data models, and utilities. 