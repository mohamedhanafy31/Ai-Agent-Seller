# API Documentation for Frontend Integration

## 📋 **Overview**

This documentation covers all endpoints available for frontend integration, including both REST APIs and WebSocket connections.

**Base URL**: `http://localhost:8000`  
**WebSocket URL**: `ws://localhost:8000`

---

## 🔗 **REST Endpoints**

### **Chat Endpoints**

#### **1. Send Message to AI Assistant**
```http
POST /api/v1/chat/message
Content-Type: application/json

{
  "message": "أريد شراء قميص أزرق للعمل",
  "session_id": "sess_abc123"
}
```

**Response:**
```json
{
  "response": "مرحباً! أرى أنك تبحث عن قميص أزرق للعمل. لدينا مجموعة رائعة من القمصان الرسمية. ما هو مقاسك المفضل؟",
  "session_id": "sess_abc123",
  "timestamp": "2024-01-20T10:30:00Z",
  "processing_time": 1.2,
  "confidence": 0.95
}
```

#### **2. Stream Chat Response (Server-Sent Events)**
```javascript
// Frontend implementation
const eventSource = new EventSource('/api/v1/chat/stream', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: 'أريد شراء قميص أزرق للعمل',
    session_id: 'sess_abc123'
  })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case 'token':
      appendToChat(data.content);
      break;
    case 'complete':
      console.log('Chat complete:', data.full_response);
      break;
    case 'error':
      console.error('Chat error:', data.message);
      break;
  }
};
```

#### **3. Get Chat Sessions**
```http
GET /api/v1/chat/sessions
```

**Response:**
```json
[
  {
    "session_id": "sess_abc123",
    "created_at": "2024-01-20T10:00:00Z",
    "last_activity": "2024-01-20T10:30:00Z",
    "message_count": 5,
    "is_active": true
  }
]
```

#### **4. Create Chat Session**
```http
POST /api/v1/chat/sessions
```

**Response:**
```json
{
  "session_id": "sess_new123",
  "created_at": "2024-01-20T11:00:00Z",
  "last_activity": "2024-01-20T11:00:00Z",
  "message_count": 0,
  "is_active": true
}
```

### **TTS (Text-to-Speech) Endpoints**

#### **1. Synthesize Speech**
```http
POST /api/v1/tts/synthesize
Content-Type: application/json

{
  "text": "اهلا بيك تعالي",
  "language": "ar",
  "speed": 1.0
}
```

**Response:**
```json
{
  "audio_url": "/api/v1/tts/audio/greeting_abc123.wav",
  "duration": 2.5,
  "sample_rate": 22050,
  "processing_time": 1.1
}
```

#### **2. Get Audio File**
```http
GET /api/v1/tts/audio/{filename}
```

**Usage:**
```javascript
// Frontend implementation
const audioUrl = response.audio_url;
const audio = new Audio(`http://localhost:8000${audioUrl}`);
audio.play();
```

#### **3. Quick Speech Synthesis**
```http
POST /api/v1/tts/quick-speech
Content-Type: application/x-www-form-urlencoded

text=اهلا بيك تعالي&language=ar&speed=1.0
```

### **STT (Speech-to-Text) Endpoints**

#### **1. Transcribe Audio**
```http
POST /api/v1/stt/transcribe
Content-Type: multipart/form-data

file: [audio_file.wav]
language: ar
```

**Response:**
```json
{
  "text": "أريد شراء قميص أزرق للعمل",
  "language": "ar",
  "confidence": 0.94,
  "duration": 4.2,
  "processing_time": 1.8
}
```

#### **2. Get Audio Info**
```http
POST /api/v1/stt/audio-info
Content-Type: multipart/form-data

file: [audio_file.wav]
```

### **Person Tracking Endpoints**

#### **1. Upload Video for Tracking**
```http
POST /api/v1/tracking/upload
Content-Type: multipart/form-data

file: [video_file.mp4]
confidence_threshold: 0.5
max_persons: 10
```

**Response:**
```json
{
  "session_id": "track_session_abc123",
  "status": "uploaded",
  "filename": "store_surveillance.mp4"
}
```

#### **2. Process Uploaded Video**
```http
POST /api/v1/tracking/process/{session_id}
Content-Type: application/x-www-form-urlencoded

confidence_threshold: 0.5
max_tracks: 10
```

**Response:**
```json
{
  "session_id": "track_session_abc123",
  "status": "processing",
  "tracking_info": {
    "device_id": 0,
    "resolution": "1920x1080",
    "frame_rate": 30
  }
}
```

#### **3. Get Tracking Sessions**
```http
GET /api/v1/tracking/sessions
```

#### **4. Get Specific Tracking Session**
```http
GET /api/v1/tracking/sessions/{session_id}
```

### **Person Status Analysis Endpoints**

#### **1. Analyze Person Status**
```http
POST /api/v1/status/analyze
Content-Type: multipart/form-data

