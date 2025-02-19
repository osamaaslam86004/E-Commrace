""""
Key Optimizations for Your t3.micro (1 vCPU, 1GB RAM)
Removed multiprocessing: Celery already handles task queuing. Running multiple image processes in parallel would consume too much memory.
Downscaled images before processing (600px width): Reduces RAM and CPU usage before background removal.
Removed quality=95 (PNG doesn't use this setting): Used optimize=True instead for better compression.
Reduced final image size: Resized output to 800x800 instead of 1000x1000.
Sequential processing instead of batch: Processes one image at a time to prevent high RAM spikes.
"""

import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

image_extensions = (".png", ".jpg", ".jpeg", ".webp")


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


def resize_image(img, my_scale):
    """Resize image while maintaining aspect ratio."""
    img_width, img_height = img.size
    if img_height > img_width:
        hpercent = my_scale / float(img_height)
        wsize = int((float(img_width) * float(hpercent)))
        return img.resize((wsize, my_scale), Image.Resampling.LANCZOS)
    else:
        wpercent = my_scale / float(img_width)
        hsize = int((float(img_height) * float(wpercent)))
        return img.resize((my_scale, hsize), Image.Resampling.LANCZOS)


def resize_canvas(img, canvas_width, canvas_height):
    """Center image on a transparent canvas."""
    old_width, old_height = img.size
    img = img.convert("RGBA")
    new_img = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    new_img.paste(
        img,
        ((canvas_width - old_width) // 2, (canvas_height - old_height) // 2),
        mask=img,
    )
    return new_img


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

        # Resize to target size
        resized_img = resize_image(cropped_img, 500)

        # Keep a transparent background instead of white
        final_img = resize_canvas(resized_img, 800, 800)

        # Save the final image with transparency
        final_img.save(output_path, format="PNG", optimize=True)

        print(f"✅ Processed: {output_path}")

    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")


def process_images(folder_dir):
    """Sequential image processing to reduce RAM usage."""
    for entry in os.scandir(folder_dir):
        if entry.is_file() and entry.name.lower().endswith(image_extensions):
            process_single_image(entry.path)


if __name__ == "__main__":
    input_directory = r"D:\Backend\Django\programs\Amazon_EC2\media\profile-photo"
    process_images(input_directory)
