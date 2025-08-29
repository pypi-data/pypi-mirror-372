"""
Caption generation using OpenAI API
"""

import os
from openai import OpenAI
from pydantic import BaseModel
from .config import OPENAI_MODEL, OPENAI_TEMPERATURE
from .utils.logger import logger


class Captions(BaseModel):
    captions: list[str]


class TikTokCaption(BaseModel):
    title: str
    hashtags: list[str]


client = None


def read_captions_from_file(file_path, num_images):
    """
    Read captions from a text file.

    Args:
        file_path (str): Path to the text file containing captions
        num_images (int): Number of captions needed

    Returns:
        list: List of captions read from the file

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file doesn't contain enough captions
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Caption file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        captions = [line.strip() for line in file if line.strip()]

    if len(captions) < num_images:
        raise ValueError(
            f"Not enough captions in file. Found {len(captions)}, need {num_images}"
        )

    return captions[:num_images]


def generate_captions(num_images, model=OPENAI_MODEL, language='english'):
    """Generate captions using OpenAI API"""
    global client
    if client is None:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    language_text = f" in {language}" if language.lower() != 'english' else ""
    logger.progress(f"Generating captions with {model}{language_text}")
    
    try:
        openai_response = client.responses.parse(
            model=model,
            temperature=OPENAI_TEMPERATURE,
            input=[{"role": "user", "content": generate_prompt(num_images, language)}],
            text_format=Captions,
        )

        if openai_response.output_parsed is None:
            raise ValueError("No captions generated")

        logger.success(f"Generated {len(openai_response.output_parsed.captions)} captions")
        return openai_response.output_parsed.captions
    except Exception as e:
        logger.error(f"Caption generation failed: {e}")
        raise


def generate_tiktok_captions(num_captions=1, model=OPENAI_MODEL, language='english'):
    """Generate TikTok captions using OpenAI API"""
    global client
    if client is None:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    language_text = f" in {language}" if language.lower() != 'english' else ""
    logger.progress(f"Generating TikTok captions with {model}{language_text}")
    
    try:
        openai_response = client.responses.parse(
            model=model,
            temperature=OPENAI_TEMPERATURE,
            input=[{"role": "user", "content": generate_tiktok_prompt(num_captions, language)}],
            text_format=TikTokCaption,
        )

        if openai_response.output_parsed is None:
            raise ValueError("No TikTok captions generated")

        logger.success("Generated TikTok caption")
        return openai_response.output_parsed
    except Exception as e:
        logger.error(f"TikTok caption generation failed: {e}")
        raise


def generate_prompt(num_images, language='english'):
    """Generate prompt for caption generation"""
    base_prompt = f"""Generate {num_images} motivational phrases in all lowercase, under 13 words each. These will be accompanied by a happy picture of LeBron James. Match this style exactly:

if you went back in time to erase all of your mistakes you would erase yourself
the strongest steel is forged in the hottest fire
all our dreams can come true if we have the courage to pursue them
shoot for the moon. even if you miss, you'll land among the stars

Requirements: deep, philosophical, resonate with young people, minimal use of "you/your", no em dashes or ellipses. You may occasionally use formats like "when you finally realize x" but don't overuse this pattern."""
    
    if language.lower() == 'english':
        return base_prompt
    else:
        return f"""{base_prompt}

IMPORTANT: Generate all captions in {language}. Make sure the motivational phrases are culturally appropriate and resonate with young people who speak {language}. Maintain the same style and format but translate the sentiment and meaning into {language}."""


def generate_tiktok_prompt(num_captions, language='english'):
    """Generate prompt for TikTok caption generation"""
    base_prompt = f"""Generate {num_captions} TikTok caption(s) that will be accompanied by motivational images with separate title and hashtags. After the inspirational hashtags, add some others that should be themed to basketball, the NBA, and LeBron James.

Return the response as structured data with:
- "title": An inspirational quote in all lowercase (similar to examples below)
- "hashtags": A list of 3-5 hashtags related to inspiration and motivation

Keep the quote 6 words or less and make it simple and clean, but effective. Keep in mind the audience of TikTok."""
    
    if language.lower() == 'english':
        return base_prompt
    else:
        return f"""{base_prompt}

IMPORTANT: Generate the inspirational quote in {language}. Make sure the quote is culturally appropriate and resonates with young people who speak {language}. The hashtags should be in English as they're for international reach, but the quote itself should be in {language}."""
