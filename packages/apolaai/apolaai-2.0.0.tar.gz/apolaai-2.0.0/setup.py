#!/usr/bin/env python
"""
Setup script for ApolaAI Python package
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Python API client for ApolaAI server with Gemini 2.5 Flash + 50+ textbooks"

setup(
    name="apolaai",
    version="2.0.0",
    author="ApolaAI",
    author_email="support@apolaai.com",
    description="Python API client for ApolaAI server with Gemini 2.5 Flash + 50+ textbooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/apolaai/apolaai-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    keywords=[
        "ai", "artificial intelligence", "text generation", "audio generation", 
        "image generation", "gemini", "elevenlabs", "education", "textbooks",
        "sri lanka", "apolaai", "machine learning", "nlp"
    ],
    project_urls={
        "Bug Reports": "https://github.com/apolaai/apolaai-python/issues",
        "Source": "https://github.com/apolaai/apolaai-python",
        "Documentation": "https://apolaai.com/docs",
        "Website": "https://apolaai.com",
    },
)