file: [image_file.jpg]
include_demographics: true
include_emotions: true
include_engagement: true
confidence_threshold: 0.5
```

**Response:**
```json
{
  "person_id": "person_123",
  "demographics": {
    "age_range": "25-35",
    "gender": "female",
    "appearance": {"clothing_style": "casual"}
  },
  "emotions": {
    "primary_emotion": "happy",
    "emotion_confidence": 0.91
  },
  "engagement": {
    "attention_level": 0.82,
    "interest_score": 0.76
  }
}
```

#### **2. Capture and Analyze**
```http
POST /api/v1/status/capture
Content-Type: application/x-www-form-urlencoded

camera_id: 0
resolution: 640x480
quality: 85
include_demographics: true
include_emotions: true
```

---

## 🔌 **WebSocket Endpoints**

### **TTS Real-time Audio Streaming**

**Connection:**
```javascript
const ttsWebSocket = new WebSocket('ws://localhost:8000/api/v1/tts/stream');
```

**Send Text for Synthesis:**
```javascript
ttsWebSocket.send(JSON.stringify({
  text: "مرحباً بكم في متجرنا",
  language: "ar",
  chunk_size: 1024
}));
```

**Receive Audio Chunks:**
```javascript
ttsWebSocket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'audio_chunk':
      // Play audio chunk immediately
      playAudioChunk(data.data, data.chunk_index);
      break;
      
    case 'complete':
      console.log('TTS synthesis complete');
      break;
      
    case 'error':
      console.error('TTS error:', data.message);
      break;
  }
};
```

**Audio Chunk Player:**
```javascript
function playAudioChunk(base64Audio, chunkIndex) {
  const audioData = atob(base64Audio);
  const audioArray = new Uint8Array(audioData.length);
  for (let i = 0; i < audioData.length; i++) {
    audioArray[i] = audioData.charCodeAt(i);
  }
  
  const audioBlob = new Blob([audioArray], { type: 'audio/wav' });
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  audio.play();
}
```

---

## 📝 **Session ID Management**

### **Chat Sessions**
- **Format**: `"sess_abc123"`
- **Usage**: Maintain conversation context
- **Optional**: Can be omitted for new conversations

### **Tracking Sessions**
- **Format**: `"track_session_abc123"`
- **Usage**: Required for video processing workflow
- **Source**: Returned from upload endpoint

---

## ⚠️ **Error Handling**

### **HTTP Error Responses**
```json
{
  "detail": "Error message here"
}
```

### **Common Error Codes**
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (session not found)
- **422**: Validation Error (invalid file format)
- **503**: Service Unavailable (model not loaded)

### **WebSocket Error Handling**
```javascript
ttsWebSocket.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ttsWebSocket.onclose = (event) => {
  console.log('WebSocket closed:', event.code, event.reason);
};
```

---

## 🎯 **Integration Examples**

### **Complete Chat Flow**
```javascript
class ChatIntegration {
  constructor() {
    this.sessionId = null;
    this.ttsWebSocket = null;
    this.setupTTSWebSocket();
  }
  
  setupTTSWebSocket() {
    this.ttsWebSocket = new WebSocket('ws://localhost:8000/api/v1/tts/stream');
    this.ttsWebSocket.onmessage = this.handleTTSMessage.bind(this);
  }
  
  async sendMessage(message) {
    const response = await fetch('/api/v1/chat/message', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        message: message,
        session_id: this.sessionId
      })
    });
    
    const data = await response.json();
    this.sessionId = data.session_id;
    
    // Send to TTS for audio generation
    this.ttsWebSocket.send(JSON.stringify({
      text: data.response,
      language: "ar"
    }));
    
    return data;
  }
  
  handleTTSMessage(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'audio_chunk') {
      this.playAudioChunk(data.data);
    }
  }
  
  playAudioChunk(base64Audio) {
    // Audio playback implementation
  }
}
```

### **File Upload Example**
```javascript
async function uploadAudioFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', 'ar');
  
  const response = await fetch('/api/v1/stt/transcribe', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}
```

---

## 🔧 **Testing Endpoints**

### **Health Checks**
```http
GET /health
GET /api/v1/chat/health
GET /api/v1/tts/health
GET /api/v1/stt/health
GET /api/v1/tracking/health
GET /api/v1/status/health
```

### **WebSocket Testing**
```javascript
// Browser console testing
const ws = new WebSocket('ws://localhost:8000/api/v1/tts/stream');
ws.onopen = () => {
  console.log('Connected to TTS WebSocket');
  ws.send(JSON.stringify({text: "مرحبا", language: "ar"}));
};
ws.onmessage = (event) => console.log('Received:', event.data);
```

---

## 📋 **Quick Reference**

| Endpoint | Method | Real-time | Purpose |
|----------|--------|-----------|---------|
| `/api/v1/chat/message` | POST | ❌ | Send chat message |
| `/api/v1/chat/stream` | POST | ✅ | Stream chat response |
| `/api/v1/tts/synthesize` | POST | ❌ | Generate audio file |
| `/api/v1/tts/stream` | WebSocket | ✅ | Real-time audio streaming |
| `/api/v1/stt/transcribe` | POST | ❌ | Transcribe audio file |
| `/api/v1/tracking/upload` | POST | ❌ | Upload video for tracking |
| `/api/v1/tracking/process/{id}` | POST | ❌ | Process uploaded video |
| `/api/v1/status/analyze` | POST | ❌ | Analyze person status |

**Note**: WebSocket endpoints are not visible in Swagger UI but are fully functional. 