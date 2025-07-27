# AI Agent Seller Backend

A professional, well-structured backend for the AI Agent Seller multi-modal AI system. This backend provides Arabic conversational AI, speech processing, computer vision, and retail management capabilities.

## 🏗️ **Architecture Overview**

This backend follows **clean architecture principles** with clear separation of concerns:

```
backend/
├── app/                      # Main application package
│   ├── api/                  # API layer with versioning
│   │   └── v1/              # API version 1
│   │       ├── endpoints/   # Individual endpoint modules
│   │       └── deps.py      # Dependency injection
│   ├── core/                # Core configuration and utilities
│   │   ├── config.py        # Settings management
│   │   ├── logging.py       # Logging configuration
│   │   └── exceptions.py    # Custom exceptions
│   ├── models/              # SQLAlchemy database models
│   ├── schemas/             # Pydantic request/response models
│   ├── services/            # Business logic layer
│   ├── db/                  # Database configuration
│   └── utils/               # Utility functions
├── tests/                   # Comprehensive test suite
├── requirements/            # Environment-specific dependencies
├── docker/                  # Docker configuration
└── alembic/                # Database migrations
```

## 🚀 **Key Improvements**

### **1. Professional Structure**
- ✅ **Separation of Concerns**: Clear boundaries between API, business logic, and data layers
- ✅ **API Versioning**: Future-proof design with `/api/v1/` structure
- ✅ **Dependency Injection**: Clean dependency management with FastAPI's DI system
- ✅ **Configuration Management**: Centralized, environment-based configuration
- ✅ **Error Handling**: Comprehensive exception handling with custom error types

### **2. Scalability & Maintainability**
- ✅ **Service Layer**: Business logic separated from API endpoints
- ✅ **Model Organization**: Clean SQLAlchemy models with proper relationships
- ✅ **Schema Validation**: Pydantic models for request/response validation
- ✅ **Logging System**: Professional logging with Loguru
- ✅ **Testing Structure**: Organized test suite with pytest

### **3. Production Ready**
- ✅ **Docker Support**: Optimized Dockerfile and Docker Compose
- ✅ **Environment Management**: Separate configs for dev/staging/production
- ✅ **Security**: Proper authentication, CORS, and input validation
- ✅ **Health Checks**: Comprehensive health monitoring
- ✅ **Database Migrations**: Alembic for schema versioning

## 🛠️ **Components**

### **AI Services**
| Service | Endpoint | Model | Purpose |
|---------|----------|-------|---------|
| **Chat** | `/api/v1/chat` | Ollama Gemma3:4b | Arabic conversational AI |
| **STT** | `/api/v1/stt` | Whisper Large V3 Turbo | Arabic speech recognition |
| **TTS** | `/api/v1/tts` | XTTS-v2 | Arabic text-to-speech |
| **Tracking** | `/api/v1/tracking` | YOLOv11x + BoostTrack | Person detection & tracking |
| **Status** | `/api/v1/status` | Ollama | Person mood/age/gender analysis |

### **Database Models**
- **Category**: Product categorization
- **Store**: Retail locations
- **Clothes**: Product inventory
- **Customer**: User management
- **Order/OrderItem**: Transaction processing

## 🚀 **Quick Start**

### **Option 1: Docker Compose (Recommended)**

```bash
# Clone and setup
cd backend
cp .env.example .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Test the API
curl http://localhost:8000/health
```

### **Option 2: Local Development**

```bash
# Setup environment
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements/development.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Setup database
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 **API Documentation**

### **Interactive Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Sample API Calls**

#### **Chat Interface**
```bash
# Send Arabic message
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "أريد شراء قميص أزرق"}'
```

#### **Speech-to-Text**
```bash
# Upload audio file
curl -X POST "http://localhost:8000/api/v1/stt/transcribe" \
  -F "file=@audio.wav"
```

#### **Person Tracking**
```bash
# Upload video for tracking
curl -X POST "http://localhost:8000/api/v1/tracking/upload" \
  -F "file=@video.mp4"
