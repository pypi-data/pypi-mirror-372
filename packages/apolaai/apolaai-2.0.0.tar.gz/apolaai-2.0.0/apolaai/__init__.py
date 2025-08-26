"""
ApolaAI - Python API for AI Generation
Simple and easy-to-use functions for text, audio, and image generation
"""

from .apolaai import generatetext, generateaudio, generateimage, get_available_voices, check_server_status, set_server_url

__version__ = "2.0.0"
__author__ = "ApolaAI"
__description__ = "Python API client for ApolaAI server with Gemini 2.5 Flash + 50+ textbooks"

__all__ = ['generatetext', 'generateaudio', 'generateimage', 'get_available_voices', 'check_server_status', 'set_server_url']