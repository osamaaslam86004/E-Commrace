from typing import Any

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from book_.models import BookAuthorName, BookFormat, Rating, Review
from i.custom_validators import file_size_validator, image_validator


class BookAuthorNameForm(forms.ModelForm):

    class Meta:
        model = BookAuthorName
        fields = ["author_name", "book_name", "about_author", "language"]
        labels = {
            "author_name": "Author Name",
            "book_name": "Book Name",
            "about_author": "About Author",
            "language": "Language",
        }
        widgets = {
            "author_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter the name of the author",
                }
            ),
            "book_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter the name of the book",
                }
            ),
            "about_author": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter previous work of author",
                }
            ),
            "language": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter the language"}
            ),
        }

    def clean_book_name(self):
        book_name = self.cleaned_data.get("book_name")
        if len(book_name) > 50:
            raise forms.ValidationError("Book name must be 255 characters or fewer.")
        return book_name


class BookFormatForm(forms.ModelForm):
    allowed_extensions = ["png", "jpeg", "jpg", "webp"]

    image_1 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        validators=[image_validator, file_size_validator],
    )
    image_2 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        validators=[image_validator, file_size_validator],
    )
    image_3 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        validators=[image_validator, file_size_validator],
    )

    class Meta:
        model = BookFormat
        fields = [
            "format",
            "is_new_available",
            "is_used_available",
            "publisher_name",
            "publishing_date",
            "edition",
            "length",
            "narrator",
            "price",
            "is_active",
            "restock_threshold",
            "image_1",
            "image_2",
            "image_3",
        ]
        labels = {
            "format": "Format",
            "is_new_available": "Is New Available",
            "is_used_available": "Is Used Available",
            "publisher_name": "Publisher Name",
            "publishing_date": "Publishing Date",
            "edition": "Edition",
            "length": "Length",
            "narrator": "Narrator",
            "price": "Price",
            "is_active": "Is Active",
            "restock_threshold": "Restock Threshold",
            "image_1": "Image 1",
            "image_2": "Image 2",
            "image_3": "Image 3",
        }
        widgets = {
            "book_author_name": forms.Select(attrs={"class": "form-control"}),
            "user": forms.Select(attrs={"class": "form-control"}),
            "product_category": forms.Select(attrs={"class": "form-control"}),
            "format": forms.Select(
                choices=BookFormat.FORMAT_CHOICES, attrs={"class": "form-control"}
            ),
            "is_new_available": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "is_used_available": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "publisher_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter publisher name"}
            ),
            "publishing_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "edition": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter edition"}
            ),
            "length": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "narrator": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter narrator"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 999999.99}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "restock_threshold": forms.NumberInput(
                attrs={"class": "form-control", "min": 9}
            ),
            # "image_2": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
            # "image_3": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        }

    def clean_format(self):
        format = self.cleaned_data.get("format")
        if (
            not format
            or format is None
            or format not in dict(BookFormat.FORMAT_CHOICES)
        ):
            raise forms.ValidationError("Valid format is required.")
        return format

    def clean_is_new_available(self):
        is_new_available = self.cleaned_data.get("is_new_available")
        if (
            is_new_available is None
            or is_new_available < 0
            or is_new_available > 2147483647
        ):
            raise forms.ValidationError("Is new available is in range 0 to 2147483647")
        return is_new_available

    def clean_is_used_available(self):
        is_used_available = self.cleaned_data.get("is_used_available")
        if (
            is_used_available is None
            or is_used_available < 0
            or is_used_available > 2147483647
        ):
            raise forms.ValidationError("Is used available is in range 0 to 2147483647")
        return is_used_available

    def clean_publisher_name(self):
        publisher_name = self.cleaned_data.get("publisher_name")
        if not publisher_name or len(publisher_name) > 100:
            raise forms.ValidationError(
                "Publisher name is required, 0 to 100 characters"
            )
        return publisher_name

    def clean_narrator(self):
        narrator = self.cleaned_data.get("narrator")
        if narrator is None or len(narrator) > 20:
            raise forms.ValidationError("Length of narrator must 0 to 20 characters")
        return narrator

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None or price < 1 or price > 999999.99:
            raise forms.ValidationError("Price must be between 1 and 999999.99.")
        return price

    def clean_restock_threshold(self):
        restock_threshold = self.cleaned_data.get("restock_threshold")
        if (
            not restock_threshold
            or restock_threshold < 9
            or restock_threshold > 2147483647
        ):
            raise forms.ValidationError(("restock_threshold range: 9 to 2147483647"))
        return restock_threshold

    # def clean_image_1(self):
    #     image_1 = self.cleaned_data.get("image_1")

    #     if image_1 is not None:
    #         if (
    #             image_1
    #             and str(image_1.image.format).lower() not in self.allowed_extensions
    #         ):
    #             raise forms.ValidationError(
    #                 f"image 1 in {self.allowed_extensions} formats is required.."
    #             )

    #         if image_1 and image_1.size > 5 * 1024 * 1024:
    #             raise forms.ValidationError(
    #                 "Image_1 is too large. Maximum size is 5MB."
    #             )
    #     return image_1

    # def clean_image_2(self):
    #     image_2 = self.cleaned_data.get("image_2")
    #     if image_2 is not None:
    #         if (
    #             image_2
    #             and str(image_2.image.format).lower() not in self.allowed_extensions
    #         ):
    #             raise forms.ValidationError(
    #                 f"image 2 in {self.allowed_extensions} formats is required.."
    #             )

    #         if image_2 and image_2.size > 5 * 1024 * 1024:
    #             raise forms.ValidationError(
    #                 "Image_2 is too large. Maximum size is 5MB."
    #             )
    #     return image_2

    # def clean_image_3(self):
    #     image_3 = self.cleaned_data.get("image_3")
    #     if image_3 is not None:
    #         if (
    #             image_3
    #             and str(image_3.image.format).lower() not in self.allowed_extensions
    #         ):
    #             raise forms.ValidationError(
    #                 f"image 3 in {self.allowed_extensions} formats is required.."
    #             )

    #         if image_3 and image_3.size > 5 * 1024 * 1024:
    #             raise forms.ValidationError(
    #                 "Image_3 is too large. Maximum size is 5MB."
    #             )
    #     return image_3


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = [
            "rating",
        ]
        labels = {
            "rating": "Rating (1-5)",
        }


