# � EthicalDRM - Content Protection Toolkit

A lightweight content protection toolkit built for independent creators, educators, OTT startups, and small film studios. EthicalDRM protects your videos from downloaders, screen recorders, and browser extensions with enterprise-grade security.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

## ✨ Features

- **🔒 HLS Video Encryption** - AES-128 encryption with per-user access control
- **🎫 JWT Token System** - Secure, expiring video access tokens
- **🏷️ Digital Watermarking** - Invisible user-specific watermarks for leak tracing
- **🔍 AI Leak Detection** - Fingerprint-based content monitoring and piracy detection
- **🛡️ Screen Recorder Detection** - Real-time detection of recording software
- **📜 DMCA Takedown Generator** - Automated legal notice generation
- **� Web Player** - Beautiful, protected HTML5 video player
- **⚙️ CLI Tools** - Complete command-line interface for all operations
- **🐳 Docker Ready** - Containerized deployment with Docker Compose

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install ethicaldrm

# Or install from source
git clone https://github.com/devils-advocate1/ethicaldrm.git
cd ethicaldrm
pip install -r requirements.txt
pip install -e .
```

### Prerequisites

- Python 3.8+
- FFmpeg (for video processing)
- OpenCV (for AI features)

```bash
# Ubuntu/Debian
sudo apt install ffmpeg libopencv-dev

# macOS
brew install ffmpeg opencv

# Windows
# Download FFmpeg from https://ffmpeg.org/
```

### Basic Usage

```bash
# 1. Encrypt a video
ethicaldrm encrypt --input video.mp4 --video-id my-video --user-id user123

# 2. Start the API server
ethicaldrm-api

# 3. Generate access token
ethicaldrm generate-token --user-id user123 --video-id my-video

# 4. Access protected video at:
# http://localhost:5000/player.html?video=my-video&token=YOUR_TOKEN
```

## 📚 Comprehensive Guide

### 🎬 Video Encryption

Encrypt videos using HLS with AES-128 encryption:

```python
from ethicaldrm import VideoEncryption

encryptor = VideoEncryption("output_dir")

# Add user watermark and encrypt
watermarked = encryptor.add_watermark("input.mp4", "user123")
result = encryptor.encrypt_video(watermarked, "video_id")

print(f"Encrypted video: {result['playlist_path']}")
print(f"Segments created: {result['segments_count']}")
```

### 🎫 Token Management

Secure access control with JWT tokens:

```python
from ethicaldrm import TokenManager

token_mgr = TokenManager("your-secret-key")

# Generate token (expires in 1 hour)
token = token_mgr.generate_token("user123", "video_id", expires_in=3600)

# Validate token
payload = token_mgr.validate_token(token)
print(f"Valid for user: {payload['user_id']}")
```

### 🔍 Leak Detection

AI-powered content monitoring:

```python
from ethicaldrm import LeakDetector

detector = LeakDetector()

# Register original content
owner_info = {"name": "Creator", "email": "creator@example.com"}
detector.register_content("original.mp4", "content_id", owner_info)

# Check for leaks
matches = detector.detect_leak("suspect_video.mp4")
for match in matches:
    print(f"Similarity: {match['similarity']:.2%}")
    print(f"Confidence: {match['confidence']}")
```

### 🛡️ Security Monitoring

Real-time security scanning:

```python
from ethicaldrm.utils.security import SecurityUtils

security = SecurityUtils()

# Detect screen recorders
recorders = security.detect_screen_recorders()
print(f"Found {len(recorders)} screen recording apps")

# Generate protection headers
headers = security.generate_security_headers()
```

## 🌐 API Endpoints

The EthicalDRM API provides RESTful endpoints for all operations:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/generate_token` | POST | Generate access token |
| `/get_stream/{video_id}.m3u8` | GET | Get HLS playlist |
| `/get_segment` | GET | Get video segment |
| `/get_key` | GET | Get encryption key |
| `/upload_video` | POST | Upload and encrypt video |
| `/validate_token` | POST | Validate token |

### Example API Usage

