"""
OCR Module

This module handles the Optical Character Recognition (OCR) process
using Tesseract OCR with image preprocessing to improve accuracy.
"""

import os
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy for handwritten text.
    
    Args:
        image: PIL Image object
        
    Returns:
        Processed PIL Image object
    """
    # Convert to grayscale if not already
    if image.mode != 'L':
        image = image.convert('L')
    
    # Increase contrast
    image = ImageEnhance.Contrast(image).enhance(2.0)
    
    # Apply sharpening
    image = image.filter(ImageFilter.SHARPEN)
    
    # Apply threshold to make text more distinct (black and white)
    threshold = 150  # Adjust this value as needed (0-255)
    image = image.point(lambda p: 255 if p > threshold else 0)
    
    return image


def image_to_text(image_path: str) -> str:
    """
    Performs OCR on the given image and returns the extracted text.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text from the image
    """
    print(f"[OCR] Starting OCR for {image_path}")
    
    try:
        # Get Tesseract path from environment or use default
        tesseract_path = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"[OCR] Using tesseract at: {tesseract_path}")
        
        # Open and preprocess the image
        image = Image.open(image_path)
        processed = preprocess_image(image)
        
        # Configure OCR options
        # --oem 1: Use LSTM OCR Engine only
        # --psm 6: Assume a single uniform block of text
        config = r'--oem 1 --psm 6'
        
        # Perform OCR
        text = pytesseract.image_to_string(processed, config=config, lang='eng')
        
        print(f"[OCR] Extracted text for {image_path}:\n{text}\n---")
        return text
        
    except Exception as e:
        print(f"[OCR] Error processing {image_path}: {e}")
        return "" 