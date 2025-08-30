import logging
from pathlib import Path

import click

from .convert import compress_animated_webp, compress_image_to_webp

# Supported image formats
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp"}


def is_animated_image(image_path: Path) -> bool:
    """
    Check if an image is animated (has multiple frames).

    Args:
        image_path: Path to the image file

    Returns:
        True if the image is animated, False otherwise
    """
    try:
        from PIL import Image

        with Image.open(image_path) as img:
            # Try to seek to the second frame
            img.seek(1)
            return True
    except (EOFError, IndexError):
        # No second frame found, not animated
        return False
    except Exception:
        # Error reading image, assume not animated
        return False


def process_single_image(
    root_output_dir: Path, image_file: Path, input_dir: Path, recursive: bool, quality: int
) -> tuple[bool, int, int]:
    """
    Process a single image file.

    Args:
        root_output_dir: Root output directory
        image_file: Path to the image file to process
        input_dir: Input directory (for relative path calculation)
        recursive: Whether we're in recursive mode
        quality: Quality for lossy compression

    Returns:
        Tuple of (success: bool, original_size: int, compressed_size: int)
    """
    # Determine output directory for this file
    if recursive:
        relative_path = image_file.relative_to(input_dir)
        file_output_dir = root_output_dir / relative_path.parent
    else:
        file_output_dir = root_output_dir

    # Create output directory if it doesn't exist
    file_output_dir.mkdir(parents=True, exist_ok=True)

    # Skip if output file already exists
    output_file = file_output_dir / f"{image_file.stem}.webp"
    if output_file.exists():
        logging.info(f"Skipping {image_file.name} (output already exists)")
        return False, 0, 0

    # Check if image is animated
    if is_animated_image(image_file):
        logging.info(f"Processing animated image: {image_file.name}")
        _, compressed_size = compress_animated_webp(input_path=image_file, output_dir=file_output_dir, quality=quality)
    else:
        # Process the image
        _, compressed_size = compress_image_to_webp(input_path=image_file, output_dir=file_output_dir, quality=quality)

    original_size = image_file.stat().st_size
    return True, original_size, compressed_size


def process_directory(input_dir: Path, output_dir: Path | None, quality: int, recursive: bool = False):
    """
    Process all image files in a directory.

    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        quality: Quality for lossy compression
        recursive: Whether to process subdirectories recursively
    """
    processed_count = 0
    error_count = 0
    total_original_size = 0
    total_compressed_size = 0

    image_files = []
    # Get all image files in the directory
    if recursive:
        for ext in SUPPORTED_FORMATS:
            image_files.extend(input_dir.rglob(f"*{ext}"))
    else:
        for ext in SUPPORTED_FORMATS:
            image_files.extend(input_dir.glob(f"*{ext}"))

    if not image_files:
        logging.warning(f"No supported image files found in {input_dir}")
        return processed_count, error_count

    logging.info(f"Found {len(image_files)} image files to process")
    logging.debug(f"image_files: {image_files}")

    if output_dir is None:
        root_output_dir = input_dir
    else:
        root_output_dir = output_dir

    for image_file in image_files:
        try:
            success, original_size, compressed_size = process_single_image(
                root_output_dir=root_output_dir,
                image_file=image_file,
                input_dir=input_dir,
                recursive=recursive,
                quality=quality,
            )

            if success:
                total_original_size += original_size
                total_compressed_size += compressed_size
                processed_count += 1

        except Exception as e:
            logging.error(f"Error processing {image_file}: {e}")
            error_count += 1

    return processed_count, error_count, total_original_size, total_compressed_size


@click.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir", "-o", type=click.Path(path_type=Path), help="Output directory (defaults to input file directory)"
)
@click.option(
    "--quality",
    "-q",
    type=click.IntRange(1, 100),
    default=80,
    help="Quality for lossy compression (1-100, default: 80)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--recursive", "-r", is_flag=True, help="Process directories recursively")
def main(input_path: Path, output_dir: Path, quality: int, verbose: bool, recursive: bool):
    """
    Compress an image to WebP format using optimal compression.

    The tool will try both lossless and lossy compression and save the smaller file.
    If INPUT_PATH is a directory, all image files in it will be processed.

    INPUT_PATH: Path to the input image file or directory
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s", handlers=[logging.StreamHandler()])

    try:
        if input_path.is_file():
            # Process single file
            if is_animated_image(input_path):
                logging.info(f"Processing animated image: {input_path.name}")
                result_path, _ = compress_animated_webp(input_path=input_path, output_dir=output_dir, quality=quality)
            else:
                result_path, _ = compress_image_to_webp(input_path=input_path, output_dir=output_dir, quality=quality)
            click.echo(f"✅ Successfully compressed: {result_path}")

        elif input_path.is_dir():
            # Process directory
            logging.info(f"Processing directory: {input_path}")
            processed_count, error_count, total_original_size, total_compressed_size = process_directory(
                input_dir=input_path, output_dir=output_dir, quality=quality, recursive=recursive
            )

            if error_count > 0:
                click.echo(f"⚠️  Completed with {error_count} errors")
            else:
                click.echo(f"✅ Successfully processed {processed_count} files")

            # Display total compression statistics
            if processed_count > 0:
                total_reduction_percent = ((total_original_size - total_compressed_size) / total_original_size) * 100
                total_saved_mb = (total_original_size - total_compressed_size) / (1024 * 1024)
                click.echo(
                    f"📊 Total compression: {total_original_size:,} bytes → {total_compressed_size:,} bytes (-{total_reduction_percent:.1f}%, saved {total_saved_mb:.1f} MB)"  # noqa: E501
                )

        else:
            click.echo(f"❌ Error: {input_path} is neither a file nor a directory", err=True)
            exit(1)

    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        exit(1)


if __name__ == "__main__":
    main()
