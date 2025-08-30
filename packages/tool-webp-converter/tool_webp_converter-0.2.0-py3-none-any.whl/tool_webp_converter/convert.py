import io
import logging
from pathlib import Path

from PIL import Image


def compress_image_to_webp(input_path: Path, output_dir: Path = None, quality: int = 80) -> tuple[Path, int]:
    """
    Compress an image to WebP format using both lossless and lossy compression,
    then save the one with the smallest file size.

    Args:
        input_path: Path to the input image file
        output_dir: Directory to save the output file (defaults to input directory)
        quality: Quality for lossy compression (1-100, default 80)

    Returns:
        Tuple of (Path to the saved WebP file, compressed file size in bytes)
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Get original file size and format
    original_size = input_path.stat().st_size
    original_format = input_path.suffix.upper().lstrip(".")

    # Set output directory
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename
    output_name = input_path.stem + ".webp"
    output_path = output_dir / output_name

    # Open the image
    with Image.open(input_path) as img:
        # Handle different image modes
        if img.mode == "P":
            # Convert palette-based images to RGBA to preserve transparency
            img = img.convert("RGBA")
        elif img.mode == "LA":
            # Convert grayscale with alpha to RGBA
            img = img.convert("RGBA")
        elif img.mode not in ("RGB", "RGBA"):
            # Convert other modes to RGB (no transparency)
            img = img.convert("RGB")

        # Check if image has transparency (RGBA mode with non-opaque alpha)
        has_transparency = False
        if img.mode == "RGBA":
            # Check if any pixel has alpha < 255
            alpha_channel = img.split()[-1]
            if alpha_channel.getextrema()[1] < 255:
                has_transparency = True
                logging.debug("Image has transparency, preserving RGBA mode")

        # Create lossless version
        lossless_buffer = io.BytesIO()
        img.save(lossless_buffer, format="WEBP", lossless=True)
        lossless_size = lossless_buffer.tell()

        # Create lossy version
        lossy_buffer = io.BytesIO()
        img.save(lossy_buffer, format="WEBP", quality=quality, optimize=True)
        lossy_size = lossy_buffer.tell()

        # Choose the smaller file
        if lossy_size <= lossless_size:
            # Save lossy version
            lossy_buffer.seek(0)
            with open(output_path, "wb") as f:
                f.write(lossy_buffer.read())

            # Calculate reduction percentage
            reduction_percent = ((original_size - lossy_size) / original_size) * 100
            compression_type = "lossy"
            compressed_size = lossy_size
        else:
            # Save lossless version
            lossless_buffer.seek(0)
            with open(output_path, "wb") as f:
                f.write(lossless_buffer.read())

            # Calculate reduction percentage
            reduction_percent = ((original_size - lossless_size) / original_size) * 100
            compression_type = "lossless"
            compressed_size = lossless_size

        # Log the conversion details
        mode_info = f"({img.mode})" if img.mode != "RGB" else ""
        transparency_info = " with transparency" if has_transparency else ""
        logging.info(
            f"{original_format} ({original_size} bytes) → WebP ({compression_type}){mode_info}{transparency_info}: {output_path} ({compressed_size} bytes, -{reduction_percent:.1f}%)"  # noqa: E501
        )

    return output_path, compressed_size


def compress_animated_webp(input_path: Path, output_dir: Path = None, quality: int = 80) -> tuple[Path, int]:
    """
    Compress an animated image to animated WebP format.

    Args:
        input_path: Path to the input animated image file (GIF, etc.)
        output_dir: Directory to save the output file (defaults to input directory)
        quality: Quality for lossy compression (1-100, default 80)

    Returns:
        Tuple of (Path to the saved WebP file, compressed file size in bytes)
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Get original file size and format
    original_size = input_path.stat().st_size
    original_format = input_path.suffix.upper().lstrip(".")

    # Set output directory
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename
    output_name = input_path.stem + ".webp"
    output_path = output_dir / output_name

    # Open the animated image
    with Image.open(input_path) as img:
        # Extract frames and durations
        frames = []
        durations = []
        frame_count = 0

        try:
            while True:
                # Get frame duration (default to 100ms if not available)
                duration = img.info.get("duration", 100)
                durations.append(duration)

                # Convert frame to appropriate mode
                frame = img.copy()
                if frame.mode == "P":
                    frame = frame.convert("RGBA")
                elif frame.mode == "LA":
                    frame = frame.convert("RGBA")
                elif frame.mode not in ("RGB", "RGBA"):
                    frame = frame.convert("RGB")

                frames.append(frame)
                frame_count += 1

                # Try to go to next frame
                try:
                    img.seek(frame_count)
                except EOFError:
                    break
        except EOFError:
            pass  # End of frames

        if len(frames) == 1:
            # Single frame, use regular compression
            logging.info("Single frame detected, using regular compression")
            return compress_image_to_webp(input_path, output_dir, quality)

        logging.info(f"Processing animated image with {len(frames)} frames")

        # Save as animated WebP
        buffer = io.BytesIO()
        frames[0].save(
            buffer,
            format="WEBP",
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,  # Loop indefinitely
            quality=quality,
            optimize=True,
            background=(0, 0, 0, 0),  # Transparent background
        )

        compressed_size = len(buffer.getvalue())
        buffer.seek(0)

        with open(output_path, "wb") as f:
            f.write(buffer.read())

        # Calculate reduction percentage
        reduction_percent = ((original_size - compressed_size) / original_size) * 100
        logging.info(
            f"{original_format} animated ({original_size} bytes) → WebP animated ({len(frames)} frames): {output_path} ({compressed_size} bytes, -{reduction_percent:.1f}%)"  # noqa: E501
        )

    return output_path, compressed_size
