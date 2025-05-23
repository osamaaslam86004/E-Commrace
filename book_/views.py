from cloudinary.uploader import upload
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import CreateView, UpdateView

from book_.custom_mixins.filtered_books_mixin import FilteredBooksMixin
from book_.forms import (
    BookAuthorNameForm,
    BookFormatForm,
    CustomBookFormatFilterForm,
    ReviewForm,
)
from book_.models import BookAuthorName, BookFormat, Rating, Review
from book_.utils import RatingCalculator
from i.browsing_history import add_product_to_browsing_history, your_browsing_history
from i.decorators import (
    check_user_linked_to_comment,
    user_add_product_permission_required,
    user_comment_permission_required,
)
from i.models import ProductCategory


class Create_Book_Formats_View(SuccessMessageMixin, CreateView):
    template_name = "subcategory_form.html"
    form_class = BookFormatForm
    success_url = reverse_lazy("i:success_page")
    success_message = "All forms submitted successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["book_author_name_form"] = BookAuthorNameForm()
        context["book_format_form"] = BookFormatForm()
        context["form"] = None
        return context

    def form_valid(self, form):
        book_author_name_form = BookAuthorNameForm(self.request.POST)
        book_format_form = form

        if book_author_name_form.is_valid() and book_format_form.is_valid():
            book_author = book_author_name_form.save(commit=False)
            book_format = book_format_form.save(commit=False)

            # Check for an existing book format by the user
            requested_format = book_format_form.cleaned_data["format"]
            check_existing_book_format = BookFormat.objects.filter(
                format=requested_format, user=self.request.user
            ).exists()

            if check_existing_book_format:
                messages.error(
                    self.request,
                    f"You have already added a book for {requested_format}",
                )
                return self.form_invalid(form)

            # Save book author and book format
            uploaded_images = {
                "image_1": self.request.FILES.get("image_1"),
                "image_2": self.request.FILES.get("image_2"),
                "image_3": self.request.FILES.get("image_3"),
            }

            if self.all_images_uploaded_by_user(uploaded_images):
                book_author.save()
                transformation_options = {
                    "width": 300,
                    "height": 200,
                    "crop": "fill",
                    "gravity": "face",
                    "effect": "auto_contrast",
                }

                for key, image_file in uploaded_images.items():
                    if image_file:
                        image_data = upload(
                            image_file,
                            transformation=transformation_options,
                            resource_type="image",
                        )

                        resized_image_url = image_data["url"]
                        setattr(book_format, f"image_{key[-1]}", resized_image_url)
                    else:
                        messages.info(
                            self.request,
                            "Images did not upload properly, try again!",
                        )
                        return self.form_invalid(form)

                try:
                    # Set relationships and other attributes for book_format
                    book_format.user = self.request.user
                    book_category = ProductCategory.objects.get(name="BOOKS")
                    book_format.product_category = book_category
                    book_format.book_author_name = book_author
                    book_format.save()
                except Exception as e:
                    book_author.delete()
                    print(f"Error: {e}")
                    messages.error(self.request, "Failed to save book format.")
                    return self.form_invalid(form)
            else:
                messages.error(self.request, "Please upload all three images")
                return self.form_invalid(form)
        else:
            # Print form errors
            print("Author form errors:", book_author_name_form.errors)
            print("Format form errors:", book_format_form.errors)
            messages.error(self.request, "Form not valid")
            return self.form_invalid(form)

        return super().form_valid(form)

    def all_images_uploaded_by_user(self, uploaded_images):
        return all(uploaded_images.values())


