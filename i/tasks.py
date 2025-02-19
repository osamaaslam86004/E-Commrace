import logging
from io import BytesIO

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.db import transaction
from PIL import Image, ImageEnhance, ImageOps

from i.models import Monitors
from iii.custom_storage_backend import (
    PublicMediaStorage,  # Import your custom storage backend
)

logger = logging.getLogger(__name__)


# Refrences:
# 1. https://docs.celeryq.dev/en/stable/userguide/tasks.html
# 2. https://docs.celeryq.dev/en/stable/_modules/celery/exceptions.html#MaxRetriesExceededError


import time

from django.db import DatabaseError, transaction


def store_images_path(monitor_id, uploaded_urls, max_retries=3, delay=2):

    try:
        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Lock the specific monitor instance
            monitor = Monitors.objects.select_for_update().get(id=monitor_id)

            for key, image_url in uploaded_urls.items():
                # Update the specific image field
                setattr(monitor, f"image_{key[-1]}", image_url)

            # Save the changes to the database
            monitor.save()

    except DatabaseError as e:
        # Log the error (optional)
        logger.error(f"Attempt failed: {str(e)}")
        raise  # Re-raise the exception to stop execution

    except Exception as e:
        # Handle other exceptions if necessary
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise  # Re-raise the exception to stop execution


@shared_task(
    name="i.upload_images_to_s3",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    time_limit=300,
    soft_time_limit=250,
)
def upload_images_to_s3(self, image_files, monitor_id):
    uploaded_urls = {}
    storage = PublicMediaStorage()  # Create an instance of your custom storage

    for key, image_file in image_files:
        if image_file:  # Check if the file is not None
            try:
                # Open the image using Pillow
                img = Image.open(image_file)

                # Convert to RGB if not already in that mode
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Apply transformations
                img = apply_product_transformations(img)

                # Save the transformed image to a BytesIO object
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format="WEBP", quality=100)
                img_byte_arr.seek(0)  # Move to the beginning of the BytesIO buffer

                # Save the file to S3 using your custom storage
                file_name = storage.save(image_file.name, img_byte_arr)
                file_url = storage.url(file_name)  # Get the URL of the uploaded file
                uploaded_urls[f"{key}"] = file_url

                logger.info(
                    f"Image {image_file.name} uploaded successfully: {file_url}"
                )

                try:
                    store_images_path(monitor_id, uploaded_urls)
                except Exception as e:
                    logger.info(f"{e}")

            except Exception as e:
                # log Task id with error
                logger.error(
                    f"f{self.request.id}: Error {str(e)} while processing {image_file.name}"
                )

                # Retry logic
                if self.request.retries < self.max_retries:
                    logger.info(f"Retrying... attempt {self.request.retries + 1}")
                    raise self.retry(exc=e)
                else:
                    logger.error("Max retries exceeded for uploading images.")
                    raise MaxRetriesExceededError(
                        "Max retries exceeded for uploading images."
                    )

    return uploaded_urls


def apply_product_transformations(img):
    """
    Apply transformations to make product images more attractive:
    - Resize and crop to maintain aspect ratio.
    - Auto contrast and brightness adjustment.
    - Color enhancement.
    - Sharpening.
    """

    # Resize while maintaining aspect ratio (e.g., target size 800x800)
    target_size = (800, 800)
    img.thumbnail(target_size, Image.ANTIALIAS)

    # Center crop to ensure consistent size
    width, height = img.size
    left = (width - target_size[0]) // 2
    top = (height - target_size[1]) // 2
    right = (width + target_size[0]) // 2
    bottom = (height + target_size[1]) // 2

    img = img.crop((left, top, right, bottom))

    # Auto contrast enhancement
    img = ImageOps.autocontrast(img)

    # Adjust brightness (increase by 10%)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.1)

    # Color enhancement (increase saturation by 20%)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.2)

    # Sharpening the image for better detail visibility
    sharpness_enhancer = ImageEnhance.Sharpness(img)
    img = sharpness_enhancer.enhance(1.5)

    return img


# Recommended Transformations
# Resize and Crop: Ensure that all product images are of a consistent size while maintaining aspect ratio. You can center-crop the images to focus on the product.

# Auto Contrast and Brightness Adjustment: Automatically adjust contrast and brightness to make the images pop.

# Color Enhancement: Enhance colors to make them more vibrant, which can help in attracting customer attention.

# Background Removal or Blurring: If applicable, remove or blur backgrounds to emphasize the product itself.

# Sharpening: Apply sharpening filters to enhance details in the product images.

# Add Shadows or Highlights: Subtle shadows or highlights can add depth to product images, making them appear more three-dimensional.

# @shared_task(
#     bind=True, max_retries=3, default_retry_delay=2
# )  # Retry up to 3 times with a 60-second delay
# def upload_images_to_s3(self, image_files):

#     uploaded_urls = []
#     storage = PublicMediaStorage()  # Create an instance of your custom storage

#     try:

#         for image_file in image_files:
#             if image_file:  # Check if the file is not None
#                 # Save the file to S3 using your custom storage
#                 file_name = storage.save(image_file.name, image_file)
#                 file_url = storage.url(file_name)  # Get the URL of the uploaded file
#                 uploaded_urls.append(file_url)

#                 logger.info(f"image {image_file.name} uploaded, with: {file_url}")

#     except Exception as e:
#         logger.error(f"Error {str(e)} while sending {image_file.name}")

#         # Check if we've exceeded maximum retries
#         if self.request.retries < self.max_retries:
#             logger.info(f"Retrying... attempt {self.request.retries + 1}")
#             raise self.retry(exc=e)  # Retry the task
#         else:
#             raise MaxRetriesExceededError(
#                 "Max retries exceeded for email sending task."
#             )

#     return uploaded_urls
