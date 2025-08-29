"""
Configuration settings for LeVibes
"""

import argparse
from pathlib import Path

# Default settings
DEFAULT_NUM_IMAGES = 5
DEFAULT_IMAGES_DIR = "./images"
DEFAULT_OUTPUT_DIR = "./output"
DEFAULT_IMAGE_SIZE = (1000, 1000)

# Font settings
FONT_NAMES = [
    "OpenSans-VariableFont_wdth,wght.ttf"
    "Montserrat-VariableFont_wght.ttf",
    "montserrat.ttf",
    "arial.ttf",
    "DejaVuSans.ttf",
]

# Image processing settings
PADDING_SCALING_FACTOR = 1.0
LINE_SPACING_RATIO = 0.4
MAX_TEXT_WIDTH_RATIO = 0.9
FONT_SIZE_RATIO = 20  # image width divided by this value

# OpenAI settings
OPENAI_MODEL = "gpt-4.1"
OPENAI_TEMPERATURE = 0.8


# Supported image formats
SUPPORTED_IMAGE_FORMATS = (".jpg", ".jpeg", ".png")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
IMAGES_DIR = PROJECT_ROOT / "images"
OUTPUT_DIR = PROJECT_ROOT / "output"

def load_cli_args():
    """Load CLI arguments."""
    parser = argparse.ArgumentParser(
        description="LeVibes - Motivational Image Caption Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --caption-source ai --num-images 10 --images-dir ./images --output-dir ./output
  python main.py -s file -n 5 -i ./images -o ./output -c ./captions.txt
  python main.py -s ai -n 3 --upload-tiktok  # Generate and upload to TikTok
        """
    )
    
    parser.add_argument(
        '-s', '--caption-source',
        choices=['ai', 'file'],
        help='Source for captions: "ai" for AI-generated, "file" for text file'
    )
    
    parser.add_argument(
        '-n', '--num-images',
        type=int,
        help=f'Number of images to generate (default: {DEFAULT_NUM_IMAGES})'
    )
    
    parser.add_argument(
        '-i', '--images-dir',
        help=f'Directory containing images to caption (default: {DEFAULT_IMAGES_DIR})'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        help=f'Directory to save captioned images (default: {DEFAULT_OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '-c', '--caption-file',
        help='Path to text file containing captions (required when using --caption-source file)'
    )
    
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation prompts and use first generated captions'
    )
    
    parser.add_argument(
        '--no-tiktok',
        action='store_true',
        help='Skip TikTok caption generation prompt'
    )
    
    parser.add_argument(
        '-m', '--model',
        default=OPENAI_MODEL,
        help=f'OpenAI model to use for caption generation (default: {OPENAI_MODEL})'
    )
    
    parser.add_argument(
        '-l', '--language',
        default='english',
        help='Language for caption generation (default: english)'
    )
    
    parser.add_argument(
        '--upload-tiktok',
        action='store_true',
        help='Upload images to TikTok as drafts after generation'
    )
    
    parser.add_argument(
        '--outro-image',
        default='outro.png',
        help='Path to outro image for TikTok uploads (default: outro.png)'
    )
    
    return parser.parse_args()