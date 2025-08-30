import os
import logging
from pathlib import Path
from PIL import Image
import io


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
    original_format = input_path.suffix.upper().lstrip('.')
    
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
        # Convert to RGB if necessary (WebP doesn't support RGBA)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background for transparent images
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create lossless version
        lossless_buffer = io.BytesIO()
        img.save(lossless_buffer, format='WEBP', lossless=True)
        lossless_size = lossless_buffer.tell()
        
        # Create lossy version
        lossy_buffer = io.BytesIO()
        img.save(lossy_buffer, format='WEBP', quality=quality, optimize=True)
        lossy_size = lossy_buffer.tell()
        
        # Choose the smaller file
        if lossy_size <= lossless_size:
            # Save lossy version
            lossy_buffer.seek(0)
            with open(output_path, 'wb') as f:
                f.write(lossy_buffer.read())
            
            # Calculate reduction percentage
            reduction_percent = ((original_size - lossy_size) / original_size) * 100
            logging.info(f"{original_format} ({original_size} bytes) → WebP (lossy): {output_path} ({lossy_size} bytes, -{reduction_percent:.1f}%)")
            compressed_size = lossy_size
        else:
            # Save lossless version
            lossless_buffer.seek(0)
            with open(output_path, 'wb') as f:
                f.write(lossless_buffer.read())
            
            # Calculate reduction percentage
            reduction_percent = ((original_size - lossless_size) / original_size) * 100
            logging.info(f"{original_format} ({original_size} bytes) → WebP (lossless): {output_path} ({lossless_size} bytes, -{reduction_percent:.1f}%)")
            compressed_size = lossless_size
    
    return output_path, compressed_size
