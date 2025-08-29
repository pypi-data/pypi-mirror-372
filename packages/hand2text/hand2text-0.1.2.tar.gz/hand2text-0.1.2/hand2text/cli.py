"""
Command Line Interface for the hand2text application.
This module handles the command-line arguments and passes them to the main function.
"""

import argparse

from .main import main


def run() -> None:
    """
    Parse command-line arguments and run the main function.
    """
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Convert handwritten PDF notes to text. Output directories are derived from the PDF name."
    )

    # Define arguments
    parser.add_argument("pdf_path", help="Path to the input PDF file")

    # Parse arguments
    args = parser.parse_args()

    # Run main function with parsed arguments
    main(args.pdf_path)


if __name__ == "__main__":
    run()
