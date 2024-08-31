from django.db import models
from Homepage.models import CustomUser
from i.models import ProductCategory
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField


class BookAuthorName(models.Model):
    book_name = models.CharField(
        max_length=255,
        blank=False,
    )
    author_name = models.CharField(
        max_length=50,
        blank=False,
    )
    about_author = models.TextField(max_length=500, blank=False, default="default")
    language = models.CharField(max_length=15, blank=False, default="English")

    def __str__(self):
        return f"{self.author_name} - {self.book_name}"


class BookFormat(models.Model):
    FORMAT_CHOICES = [
        ("AUDIO_CD", "Audio CD"),
        ("SPIRAL_BOUND", "spiral bound"),
        ("PAPER_BACK", "paper back"),
        ("HARDCOVER", "Hardcover"),
    ]

    book_author_name = models.ForeignKey(
        BookAuthorName, on_delete=models.CASCADE, related_name="format_name"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="book_format_user",
    )
    product_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="book_product_category",
    )
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    is_new_available = models.PositiveIntegerField(blank=False)
    is_used_available = models.PositiveIntegerField(blank=False)
    publisher_name = models.CharField(max_length=100, blank=False, null=True)
    publishing_date = models.DateField(blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True)
    length = models.PositiveIntegerField(blank=False, null=True)
    narrator = models.CharField(max_length=20, blank=True, null=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )
    is_active = models.BooleanField(default=True, null=True)
    restock_threshold = models.PositiveIntegerField(default=9)
    image_1 = models.ImageField(
        upload_to="images/",
        null=True,
        default="https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico",
    )
    image_2 = models.ImageField(
        upload_to="images/",
        null=True,
        default="https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico",
    )
    image_3 = models.ImageField(
        upload_to="images/",
        null=True,
        default="https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico",
    )

    def custom_string_representation_of_object(self):
        return f"Name: {self.book_author_name.book_name} - {self.format} - ${self.price} - Author: {self.book_author_name.author_name}"

    def __str__(self):
        return self.custom_string_representation_of_object()


class Review(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="book_user_review"
    )
    book_format = models.ForeignKey(
        BookFormat, on_delete=models.CASCADE, related_name="book_review_format"
    )
    title = models.CharField(max_length=100, blank=True)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True, null=True)
    status = models.BooleanField(default=True, null=True)
    image_1 = models.ImageField(
        upload_to="images/",
        null=True,
        default="https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico",
    )

    image_2 = models.ImageField(
        upload_to="images/",
        null=True,
        default="https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico",
    )

    def __str__(self):
        return f"Review by {self.user} for {self.book_format.book_author_name.author_name} - {self.book_format.book_author_name.book_name}"


class Rating(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="book_user_rating"
    )
    book_format = models.ForeignKey(
        BookFormat,
        on_delete=models.CASCADE,
        verbose_name="book_format_rating",
        related_name="rating_format",
    )
    rating = models.DecimalField(
        blank=False,
        decimal_places=1,
        max_digits=2,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating by {self.user} for {self.book_format.book_author_name.author_name}- {self.book_format.book_author_name.book_name}"
