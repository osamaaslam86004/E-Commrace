""""
Key Optimizations for Your t3.micro (1 vCPU, 1GB RAM)

Downscaled images before processing (600px width): Reduces RAM and CPU usage before background removal.
Auto-Crop to reduce image size
Sequential processing instead of batch: Processes one image at a time to prevent high RAM spikes.

Removed multiprocessing: Celery already handles task queuing. Running multiple image processes in parallel would consume too much memory.
Removed quality=95 (PNG doesn't use this setting): Used optimize=True instead for better compression.
"""

import os
from pathlib import Path

import cv2
from PIL import Image
from rembg import remove

# Constants
IMAGE_EXTENSIONS = ("PNG", ".png", ".jpg", ".jpeg", ".webp")
DEFAULT_BACKGROUND_COLOR = (
    255,
    255,
    255,
    255,
)  # White background (change for branding)


def append_id(filename):
    """Append '_Processed' to filenames."""
    p = Path(filename)
    return f"{p.parent}/{p.stem}_Processed.png"


def autocrop_image(img, border=0):
    """Crop empty areas around the product."""
    bbox = img.getbbox()
    if not bbox:
        return img
    img = img.crop(bbox)
    scale, height = img.size
    scale += border * 2
    height += border * 2
    cropped_image = Image.new("RGBA", (scale, height), (0, 0, 0, 0))
    cropped_image.paste(img, (border, border))
    return cropped_image


# def autocrop_image(img, border=10):
#     """
#     Crop empty space around the product after background removal.
#     Adds a border for a better visual appearance.
#     """
#     bbox = img.getbbox()
#     if not bbox:
#         return img
#     cropped = img.crop(bbox)

#     if border:
#         return ImageOps.expand(cropped, border, DEFAULT_BACKGROUND_COLOR)
#     else:
#         """
#         Crop empty space around the product after background removal.
#         No border is added for a cleaner appearance.
#         """

#     return cropped


def fast_resize_with_opencv(image_path, new_width=600):
    """Quickly resize image using OpenCV before processing (to save RAM)."""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    height, width = img.shape[:2]
    aspect_ratio = height / width
    new_height = int(new_width * aspect_ratio)
    img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))


def process_single_image(image_path):
    """Process a single image while keeping transparency."""
    try:
        output_path = append_id(image_path)

        # Resize before background removal to reduce memory usage
        img = fast_resize_with_opencv(image_path, 600)
        if img is None:
            print(f"❌ Skipping {image_path} (Invalid Image)")
            return

        img = img.convert("RGBA")  # Ensure transparency support

        # Remove background (can be slow, so keep it as the main processing step)
        removed_bg_img = remove(img).convert("RGBA")

        # Crop excess space
        cropped_img = autocrop_image(removed_bg_img, 0)

        cropped_img.save(output_path, format="PNG", optimize=True)
        print(f"✅ Processed: {output_path}")

    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")


def process_images(folder_dir):
    """Sequential image processing to reduce RAM usage."""
    for entry in os.scandir(folder_dir):
        if entry.is_file() and entry.name.lower().endswith(IMAGE_EXTENSIONS):
            process_single_image(entry.path)


if __name__ == "__main__":
    input_directory = r"D:\Backend\Django\programs\Amazon_EC2\media\profile-photo"
    process_images(input_directory)
