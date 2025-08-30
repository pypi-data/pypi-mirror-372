# tool-webp-converter

A Python tool for optimal WebP image compression that automatically chooses between lossless and lossy compression to achieve the smallest file size.

## Why WebP?

WebP is a modern image format developed by Google that provides superior compression for images on the web. It offers:

- **Better compression**: 25-35% smaller file sizes compared to JPEG and PNG
- **Lossless and lossy compression**: Choose the best compression method for your needs
- **Transparency support**: Like PNG, but with better compression
- **Animation support**: Similar to GIF but with much smaller file sizes
- **Wide browser support**: Supported by all modern browsers

## Installation

Install the package from PyPI:

```bash
pip install tool-webp-converter
```

## Usage

The tool provides a command-line interface for converting images to WebP format. It automatically tests both lossless and lossy compression and saves the smaller file.

### Basic Usage

Convert a single image:
```bash
webp-converter image.jpg
```

Convert all images in a directory:
```bash
webp-converter /path/to/images/
```

### Command Line Options

```bash
webp-converter [OPTIONS] INPUT_PATH
```

**Arguments:**
- `INPUT_PATH`: Path to the input image file or directory

**Options:**
- `-o, --output-dir PATH`: Output directory (defaults to input file directory)
- `-q, --quality INTEGER`: Quality for lossy compression (1-100, default: 80)
- `-v, --verbose`: Enable verbose logging
- `-r, --recursive`: Process directories recursively

### Examples

Convert a single image with custom quality:
```bash
webp-converter photo.jpg --quality 90
```

Convert all images in a directory to a specific output folder:
```bash
webp-converter /path/to/images/ --output-dir /path/to/output/
```

Process a directory recursively (including subdirectories):
```bash
webp-converter /path/to/images/ --recursive
```

### Supported Formats

The tool supports the following input formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- GIF (.gif)
- WebP (.webp)

### How It Works

1. **Dual Compression**: The tool creates both lossless and lossy WebP versions
2. **Automatic Selection**: It automatically saves the smaller file
3. **Quality Control**: You can adjust the quality for lossy compression (1-100)
4. **Batch Processing**: Process single files or entire directories
5. **Recursive Support**: Optionally process subdirectories

### Output

The tool provides detailed feedback including:
- Compression statistics (original vs compressed size)
- Percentage reduction achieved
- Total space saved for batch operations
- Error reporting for failed conversions

## Development

This project uses Poetry for dependency management. To set up the development environment:

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run the tool
python -m tool_webp_converter.cli image.jpg
``` 