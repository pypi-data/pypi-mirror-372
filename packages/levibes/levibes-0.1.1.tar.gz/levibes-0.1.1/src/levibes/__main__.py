"""
LeVibes - Motivational Image Caption Generator

Module entry point for the levibes package. Enables both:
- `python -m levibes`
- console script `levibes`
"""

import os
import sys
from dotenv import load_dotenv
import gratient

from .cli import (
    display_welcome,
    get_user_inputs,
    ask_caption_source,
    get_caption_file_path,
    confirm_captions,
    ask_retry,
    display_success,
    ask_tiktok_caption,
    confirm_tiktok_upload,
)
from .caption_generation import (
    generate_captions,
    generate_tiktok_captions,
    read_captions_from_file,
)
from .generate_images import generate_images
from .utils.file_helpers import (
    create_unique_output_dir,
    ensure_directory_exists,
)
from .config import load_cli_args
from .upload import upload_to_tiktok, validate_tiktok_env, TikTokUploadError
from .utils.logger import logger, set_quiet


def validate_cli_args(args):
    """
    Validate CLI arguments and show errors if invalid.

    Args:
        args: Parsed CLI arguments

    Returns:
        True if valid, False otherwise
    """
    # If caption source is file, caption file must be provided
    if args.caption_source == "file" and not args.caption_file:
        logger.error("--caption-file is required when using --caption-source file")
        return False

    # Validate caption file exists and has enough captions
    if args.caption_file:
        if not os.path.exists(args.caption_file):
            logger.error(f"Caption file '{args.caption_file}' does not exist")
            return False

        if not os.path.isfile(args.caption_file):
            logger.error(f"'{args.caption_file}' is not a file")
            return False

        # Check if file has enough captions
        if args.num_images:
            try:
                with open(args.caption_file, "r", encoding="utf-8") as f:
                    captions = [line.strip() for line in f if line.strip()]
                    if len(captions) < args.num_images:
                        logger.error(
                            f"Caption file only contains {len(captions)} captions, but {args.num_images} images requested"
                        )
                        return False
            except Exception as e:
                logger.error(f"Error reading caption file: {e}")
                return False

    # Validate images directory
    if args.images_dir:
        if not os.path.exists(args.images_dir):
            logger.error(f"Images directory '{args.images_dir}' does not exist")
            return False

        if not os.path.isdir(args.images_dir):
            logger.error(f"'{args.images_dir}' is not a directory")
            return False

        # Check if directory has enough images
        if args.num_images:
            image_files = [
                f
                for f in os.listdir(args.images_dir)
                if f.endswith((".jpg", ".jpeg", ".png"))
            ]
            if len(image_files) < args.num_images:
                logger.error(
                    f"Images directory only contains {len(image_files)} images, but {args.num_images} images requested"
                )
                return False

    # Validate num_images is positive
    if args.num_images is not None and args.num_images <= 0:
        logger.error("Number of images must be positive")
        return False

    # If TikTok upload is enabled, validate environment variables
    if args.upload_tiktok:
        try:
            validate_tiktok_env()
        except ImportError:
            logger.error("TikTok upload module not available")
            return False
        except Exception as e:
            logger.error(f"TikTok environment validation failed: {e}")
            logger.info(
                "Please set TIKTOK_CLIENT_ID and TIKTOK_CLIENT_SECRET in your .env file"
            )
            return False

    return True