class ReviewForm(forms.ModelForm):
    rating = RatingForm()
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Review
        fields = ["image_1", "image_2", "title", "content"]
        exclude = ["book_format"]
        labels = {
            "title": "Title",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter the review title"}
            ),
        }


class CustomBookFormatFilterForm(forms.Form):
    FORMAT_CHOICES = [
        ("", "Any Format"),
        ("AUDIO_CD", "Audio CD"),
        ("SPIRAL_BOUND", "Spiral Bound"),
        ("PAPER_BACK", "Paperback"),
        ("HARDCOVER", "Hardcover"),
    ]

    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    book_name = forms.CharField(
        max_length=100,
        required=False,
        label="Book Name",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    author_name = forms.CharField(
        max_length=50,
        required=False,
        label="Author Name",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    price_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Minimum Price",
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    price_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Maximum Price",
        validators=[MaxValueValidator(999999.99)],
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    is_new_available = forms.BooleanField(
        required=False,
        label="Is New Available",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    is_used_available = forms.BooleanField(
        required=False,
        label="Is Used Available",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    publisher_name = forms.CharField(
        max_length=100,
        required=False,
        label="Publisher Name",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    rating_min = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        required=False,
        label="Minimum Rating",
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    rating_max = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        required=False,
        label="Maximum Rating",
        validators=[MaxValueValidator(5)],
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )


# class BookAuthorNameForm(forms.ModelForm):
#     class Meta:
#         model = BookAuthorName
#         fields = ["author_name", "book_name", "about_author", "language"]
#         labels = {
#             "author_name": "Author Name",
#             "book_name": "Book Name",
#             "about_author": "About Author",
#             "language": "Language",
#         }
#         widgets = {
#             "author_name": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter the name of the author",
#                 }
#             ),
#             "book_name": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter the name of the book",
#                 }
#             ),
#             "about_author": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter previous work of author",
#                 }
#             ),
#             "language": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": "Enter the language"}
#             ),
#         }


# class BookFormatForm(forms.ModelForm):
#     is_active = forms.TypedChoiceField(
#         coerce=lambda x: x == "True",
#         choices=[(True, "Active"), (False, "In Active")],
#         widget=forms.RadioSelect(),
#         required=False,
#         initial=True,
#         label="Choose the status of the book",
#     )

#     class Meta:
#         model = BookFormat
#         fields = [
#             "format",
#             "is_active",
#             "image_1",
#             "image_2",
#             "image_3",
#             "is_new_available",
#             "is_used_available",
#             "publisher_name",
#             "edition",
#             "length",
#             "narrator",
#             "price",
#             "publishing_date",
#         ]

#         labels = {
#             "book_author_name": "Author Name",
#             "format": "Format",
#             "is_new_available": "Is New Available",
#             "is_used_available": "Is Used Available",
#             "publisher_name": "Publisher Name",
#             "edition": "Edition",
#             "length": "Length",
#             "narrator": "Narrator",
#             "price": "Price",
#             "publishing_date": "Publishing Date",
#         }

#         widgets = {
#             "format": forms.Select(attrs={"class": "form-control"}),
#             "is_new_available": forms.NumberInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "enter the number of available new books",
#                 }
#             ),
#             "is_used_available": forms.NumberInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "enter the number of available used books",
#                 }
#             ),
#             "publisher_name": forms.TextInput(attrs={"class": "form-control"}),
#             "edition": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": "Rebound version / 2012"}
#             ),
#             "length": forms.NumberInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "enter the number of pages of a book",
#                 }
#             ),
#             "narrator": forms.TextInput(attrs={"class": "form-control"}),
#             "price": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "step": "0.01",
#                     "placeholder": "Price must be between 1 and 999999.99.",
#                 }
#             ),
#             "publishing_date": forms.DateInput(attrs={"format": "%Y-%m-%d"}),
#         }
