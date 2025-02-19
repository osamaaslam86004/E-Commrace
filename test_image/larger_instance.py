import math
import os
from multiprocessing import Pool, cpu_count
from pathlib import Path

import cv2  # OpenCV for fast image processing
from PIL import Image
from rembg import remove

"""
1. 🔧 Fix for Transparent Background
2. Modify the resize_canvas function so it keeps transparency rather than replacing it with a white background.
3. Ensure the output image is saved with transparency
4. Ensure rembg.remove() outputs RGBA images
✔️ The script will still be fast and efficient for larger EC2 Instance.

References:
1. https://medium.com/@nimritakoul01/image-processing-using-opencv-python-9c9b83f4b1ca
"""


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

    # Ensure image has an alpha channel (transparency)
    img = img.convert("RGBA")

    # Create a transparent background
    new_img = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

    # Paste image in the center
    new_img.paste(
        img,
        ((canvas_width - old_width) // 2, (canvas_height - old_height) // 2),
        mask=img,
    )

    return new_img


def fast_resize_with_opencv(image_path, new_width=800):
    """Quickly resize image using OpenCV."""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    height, width = img.shape[:2]
    aspect_ratio = height / width
    new_height = int(new_width * aspect_ratio)
    img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))


def process_single_image(image_path):
    """Process a single image while keeping transparency."""
    try:
        output_path = append_id(image_path)

        # Fast resize before removing background
        img = fast_resize_with_opencv(image_path, 800).convert("RGBA")

        # Remove background
        removed_bg_img = remove(img).convert("RGBA")

        # Crop excess space
        cropped_img = autocrop_image(removed_bg_img, 0)

        # Resize to target size
        resized_img = resize_image(cropped_img, 700)

        # Keep a transparent background instead of white
        final_img = resize_canvas(resized_img, 1000, 1000)

        # Save the final image with transparency
        final_img.save(output_path, format="PNG", quality=95)

        print(f"✅ Processed: {output_path}")

    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")


def process_images(folder_dir):
    """Process images in parallel using multiprocessing."""
    image_paths = [
        os.path.join(folder_dir, entry.name)
        for entry in os.scandir(folder_dir)
        if entry.is_file() and entry.name.lower().endswith(image_extensions)
    ]

    # Run image processing in parallel using all CPU cores
    with Pool(cpu_count()) as pool:
        pool.map(process_single_image, image_paths)


if __name__ == "__main__":
    input_directory = r"D:\Backend\Django\programs\Amazon_EC2\media\profile-photo"
    process_images(input_directory)
