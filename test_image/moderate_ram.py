# Use Case
# The primary use case for the rembg library is in scenarios where you want to isolate a subject or object from its background in images. Some common applications include:

# E-commerce: Automatically remove backgrounds from product images to create clean, professional-looking listings.

# Graphic Design: Easily create designs with transparent backgrounds for logos, icons, and other graphical elements.

# Photography: Prepare images for creative projects by separating subjects from their surroundings.

# Marketing Materials: Generate visually appealing marketing materials by placing subjects on different backgrounds.

# Art and Creativity: Use background removal as a creative tool to merge different elements and experiment with compositions.


import math
import os
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps
from rembg import remove

image_extensions = (".png", ".jpg", ".jpeg", ".webp")


def append_id(filename):
    p = Path(filename)
    return "{0}_{2}{1}".format(Path.joinpath(p.parent, p.stem), ".webp", "Processed")


def autocrop_image(img, border=0):
    bbox = img.getbbox()
    img = img.crop(bbox)
    (scale, height) = img.size
    scale += border * 2
    height += border * 2
    cropped_image = Image.new("RGBA", (scale, height), (0, 0, 0, 0))
    cropped_image.paste(img, (border, border))
    return cropped_image


def resize_image(img, myScale):
    img_width, img_height = img.size

    if img_height > img_width:
        hpercent = myScale / float(img_height)
        wsize = int((float(img_width) * float(hpercent)))
        resized_img = img.resize((wsize, myScale), Image.Resampling.LANCZOS)

    if img_width > img_height:
        wpercent = myScale / float(img_width)
        hsize = int((float(img_height) * float(wpercent)))
        resized_img = img.resize((myScale, hsize), Image.Resampling.LANCZOS)

    return resized_img


def resize_canvas(img, canvas_width, canvas_height):
    old_width, old_height = img.size
    x1 = int(math.floor((canvas_width - old_width) / 2))
    y1 = int(math.floor((canvas_height - old_height) / 2))
    mode = img.mode
    if len(mode) == 1:
        new_background = 255
    if len(mode) == 3:
        new_background = (255, 255, 255)
    if len(mode) == 4:
        new_background = (255, 255, 255, 255)
    newImage = Image.new(mode, (canvas_width, canvas_height), new_background)
    newImage.alpha_composite(
        img, ((canvas_width - old_width) // 2, (canvas_height - old_height) // 2)
    )
    return newImage


def process_images(folder_dir):
    for entry in os.scandir(folder_dir):
        if entry.is_file() and entry.name.lower().endswith(image_extensions):
            image_path = entry.path
            img = Image.open(image_path)
            output_path = append_id(image_path)
            removedBGimage = remove(img)
            croppedImage = autocrop_image(removedBGimage, 0)
            resizedImage = resize_image(croppedImage, 700)
            combinedImage = resize_canvas(resizedImage, 1000, 1000)
            combinedImage.save(output_path, quality=100)
        elif entry.is_dir():
            process_images(entry.path)


if __name__ == "__main__":
    input_directory = r"D:\Backend\Django\programs\Amazon_EC2\media\profile-photo"
    process_images(input_directory)


def apply_product_transformations(img):
    """
    Apply transformations to make product images more attractive:
    - Remove background automatically
    - Replace it with a clean white background
    - Enhance brightness, contrast, and sharpness
    """
    # Remove background
    img_no_bg = remove(img)

    # Convert to RGBA if not already
    if img_no_bg.mode != "RGBA":
        img_no_bg = img_no_bg.convert("RGBA")

        # Resize while maintaining aspect ratio (e.g., target size 800x800)
        target_size = (800, 800)
        img.thumbnail(target_size, Image.LANCZOS)

        # Center crop to ensure consistent size
        width, height = img_no_bg.size
        left = (width - target_size[0]) // 2
        top = (height - target_size[1]) // 2
        right = (width + target_size[0]) // 2
        bottom = (height + target_size[1]) // 2

        img_no_bg = img_no_bg.crop((left, top, right, bottom))

    # Create a new white background
    white_bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255, 255))

    # Composite the image with the white background
    img_with_white_bg = Image.alpha_composite(white_bg, img_no_bg)

    # enhancer = ImageEnhance.Brightness(img_with_white_bg)
    img_with_white_bg = enhancer.enhance(1.1)  # Increase brightness

    # Color enhancement (increase saturation by 20%)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.6)

    enhancer = ImageEnhance.Sharpness(img_with_white_bg)
    img_with_white_bg = enhancer.enhance(2.5)  # Increase sharpness

    # Convert to RGB for saving
    if img_with_white_bg.mode != "RGB":
        img_with_white_bg = img_with_white_bg.convert("RGB")

        # Enhance brightness and contrast
        img_with_white_bg = ImageOps.autocontrast(img_with_white_bg)

    return img_with_white_bg


def process_images(input_directory):
    """
    Process all images in the specified directory.
    """
    for filename in os.listdir(input_directory):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            file_path = os.path.join(input_directory, filename)
            try:
                # Open the image
                img = Image.open(file_path)

                # Apply transformations
                transformed_img = apply_product_transformations(img)

                # Create a new filename
                new_filename = f"{os.path.splitext(filename)[0]}_formatted.webp"
                new_file_path = os.path.join(input_directory, new_filename)

                # Save the transformed image
                transformed_img.save(new_file_path, format="WEBP", quality=100)

                print(f"Processed and saved: {new_file_path}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    input_directory = r"D:\Backend\Django\programs\Amazon_EC2\media\profile-photo"
    process_images(input_directory)

    # try:
    #     # Create a mask for the image
    #     if "A" in img.getbands():  # Check if the image has an alpha channel
    #         mask = img.getchannel("A")  # Get the alpha channel as a mask
    #     else:
    #         # If no alpha channel, create a mask based on brightness
    #         mask = img.convert("L").point(
    #             lambda x: 255 if x > 200 else 0
    #         )  # Simple thresholding

    # except Exception as e:
    #     print(f"Error Createing mask: {e}")
