import os

from PIL import Image, ImageOps
from rembg import remove

# Constants
IMAGE_EXTENSIONS = ("PNG", ".png", ".jpg", ".jpeg", ".webp")
DEFAULT_BACKGROUND_COLOR = (
    255,
    255,
    255,
    255,
)  # White background (change for branding)


def autocrop(img, border=10):
    """
    Crop empty space around the product after background removal.
    Adds a border for a better visual appearance.
    """
    bbox = img.getbbox()
    if not bbox:
        return img
    cropped = img.crop(bbox)

    if border:
        return ImageOps.expand(cropped, border, DEFAULT_BACKGROUND_COLOR)
    else:
        """
        Crop empty space around the product after background removal.
        No border is added for a cleaner appearance.
        """

    return cropped


def process_product_image(image_path):
    """
    Process a single product image with background removal, cropping, and resizing.
    Handles errors to avoid crashing on corrupt or unsupported images.
    """
    try:
        # Try opening the image with Pillow
        with Image.open(image_path) as img:
            img = img.convert("RGBA")  # Ensure it's in RGBA mode

            # Remove background with fine details (Alpha Matting enabled)
            processed_img = remove(
                img,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_structure_size=10,
                alpha_matting_base_size=1000,
            )

            # Without Alpha matting
            # processed_img = remove(img)

            # Crop empty space
            cropped_img = autocrop(processed_img)

            # Save as PNG with transparency
            output_path = image_path.replace(".jpg", "_processed.png").replace(
                ".jpeg", "_processed.png"
            )
            cropped_img.save(output_path, format="PNG", quality=90)

            # Convert the output png of rembg to webp to reduce size by 5x
            # output_path = (
            #     image_path.replace(".jpg", "_processed.webp")
            #     .replace(".jpeg", "_processed.webp")
            #     .replace(".png", "_processed.webp")
            # )

            # cropped_img.save(output_path, format="WEBP", quality=90)

            print(f"✅ Processed: {output_path}")
            return output_path

    except OSError:
        print(f"❌ Skipping {image_path}: Corrupt or unsupported image format.")
    except MemoryError:
        print(f"❌ Skipping {image_path}: Not enough memory to process.")
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")

    return None


def process_images(folder_dir):
    """Sequential image processing to reduce RAM usage."""

    for entry in os.scandir(folder_dir):
        if entry.is_file() and entry.name.lower().endswith(IMAGE_EXTENSIONS):
            process_product_image(entry.path)


if __name__ == "__main__":
    input_directory = r"D:\Backend\Django\programs\Amazon_EC2\media\profile-photo"
    process_images(input_directory)