@method_decorator(login_required, name="dispatch")
class Update_Book_Formats_View(
    UpdateView, SuccessMessageMixin, PermissionRequiredMixin
):
    model = BookFormat
    form_class = BookFormatForm
    template_name = "create_update_book_formats.html"
    success_url = reverse_lazy("Homepage:Home")
    success_message = "Book details updated successfully"

    def handle_no_permission(self, request):
        user_email = self.request.user.email
        user_permission = "delete comment"
        return render(
            self.request,
            "permission_denied.html",
            {"user_email": user_email, "user_permission": user_permission},
        )

    def custom_check_has_permission(self, request):
        user_type = self.request.user

        if user_type == "SELLER" and request.user.has_perm(
            "Homepage.seller_update_product"
        ):
            return True

        elif user_type == "ADMINISTRATOR" and request.user.has_perm(
            "Homepage.admin_update_product"
        ):
            return True

        elif user_type == "MANAGER" and request.user.has_perm(
            "Homepage.manager_update_product"
        ):
            return True
        else:
            return False

    def check_requested_and_object_user_are_same(self, request, **kwargs):
        user_who_requested = self.request.user

        get_user_of_book_format = BookFormat.objects.get(id=self.kwargs["pk"]).user
        get_user_who_requested = BookFormat.objects.get(
            id=self.kwargs["pk"]
        ).user_who_requested

        if get_user_who_requested == get_user_of_book_format:
            return True
        else:
            False

    def all_images_uploaded(self, uploaded_images):
        if any(uploaded_images.values()):
            return True
        else:
            False

    def form_valid(self, form):
        user_who_requested = self.object.user
        book_format_form = form

        if self.custom_check_has_permission(self.request):
            if self.check_requested_and_object_user_are_same(
                self.request, self.kwargs["pk"]
            ):
                book_format = self.get_object()
                if book_format:
                    book_author_name = book_format.book_author_name

                    book_author_name_form = BookAuthorNameForm(
                        self.request.POST, instance=book_author_name
                    )

                    if book_format_form.is_valid() and book_author_name_form.is_valid():
                        book_form = book_format_form(commit=False)
                        author_form = book_author_name_form(commmit=False)

                        requested_format = book_format_form.cleaned_data["format"]

                        check_existing_book_format = book_format.format
                        if check_existing_book_format:
                            messages.erro(
                                self.request,
                                f"You have already added a book for {requested_format}",
                            )
                        else:
                            uploaded_images = {
                                "image_1": self.request.FILES["image_1"],
                                "image_2": self.request.FILES["image_2"],
                                "image_3": self.request.FILES["image_3"],
                            }

                            if self.all_images_uploaded(uploaded_images):
                                author_form.save()
                                transformation_options = {
                                    "width": 300,
                                    "height": 200,
                                    "crop": "fill",
                                    "gravity": "face",
                                    "effect": "auto_contrast",
                                }

                                resized_image_urls = {}
                                for key, image_file in uploaded_images.items():
                                    if image_file:
                                        image_data = upload(
                                            image_file,
                                            transformation=transformation_options,
                                            resource_type="image",
                                        )

                                        resized_image_urls = image_data["secure_url"]
                                        setattr(
                                            book_format,
                                            f"image_{key[-1]}",
                                            resized_image_urls,
                                        )
                                    else:
                                        messages.info(
                                            self.request,
                                            "images did not uploaded properly, Try again!",
                                        )
                                        return super().form_invalid(form)

                            book_format.book_author_name = author_form
                            get_product_category = ProductCategory.objects.get(
                                name="BOOKS"
                            )
                            book_format.product_category = get_product_category
                            book_format.user = self.object.user
                            book_format.save()
                    else:
                        messages.error(self.request, "Form is not valid")
                        return super().form_invalid(form)
                else:
                    messages.error(self.request, "This book does not exist")
                    return redirect("book_:book_list_filter")
            else:
                self.handle_no_permission(self.request)
        else:
            self.handle_no_permission(self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        book_format = self.get_object()
        book_author_name = book_format.book_author_name

        book_author_name_form = BookAuthorNameForm(instance=book_author_name)
        book_format_form = BookFormatForm(instance=book_format)

        context["book_author_name_form"] = book_author_name_form
        context["book_format_form"] = book_format_form
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(user_add_product_permission_required, name="dispatch")
class Delete_Book_Format_View(View, PermissionRequiredMixin):
    template_name = "list_of_products_for_update.html"
    model = BookFormat

    def get(self, request, **kwargs):
        book_object = BookFormat.objects.get(id=kwargs["pk"])
        BookFormat.objects.get(id=kwargs["pk"]).delete()
        messages.success(self.request, f"Your Book with {book_object} is deleted")
        return redirect("i:list_of_books_for_user")


class FilteredBooksView(TemplateResponseMixin, View, FilteredBooksMixin):
    """
    Check the MRO
    print(FilteredBooksView.mro())
    """

    template_name = "book_list_view.html"
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        form = CustomBookFormatFilterForm()
        queryset = self.get_queryset()
        page_obj = self.paginate_queryset(queryset, self.request.GET.get("page"))
        print(f"page number: {self.request.GET.get('page')}")
        context = self.get_context_data(page_obj, form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = CustomBookFormatFilterForm(self.request.POST)
        queryset = self.get_queryset(form)
        page_obj = self.paginate_queryset(queryset, self.request.POST.get("page", 1))
        context = self.get_context_data(page_obj, form)
        return self.render_to_response(context)

    def paginate_queryset(self, queryset, page_number):
        paginator = Paginator(queryset, self.paginate_by)
        return paginator.get_page(page_number)

    def get_context_data(self, page_obj, form):
        content_id = ContentType.objects.get(app_label="book_", model="bookformat").id
        return {
            "content_id": content_id,
            "item_list": page_obj,
            "form": form,
            "request": self.request,
        }


class Book_Detail_View(DetailView):
    template_name = "book_detail_view.html"
    model = BookAuthorName

    def calculate_star_rating(self, format_id):
        book_format = get_object_or_404(BookFormat, id=format_id)
        average_rating = RatingCalculator.calculate_average_rating(book_format)
        total_ratings = RatingCalculator.count_users_who_rated(book_format)

        star_ratings = {}

        for rating in [5, 4, 3, 2, 1]:
            star_ratings[rating] = RatingCalculator.count_star_ratings(
                book_format, rating
            )

            #  Calculate the with for star rating
            width_percentages = {}

            for rating in [5, 4, 3, 2, 1]:
                count = star_ratings.get(rating, 0)
                width_percentages[rating] = (
                    count / total_ratings * 100 if total_ratings > 0 else 0
                )

        return total_ratings, average_rating, star_ratings, width_percentages

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # self.get_object(), Django internally uses the URL parameters (such as pk or slug) to query
        # the database for an instance of that model.
        # If the object is not found or if there is an error in the URL parameters,
        # get_object_or_404() is typically used to raise a 404 error,
        # manually specify pk in URL in views.py and {% url 'Homepage:Home' pk=book.id %}
        book = self.get_object()

        format_id = self.kwargs.get("format_id")
        book_format = get_object_or_404(BookFormat, id=format_id, book_author_name=book)
        # formats = BookFormat.objects.filter(book_author_name=book)

        reviews = Review.objects.filter(book_format=book_format)
        ratings = Rating.objects.filter(book_format=book_format)
        review_rating_dict = {}

        for review in reviews:
            matching_ratings = ratings.filter(user=review.user)
            if matching_ratings.exists():
                rating = matching_ratings.first()
                review_rating_dict[review] = (
                    rating  # review_rating_dict is a dictionary of review objects
                )
                #    and corresponding rating objects

        # formats = formats.annotate(avg_rating=Avg('rating_format__rating'),
        #                           user_count=Count('rating_format__user'))

        [
            total_ratings,
            average_rating,
            star_ratings,
            width_percentages,
        ] = self.calculate_star_rating(format_id)

        # add product image URL to session cookie
        scheme = "https://" if self.request.is_secure() else "http://"
        path = scheme + str(self.request.get_host()) + str(self.request.get_full_path())
        product_details = {
            "name": book_format.book_author_name.book_name,
            "price": str(book_format.price),
            "rating": str(average_rating),
            "image_url": str(book_format.image_1),
            "path": path,
            "special_features": [1],
        }
        add_product_to_browsing_history(self.request, product_details)
        zipped = your_browsing_history(self.request)

        context["book_author_name"] = book
        context["book_format"] = book_format
        context["review_rating_dict"] = review_rating_dict
        context["total_ratings"] = total_ratings
        context["average_rating"] = average_rating
        context["star_ratings"] = star_ratings
        context["width_percentages"] = width_percentages
        context["zipped"] = zipped
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(user_comment_permission_required, name="dispatch")
class Book_Detail_View_Add_Review_Form(View):
    def all_images_uploaded_by_user(self, uploaded_images):
        if all(uploaded_images.values()):
            return True
        else:
            False

    def post(self, request, **kwargs):
        book_author_name_id = kwargs["book_author_name_id"]
        format_id = kwargs["format_id"]

        try:
            book = get_object_or_404(BookAuthorName, id=book_author_name_id)
            book_format = get_object_or_404(
                BookFormat, id=format_id, book_author_name=book
            )

            reviews = Review.objects.filter(book_format=book_format)

            existing_review = reviews.filter(user=self.request.user).exists()
            if existing_review:
                messages.error(
                    request,
                    "You have already submitted a review for this book format.",
                )
                return redirect(
                    "book_:book_detail_view",
                    pk=book_author_name_id,
                    format_id=format_id,
                )
            else:
                review_form = ReviewForm(request.POST)
                star_rating = self.request.POST.get("rating")

                if review_form.is_valid() and star_rating is not None:
                    new_review = review_form.save(commit=False)

                    uploaded_images = {
                        "image_1": self.request.FILES["image_1"],
                        "image_2": self.request.FILES["image_2"],
                    }

                    if self.all_images_uploaded_by_user(uploaded_images):
                        transformation_options = {
                            "width": 75,
                            "height": 75,
                            "crop": "fill",
                            "gravity": "face",
                            "effect": "auto_contrast",
                        }

                        for key, image_file in uploaded_images.items():
                            if image_file:
                                image_data = upload(
                                    image_file,
                                    transformation=transformation_options,
                                    resource_type="image",
                                )
                                resized_image_url = image_data["url"]
                                setattr(
                                    new_review, f"image_{key[-1]}", resized_image_url
                                )
                            else:
                                messages.info(
                                    self.request,
                                    "images did not uploaded properly, Try again!",
                                )
                                return redirect("i:monitor_add_review")

                            new_review.user = request.user
                            new_review.book_format = book_format
                            new_review.rating = star_rating
                            new_review.save()

                            Star_Rating, created = Rating.objects.get_or_create(
                                user=self.request.user,
                                book_format=book_format,
                                rating=star_rating,
                            )
                            if created:
                                print(f"rating created")
                            else:
                                print(f"rating has already been created")

                            messages.success(request, "Review submitted successfully.")
                            return redirect(
                                "book_:book_detail_view",
                                pk=book_author_name_id,
                                format_id=format_id,
                            )
                    else:
                        messages.error(request, "Please, upload all images")
                        return redirect(
                            "book_:book_detail_view_add_review_form",
                            book_author_name_id=book_author_name_id,
                            format_id=format_id,
                        )
                else:
                    messages.error(request, "Form is not valid / Enter Star Rating.")
                    return redirect(
                        "book_:book_detail_view_add_review_form",
                        book_author_name_id=book_author_name_id,
                        format_id=format_id,
                    )
        except book.DoesNotExist and book_format.DoesNotExist:
            return redirect("book_:book_list_filters")

    def get(self, request, **kwargs):
        book_author_name_id = kwargs["book_author_name_id"]
        format_id = kwargs["format_id"]

        format = BookFormat.objects.get(id=format_id).format

        context = {
            "review_form": ReviewForm(),
            "format": format,
        }
        return render(request, "book_add_review.html", context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_comment_permission_required, name="dispatch")
@method_decorator(check_user_linked_to_comment, name="dispatch")
class Book_Detail_View_Update_Review_Form(View):
    def all_images_uploaded_by_user(self, uploaded_images):
        if all(uploaded_images.values()):
            return True
        else:
            False

    def post(self, request, **kwargs):
        review_id = kwargs["review_id"]

        review_instance = Review.objects.get(id=review_id)

        review_form = ReviewForm(self.request.POST, instance=review_instance)
        star_rating = self.request.POST.get("rating")

        if review_form.is_valid() and star_rating is not None:
            new_review = review_form.save(commit=False)

            uploaded_images = {
                "image_1": self.request.FILES["image_1"],
                "image_2": self.request.FILES["image_2"],
            }

            if self.all_images_uploaded_by_user(uploaded_images):
                transformation_options = {
                    "width": 75,
                    "height": 75,
                    "crop": "fill",
                    "gravity": "face",
                    "effect": "auto_contrast",
                }

                for key, image_file in uploaded_images.items():
                    if image_file:
                        image_data = upload(
                            image_file,
                            transformation=transformation_options,
                            resource_type="image",
                        )
                        resized_image_url = image_data["url"]
                        setattr(new_review, f"image_{key[-1]}", resized_image_url)
                    else:
                        messages.info(
                            self.request,
                            "images did not uploaded properly, Try again!",
                        )
                        return redirect("i:monitor_add_review")

                new_review.user = self.request.user
                new_review.book_format = review_instance.book_format
                new_review.rating = star_rating
                new_review.save()

                messages.success(request, "Review submitted successfully.")
                return redirect(
                    "book_:book_detail_view",
                    pk=review_instance.book_format.id,
                    format_id=review_instance.book_format.id,
                )
            else:
                messages.error(request, "Please, upload all images")
                return redirect(
                    "book_:book_detail_view_update_review_form",
                    review_id=review_id,
                )
        else:
            messages.error(request, "Form is not valid / Enter Star Rating.")
            return redirect(
                "book_:book_detail_view_update_review_form", review_id=review_id
            )

    def get(self, request, review_id):
        review = Review.objects.get(id=review_id)
        review_form = ReviewForm(instance=review)

        context = {
            "review_form": review_form,
        }
        return render(request, "edit_review_rating.html", context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_comment_permission_required, name="dispatch")
@method_decorator(check_user_linked_to_comment, name="dispatch")
class Custom_Delete_Comment(View, PermissionRequiredMixin):
    def get(self, request, review_id):
        review_to_delete = Review.objects.get(id=review_id)
        book_format_id = review_to_delete.book_format.id
        book_author_name_id = review_to_delete.book_format.book_author_name.id

        review_to_delete.delete()
        messages.success(self.request, "Message deleted successfully!")

        return redirect(
            "book_:book_detail_view",
            pk=book_author_name_id,
            format_id=book_format_id,
        )