```

## 🔧 **Configuration**

### **Environment Variables**

Key settings in `.env`:

```bash
# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Database
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/selling

# AI Models
WHISPER_MODEL=openai/whisper-large-v3-turbo
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
OLLAMA_ENDPOINT=http://localhost:11434/api/generate

# GPU
USE_GPU=true
CUDA_VISIBLE_DEVICES=0
```

### **Model Files Required**
```bash
# Place these files in the project root:
_7JpEjF2Vyk.wav                          # TTS speaker reference
fine_tuned_model_epoch_32.pth            # ReID model
yolov11x-person-mot20val-crowdhuman.pt   # YOLO model
```

## 🧪 **Testing**

### **Run Tests**
```bash
# All tests
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_api/test_chat.py

# Integration tests
pytest tests/test_integration/
```

### **Test Structure**
```
tests/
├── conftest.py              # Test configuration
├── test_api/               # API endpoint tests
├── test_services/          # Business logic tests
├── test_models/            # Database model tests
└── test_integration/       # End-to-end tests
```

## 📦 **Database Management**

### **Migrations**
```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### **Sample Data**
```bash
# Load sample data
python -c "from app.db.init_db import init_db; init_db()"
```

## 🐳 **Docker Deployment**

### **Production Deployment**
```bash
# Build and deploy
docker-compose -f docker-compose.yml up -d --build

# Scale services
docker-compose up -d --scale backend=3

# Monitor
docker-compose logs -f --tail=100 backend
```

### **Services**
- **backend**: Main FastAPI application
- **postgres**: PostgreSQL database
- **redis**: Caching and sessions
- **ollama**: AI model service

## 🔍 **Monitoring & Debugging**

### **Logs**
```bash
# Application logs
tail -f backend.log

# Docker logs
docker-compose logs -f backend

# Database logs
docker-compose logs postgres
```

### **Health Checks**
```bash
# Application health
curl http://localhost:8000/health

# Model status
curl http://localhost:8000/api/v1/models/status

# Database connectivity
curl http://localhost:8000/api/v1/db/health
```

## 🔒 **Security**

### **Authentication**
- JWT-based authentication
- Role-based access control
- API key validation

### **Input Validation**
- Pydantic schema validation
- File upload restrictions
- SQL injection prevention

### **CORS Configuration**
```python
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",  # React frontend
    "https://yourdomain.com"  # Production frontend
]
```

## 📈 **Performance**

### **Optimization Features**
- **Model Caching**: Keep AI models in memory
- **Database Connection Pooling**: Efficient DB connections
- **Async Processing**: Non-blocking I/O operations
- **GPU Acceleration**: CUDA support for AI models

### **Monitoring**
- Request/response times
- Model inference metrics
- Database query performance
- Memory and CPU usage

## 🤝 **Development**

### **Code Quality**
```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### **Pre-commit Hooks**
```bash
# Install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📝 **Migration from Old Structure**

To migrate from the old flat structure:

1. **Models**: Move from `db.py` → `app/models/`
2. **APIs**: Move from individual files → `app/api/v1/endpoints/`
3. **Business Logic**: Extract to `app/services/`
4. **Configuration**: Centralize in `app/core/config.py`
5. **Update Imports**: Use new package structure

## 🆘 **Troubleshooting**

### **Common Issues**

**Model Loading Fails**
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Verify model files
ls -la *.pth *.pt *.wav
```

**Database Connection Error**
```bash
# Test connection
psql -h localhost -U postgres -d selling

# Check Docker
docker-compose ps postgres
```

**Import Errors**
```bash
# Install in development mode
pip install -e .

# Check Python path
echo $PYTHONPATH
```

---

## 📄 **License**

This project is licensed under the MIT License.

## 🔗 **Links**

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Original Project**: Link to main repository

---

**AI Agent Seller Backend** - Professional, scalable, and production-ready! 🚀 