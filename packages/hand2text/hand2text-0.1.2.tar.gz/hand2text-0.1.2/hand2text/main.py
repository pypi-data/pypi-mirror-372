"""
Main Module for Hand2Text

This is the main entry point for the Hand2Text application, which converts
handwritten PDF notes to text. It coordinates the following pipeline:
1. Convert PDF to images
2. Use Vision LLM (or OCR+LLM fallback) to transcribe text
3. Save the results to text files
"""

import os
import sys

from .combine_texts import combine_texts
from .llm.vision_llm import vision_llm_transcribe
from .pdf2img.converter import pdf_to_images


def main(
    pdf_path: str,
    output_img_folder: str | None = None,
    output_txt_folder: str | None = None,
) -> None:
    """
    Main function that runs the entire PDF-to-text pipeline.

    Args:
        pdf_path: Path to the input PDF file
        output_img_folder: Folder where extracted images will be saved
        output_txt_folder: Folder where output text files will be saved

    Returns:
        None
    """
    pdf_base = os.path.splitext(os.path.basename(pdf_path))[0]
    if output_img_folder is None:
        output_img_folder = pdf_base + "_images"
    if output_txt_folder is None:
        output_txt_folder = pdf_base + "_text"
    print(
        f"[MAIN] Starting pipeline with {pdf_path} -> {output_img_folder} -> {output_txt_folder}"
    )

    # Step 1: Convert PDF to images
    pdf_to_images(pdf_path, output_img_folder)
    print("[MAIN] Finished PDF to images. Listing images...")

    # Step 2: Process each image to extract text
    os.makedirs(output_txt_folder, exist_ok=True)

    # Get all PNG images from the output folder
    image_files = sorted(
        [f for f in os.listdir(output_img_folder) if f.lower().endswith(".png")]
    )
    print(f"[MAIN] Found images: {image_files}")

    # Process each image
    for img_file in image_files:
        img_path = os.path.join(output_img_folder, img_file)
        print(f"[MAIN] Processing {img_path}...")

        try:
            # Use Vision LLM to transcribe the handwritten text
            # (has built-in fallback to OCR+LLM if vision models aren't available)
            transcribed_text = vision_llm_transcribe(img_path)
            print(f"[MAIN] Transcribed text: {transcribed_text}")

            # Save the transcribed text
            txt_filename = os.path.splitext(img_file)[0] + ".txt"
            txt_path = os.path.join(output_txt_folder, txt_filename)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcribed_text)

            print(f"[MAIN] Saved transcribed text to {txt_path}")

        except Exception as e:
            print(f"[MAIN] Error processing {img_path}: {e}")
            print("[MAIN] Continuing with next image...")

    # Delete images after processing
    for img_file in image_files:
        os.remove(os.path.join(output_img_folder, img_file))
    print(f"[MAIN] Deleted all images in {output_img_folder}")

    # Combine text files and cleanup
    combine_texts(output_txt_folder, combined_name=pdf_base + "_combined.txt")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print(
            "Usage: python main.py <pdf_path> [<output_img_folder> <output_txt_folder>]"
        )
        print("Or use the CLI: python cli.py <pdf_path>")
