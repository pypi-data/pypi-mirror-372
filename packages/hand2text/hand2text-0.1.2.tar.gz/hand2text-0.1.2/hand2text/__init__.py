"""
Hand2Text: Convert handwritten PDF notes to text using OCR and LLM

This package provides functionality to:
1. Convert PDF files to images
2. Extract handwritten text using Vision LLM or OCR+LLM
3. Combine extracted text into a single document
"""

__version__ = "0.1.2"

from .main import main

__all__ = ["main"]