def main():
    """Main application entry point."""
    load_dotenv()

    # Load CLI arguments
    args = load_cli_args()

    # Set quiet mode if requested
    if hasattr(args, "quiet") and args.quiet:
        set_quiet(True)

    # Validate CLI arguments
    if not validate_cli_args(args):
        sys.exit(1)

    display_welcome()

    # Ask user to choose caption source (or use CLI arg)
    caption_source = ask_caption_source(args.caption_source)

    # Only check for OpenAI API key if user chooses AI
    if caption_source == "ai" and not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY is not set in your .env file")
        sys.exit(1)

    # Get user inputs (or use CLI args)
    num_images, path_to_images, output_dir = get_user_inputs(
        args.num_images, args.images_dir, args.output_dir
    )

    captions = []

    if caption_source == "ai":
        # AI-generated captions with confirmation loop
        while True:
            try:
                ai_captions = generate_captions(
                    num_images, args.model, args.language
                )

                if confirm_captions(ai_captions, args.no_confirm):
                    captions.extend(ai_captions)
                    break
                else:
                    if not ask_retry(args.no_confirm):
                        logger.info("No captions approved. Exiting.")
                        return
            except Exception as e:
                logger.error(f"Failed to generate captions: {e}")
                if not ask_retry(args.no_confirm):
                    logger.info("Exiting due to generation error.")
                    return
    else:
        while True:
            caption_file_path = get_caption_file_path(
                num_images, args.caption_file
            )
            try:
                captions = read_captions_from_file(caption_file_path, num_images)
                if confirm_captions(captions, args.no_confirm):
                    break
                else:
                    if not ask_retry(args.no_confirm):
                        logger.info("No captions approved. Exiting.")
                        return
            except (FileNotFoundError, ValueError) as e:
                logger.error(f"Error reading caption file: {e}")
                if not ask_retry(args.no_confirm):
                    logger.info("Exiting due to file error.")
                    return

    if not captions:
        logger.error("No captions were generated. Please try again.")
        return

    ensure_directory_exists(output_dir)
    unique_output_dir = create_unique_output_dir(output_dir)

    try:
        generate_images(captions, path_to_images, unique_output_dir)
        display_success(unique_output_dir)
    except Exception as e:
        logger.error(f"Failed to generate images: {e}")
        return

    # TikTok caption generation (only available with AI)
    tiktok_caption_data = None
    if caption_source == "ai" and ask_tiktok_caption(
        args.no_tiktok, args.upload_tiktok
    ):
        if args.no_confirm:
            # Skip confirmation when no_confirm is True
            try:
                tiktok_caption_data = generate_tiktok_captions(
                    1, args.model, args.language
                )
                display_caption = (
                    f"{tiktok_caption_data.title} "
                    f"{' '.join(f'#{tag}' for tag in tiktok_caption_data.hashtags)}"
                )
                confirm_captions(
                    display_caption, args.no_confirm
                )  # This will auto-confirm and display
            except Exception as e:
                logger.error(f"Failed to generate TikTok captions: {e}")
        else:
            # Normal confirmation flow
            while True:
                try:
                    tiktok_caption_data = generate_tiktok_captions(
                        1, args.model, args.language
                    )
                    # Display the structured caption for confirmation
                    display_caption = (
                        f"{tiktok_caption_data.title} "
                        f"{' '.join(f'#{tag}' for tag in tiktok_caption_data.hashtags)}"
                    )
                    if confirm_captions(display_caption, args.no_confirm):
                        break
                    else:
                        if not ask_retry(args.no_confirm):
                            logger.info("No TikTok caption approved. Exiting.")
                            return
                except Exception as e:
                    logger.error(f"Failed to generate TikTok captions: {e}")
                    if not ask_retry(args.no_confirm):
                        logger.info(
                            "Exiting due to TikTok caption generation error."
                        )
                        return

    # TikTok upload functionality
    if confirm_tiktok_upload(args.upload_tiktok):
        # Validate TikTok environment variables
        try:
            validate_tiktok_env()
        except TikTokUploadError as e:
            logger.error(f"TikTok upload not available: {e}")
            logger.info(
                "Please set TIKTOK_CLIENT_ID and TIKTOK_CLIENT_SECRET in your .env file"
            )
        else:
            # Use TikTok caption data if available, otherwise use the first regular caption
            upload_caption_data = (
                tiktok_caption_data if tiktok_caption_data else (captions[0] if captions else "")
            )

            # Upload to TikTok (always as draft)
            success = upload_to_tiktok(
                unique_output_dir, upload_caption_data, args.outro_image
            )

            if not success:
                logger.warning(
                    "TikTok upload failed. Images are still saved locally."
                )

    # Simple closing message with minimal gradient
    print("\n" + gratient.blue("Thank you for using LeVibes!"))


if __name__ == "__main__":
    main()


