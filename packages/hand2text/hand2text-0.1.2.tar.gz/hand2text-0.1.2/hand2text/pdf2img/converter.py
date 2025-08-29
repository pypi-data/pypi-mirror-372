"""
PDF to Image Converter Module

This module handles the conversion of PDF files to images.
It uses PyMuPDF (fitz) to read the PDF and PIL to save the images.
"""

import os

import fitz  # PyMuPDF
from PIL import Image


def pdf_to_images(pdf_path: str, output_folder: str) -> None:
    """
    Converts each page of a PDF into separate image files in the output folder.

    Args:
        pdf_path: Path to the input PDF file
        output_folder: Directory where image files will be saved

    Returns:
        None
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Open PDF document
    pdf_document = fitz.open(pdf_path)

    # Process each page
    for page_number in range(pdf_document.page_count):
        # Get page
        page = pdf_document[page_number]

        # Convert page to pixmap (image)
        pixmap = page.get_pixmap()

        # Determine color mode based on pixmap properties
        mode = "RGB" if pixmap.n < 5 else "CMYK"

        # Convert pixmap to PIL Image
        image = Image.frombytes(mode, (pixmap.width, pixmap.height), pixmap.samples)

        # Save image to output folder
        image_path = os.path.join(output_folder, f"page_{page_number + 1}.png")
        image.save(image_path)

        print(f"Page {page_number + 1} converted and saved as {image_path}")

    # Close PDF document
    pdf_document.close()