```bash
# Generate token
curl -X POST http://localhost:5000/generate_token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "video_id": "my-video", "expires_in": 3600}'

# Access video stream
curl "http://localhost:5000/get_stream/my-video.m3u8?token=YOUR_TOKEN"
```

## 🐳 Docker Deployment

Deploy with Docker Compose for production:

```bash
# Clone repository
git clone https://github.com/devils-advocate1/ethicaldrm.git
cd ethicaldrm

# Start services
docker-compose up -d

# Services available:
# - EthicalDRM API: http://localhost:5000
# - Nginx proxy: http://localhost:80
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
# - Prometheus: http://localhost:9090
```

## 📋 CLI Commands

Complete command-line interface:

```bash
# Video operations
ethicaldrm encrypt --input video.mp4 --video-id my-video
ethicaldrm batch-encrypt --input-dir videos/ --output-dir encrypted/

# Token operations  
ethicaldrm generate-token --user-id user123 --video-id my-video
ethicaldrm validate-token --token YOUR_TOKEN

# Content protection
ethicaldrm register-content --video original.mp4 --content-id content123
ethicaldrm detect-leak --suspect-video suspect.mp4
ethicaldrm generate-takedown --content-id content123 --infringing-url http://bad-site.com

# Security
ethicaldrm security-scan
ethicaldrm extract-watermark --video watermarked.mp4

# Server
ethicaldrm serve --dir encrypted_output --host 0.0.0.0 --port 5000
```

## 🎯 Use Cases

### Independent Creators
- Protect premium courses and tutorials
- Prevent unauthorized downloading
- Track content leaks back to users

### Educational Institutions  
- Secure online learning content
- Control access to recorded lectures
- Monitor for unauthorized distribution

### OTT Startups
- Enterprise-grade content protection
- User-specific watermarking
- Real-time leak detection

### Film Studios
- Protect screeners and dailies
- Generate DMCA takedown notices
- AI-powered piracy monitoring

## 🔧 Advanced Configuration

### Environment Variables

```bash
export SECRET_KEY="your-256-bit-secret"
export CONTENT_DIR="/path/to/encrypted/content"
export MAX_TOKEN_DURATION="7200"
export REDIS_URL="redis://localhost:6379"
export DATABASE_URL="postgresql://user:pass@localhost/ethicaldrm"
```

### Custom Watermarking

```python
# Add custom watermark
encryptor.add_watermark(
    "input.mp4", 
    "user123",
    watermark_text="Custom watermark text"
)
```

### AI Enhancement

```bash
# Install AI dependencies
pip install ethicaldrm[ai]

# Enhanced leak detection with TensorFlow/PyTorch
detector = LeakDetector(ai_enhanced=True)
```

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/devils-advocate1/ethicaldrm.git
cd ethicaldrm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -e .[dev]

# Run tests
pytest tests/

# Format code
black ethicaldrm/
flake8 ethicaldrm/
```

### Project Structure

```
ethicaldrm/
├── ethicaldrm/
│   ├── core/           # Core encryption and streaming
│   ├── api/            # Flask API server
│   ├── utils/          # Security utilities
│   ├── detectors/      # AI leak detection
│   ├── templates/      # HTML templates
│   └── cli.py          # Command line interface
├── examples/           # Example scripts
├── tests/             # Test suite
├── docker-compose.yml # Docker deployment
└── README.md          # This file
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Ramij Raj**
- 🎓 B.Tech CSE | Cybersecurity Specialist
- 🛡️ Cisco Certified: CCNA, Ethical Hacking, Cybersecurity
- 📧 Email: ramijraj31@gmail.com
- 🌐 GitHub: [@devils-advocate1](https://github.com/devils-advocate1)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## 🆘 Support

- 📖 Documentation: [Wiki](https://github.com/devils-advocate1/ethicaldrm/wiki)
- 🐛 Issues: [GitHub Issues](https://github.com/devils-advocate1/ethicaldrm/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/devils-advocate1/ethicaldrm/discussions)

---

**🔐 Built by Ramij Raj — Defending content, empowering creators.**
