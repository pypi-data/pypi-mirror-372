"""
ApolaAI - Python API Client
Connects to ApolaAI server with Gemini 2.5 Flash + 50+ textbooks
"""

import os
import requests
import json
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DEFAULT_SERVER_URL = "http://localhost:8000"
APOLAAI_SERVER_URL = os.getenv('APOLAAI_SERVER_URL', DEFAULT_SERVER_URL)

# Voice mappings (same as server)
AVAILABLE_VOICES = ["Laura", "Adam", "Antoni", "Arnold", "Bella", "Domi", "Elli", "Josh", "Rachel", "Sam"]

def generatetext(prompt, user_id=None, textbook="General", session_title="ApolaAI Session"):
    """
    Generate text using ApolaAI server (Gemini 2.5 Flash + 50+ textbooks)
    
    Args:
        prompt (str): Text prompt for generation
        user_id (str): Optional user identifier
        textbook (str): Textbook context to use
        session_title (str): Title for the chat session
        
    Returns:
        dict: {'success': bool, 'text': str, 'session_id': str, 'error': str}
    """
    if not user_id:
        user_id = f"apolaai-user-{uuid.uuid4().hex[:8]}"
    
    data = {
        "prompt": prompt,
        "user_id": user_id,
        "textbook": textbook,
        "session_title": session_title
    }
    
    try:
        response = requests.post(
            f"{APOLAAI_SERVER_URL}/api/apolaai/chat",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=90
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'text': '',
                'error': f'Server error: {response.status_code}'
            }
        
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'text': '',
            'error': f'Cannot connect to ApolaAI server at {APOLAAI_SERVER_URL}'
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'text': '',
            'error': 'Request timeout'
        }
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'error': str(e)
        }


def generateaudio(text, voice="Laura", user_id=None):
    """
    Generate audio using ApolaAI server
    
    Args:
        text (str): Text to convert to speech
        voice (str): Voice name (Laura, Adam, Antoni, etc.)
        user_id (str): Optional user identifier
        
    Returns:
        dict: {'success': bool, 'audio_path': str, 'error': str}
    """
    if not user_id:
        user_id = f"apolaai-user-{uuid.uuid4().hex[:8]}"
    
    if voice not in AVAILABLE_VOICES:
        voice = "Laura"
    
    data = {
        "text": text,
        "voice": voice,
        "user_id": user_id
    }
    
    try:
        response = requests.post(
            f"{APOLAAI_SERVER_URL}/api/apolaai/audio",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=90
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'audio_path': '',
                'error': f'Server error: {response.status_code}'
            }
        
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'audio_path': '',
            'error': f'Cannot connect to ApolaAI server at {APOLAAI_SERVER_URL}'
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'audio_path': '',
            'error': 'Request timeout'
        }
    except Exception as e:
        return {
            'success': False,
            'audio_path': '',
            'error': str(e)
        }


def generateimage(prompt, educational=False, textbook="General", user_id=None):
    """
    Generate image using ApolaAI server
    
    Args:
        prompt (str): Image description prompt
        educational (bool): Use educational context
        textbook (str): Textbook context for educational images
        user_id (str): Optional user identifier
        
    Returns:
        dict: {'success': bool, 'image_path': str, 'error': str}
    """
    if not user_id:
        user_id = f"apolaai-user-{uuid.uuid4().hex[:8]}"
    
    data = {
        "prompt": prompt,
        "user_id": user_id,
        "educational": educational,
        "textbook": textbook
    }
    
    try:
        response = requests.post(
            f"{APOLAAI_SERVER_URL}/api/apolaai/image",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'image_path': '',
                'error': f'Server error: {response.status_code}'
            }
        
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'image_path': '',
            'error': f'Cannot connect to ApolaAI server at {APOLAAI_SERVER_URL}'
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'image_path': '',
            'error': 'Request timeout'
        }
    except Exception as e:
        return {
            'success': False,
            'image_path': '',
            'error': str(e)
        }


# Utility functions
def get_available_voices():
    """
    Get list of available voices for audio generation
    
    Returns:
        list: Available voice names
    """
    return AVAILABLE_VOICES


def check_server_status():
    """
    Check if ApolaAI server is online and get status
    
    Returns:
        dict: Server status information
    """
    try:
        response = requests.get(f"{APOLAAI_SERVER_URL}/api/apolaai/status", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'status': 'offline',
                'error': f'Server returned {response.status_code}'
            }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'status': 'offline',
            'error': f'Cannot connect to server at {APOLAAI_SERVER_URL}'
        }
    except Exception as e:
        return {
            'success': False,
            'status': 'offline',
            'error': str(e)
        }


def set_server_url(url):
    """
    Set custom server URL
    
    Args:
        url (str): Server URL (e.g., 'https://your-app.railway.app')
    """
    global APOLAAI_SERVER_URL
    APOLAAI_SERVER_URL = url
    return f"Server URL set to: {APOLAAI_SERVER_URL}"


# Version info
__version__ = "2.0.0"
__all__ = ['generatetext', 'generateaudio', 'generateimage', 'get_available_voices', 'check_server_status', 'set_server_url']