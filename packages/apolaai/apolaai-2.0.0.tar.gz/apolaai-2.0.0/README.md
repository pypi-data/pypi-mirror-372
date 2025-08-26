# ApolaAI Python Client

🚀 **Connect to ApolaAI server powered by Gemini 2.5 Flash + 50+ Sri Lankan textbooks**

## Installation

```bash
pip install apolaai
```

## Quick Start

```python
from apolaai import generatetext, generateaudio, generateimage, set_server_url

# Configure server (if not using default)
set_server_url("https://your-apolaai-server.railway.app")

# Generate educational content with textbook context
result = generatetext(
    "Explain photosynthesis in simple terms",
    textbook="Grade 06 Science",
    user_id="student-1"
)

if result['success']:
    print(result['text'])
```

## Features

- 🔤 **Smart Text Generation** - Contextual responses using 50+ textbooks
- 🔊 **Audio Generation** - High-quality text-to-speech
- 🖼️ **Educational Images** - Curriculum-aligned visual content
- 📚 **Textbook Integration** - Grade 6-11 Sri Lankan curriculum
- 🎯 **Simple API** - Easy-to-use functions with consistent responses

## Functions

```python
from apolaai import (
    generatetext,        # Generate text with textbook context
    generateaudio,       # Convert text to speech
    generateimage,       # Create educational images
    check_server_status, # Check server health
    set_server_url,      # Configure server endpoint
    get_available_voices # List available voices
)
```

## Example Usage

```python
import apolaai

# Check server status
status = apolaai.check_server_status()
print(f"Server: {status['status']}")

# Generate educational content
result = apolaai.generatetext(
    "What is the water cycle?",
    textbook="Grade 07 Geography"
)

if result['success']:
    print(result['text'])
```

## Requirements

- Python 3.7+
- Access to ApolaAI server

## Links

- 🌐 Website: https://apolaai.com
- 📚 Documentation: https://apolaai.com/docs
- 🐛 Issues: https://github.com/apolaai/apolaai-python/issues

---

Made with ❤️ for Sri Lankan education by ApolaAI