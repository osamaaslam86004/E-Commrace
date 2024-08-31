# from typing import Any
# from django.db.models.query import QuerySet
from i.models import Review
from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from i.forms import (
    ProductCategoryForm,
    ComputerSubCategoryForm,
    ElectronicsForm,
    ComputerAndTabletsForm,
    ServersForm,
    MonitorsForm,
    LaptopAccessoriesForm,
    LineConditionersForm,
    IsolatedTransformersForm,
    PDUsForm,
    AdaptorsForm,
    PowerAccessoriesForm,
    LaptopsForm,
    DesktopForm,
    TabletsForm,
    ChargersAndadaptorsForm,
    LaptopBattryForm,
    LaptopBagsForm,
    ScreenFiltersForm,
    ScreenProtectorForm,
    TabletsReplacementPartsForm,
    FlexCablesForm,
    LcdDisplayReplacementPartsForm,
    BagPacksForm,
    HardShellCasesForm,
    MessengerAndShoulderBagForm,
    BriefCasesForm,
    LaptopBagSleevesForm,
    ReviewForm,
    Special_Features,
    SpecialFeaturesForm,
)
from i.models import ProductCategory, ComputerSubCategory, Monitors
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from i.decorators import (
    user_add_product_permission_required,
    user_comment_permission_required,
)
from i.utils import RatingCalculator, Calculate_Ratings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from i.filters import MonitorsFilter
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.db.models import Avg, Count
from book_.models import BookFormat
from cloudinary.uploader import upload
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from book_.forms import CustomBookFormatFilterForm
from django.db.models import Q
from i.browsing_history import add_product_to_browsing_history, your_browsing_history
from django.contrib.contenttypes.models import ContentType


def success_page(request):
    return render(request, "success_page.html")


@login_required(login_url="/login/")
@user_add_product_permission_required
def select_product_category(request):
    product_category_form = ProductCategoryForm()
    return render(
        request,
        "product_category.html",
        {"product_category_form": product_category_form},
    )


def load_subcategory_form(request):
    if request.method == "POST":
        selected_category = request.POST.get("name")

        if selected_category == "COMPUTER":
            subcategory_form = ComputerSubCategoryForm()
        elif selected_category == "ELECTRONICS":
            subcategory_form = ElectronicsForm()
        elif selected_category == "BOOKS":
            return redirect("book_:create_update_book_formats")
        else:
            return HttpResponseBadRequest("Invalid category selected.")
    return render(request, "subcategory_form.html", {"form": subcategory_form})


def load_subsubcategory_form(request):
    if request.method == "POST":
        selected_subcategory = request.POST.get("name")
        subsubcategory_form = None

        if selected_subcategory == "COMPUTERS_AND_TABLETS":
            subsubcategory_form = ComputerAndTabletsForm()
        elif selected_subcategory == "LAPTOP_ACCESSORIES":
            subsubcategory_form = LaptopAccessoriesForm()
        elif selected_subcategory == "TABLETS_REPLACEMENT_PARTS":
            subsubcategory_form = TabletsReplacementPartsForm()
        elif selected_subcategory == "MONITORS":
            return redirect("i:add_monitor")
        elif selected_subcategory == "SERVERS":
            return redirect("i:add_server")
        elif selected_subcategory == "POWER_ACCESSORIES":
            subsubcategory_form = PowerAccessoriesForm()

        return render(
            request,
            "subsubcategory_form.html",
            {"subsubcategory_form": subsubcategory_form},
        )


def load_sub_subsubcategory_form(request):
    if request.method == "POST":
        selected_subcategory = request.POST.get("name")
        form_1 = None

        if selected_subcategory == "LAPTOPS":
            form_1 = LaptopsForm()
        elif selected_subcategory == "DESKTOPS":
            form_1 = DesktopForm()
        elif selected_subcategory == "TABLETS":
            form_1 = TabletsForm()
        elif selected_subcategory == "SCREEN_FILTERS":
            form_1 = ScreenFiltersForm()
        elif selected_subcategory == "BAGS":
            form_1 = LaptopBagsForm()
        elif selected_subcategory == "SCREEN_PROTECTORS":
            form_1 = ScreenProtectorForm()
        elif selected_subcategory == "BATTRIES":
            form_1 = LaptopBattryForm()
        elif selected_subcategory == "CHARGERS_AND_ADAPTORS":
            form_1 = ChargersAndadaptorsForm()
        elif selected_subcategory == "LCD_DISPLAYS":
            form_1 = LcdDisplayReplacementPartsForm()
        elif selected_subcategory == "FLEX_CABLES":
            form_1 = FlexCablesForm()
        elif selected_subcategory == "ADAPTORS":
            form_1 = AdaptorsForm()
        elif selected_subcategory == "ISOLATED TRANSFORMERS":
            form_1 = IsolatedTransformersForm()
        elif selected_subcategory == "LINE CONDITIONERS":
            form_1 = LineConditionersForm()
        elif selected_subcategory == "PDUS":
            form_1 = PDUsForm()

        return render(request, "sub_subsubcategory_form.html", {"form_1": form_1})


def load_sub_sub_subsubcategory_form(request):
    if request.method == "POST":
        selected_category = request.POST.get("name")
        subcategory_form = None

        if selected_category == "BRIEFCASE":
            sub_sub_subcategory_form = BriefCasesForm()
        elif selected_category == "HARDSHELL":
            sub_sub_subcategory_form = HardShellCasesForm()
        elif selected_category == "SLEEVES_BAGS":
            sub_sub_subcategory_form = LaptopBagSleevesForm()
        elif selected_category == "MESSENGER_AND_SHOULDER_BAGS":
            sub_sub_subcategory_form = MessengerAndShoulderBagForm()
        elif selected_category == "BAGPACKS":
            sub_sub_subcategory_form = BagPacksForm()
        else:
            subcategory_form = None

        return render(
            request,
            "sub_sub_subsubcategory_form.html",
            {"sub_sub_form": sub_sub_subcategory_form},
        )


class List_Of_Products_Category(TemplateView):
    template_name = "update_product.html"

    def get_context_data(self):
        context = super().get_context_data()
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(user_add_product_permission_required, name="dispatch")
class List_Of_Books_For_User(ListView):
    model = BookFormat
    template_name = "list_of_book_products_for_update.html"
    context_object_name = "book_formats"

    def get_queryset(self):
        user = self.request.user
        try:
            book_formats = (
                BookFormat.objects.filter(user=user)
                .annotate(avg_rating=Avg("rating_format__rating"))
                .annotate(num_users_rated=Count("rating_format__user"))
            )
        except BookFormat.DoesNotExist:
            messages.error(self.request, "You have not added a BOOK-type product")
            book_formats = BookFormat.objects.none()

        return book_formats

    def get_context_data(self):
        context = super().get_context_data()

        filter_form = CustomBookFormatFilterForm()
        context["filter_form"] = filter_form
        context["book_formats"] = self.get_queryset()
        return context

    def post(self, request):
        item_list = BookFormat.objects.filter(user=self.request.user)

        if self.request.method == "POST":
            requested_user = self.request.user
            form = CustomBookFormatFilterForm(self.request.POST)
            if form.is_valid():
                filter_conditions = Q()

                is_used_available = form.cleaned_data.get("is_used_available")

                if is_used_available == "on":
                    is_used_available = True
                else:
                    is_used_available = False

                is_new_available = form.cleaned_data.get("is_new_available")
                if is_new_available == "on":
                    is_new_available = True
                else:
                    is_new_available = False

                format = form.cleaned_data.get("format")
                if format:
                    filter_conditions |= Q(format=format)

                book_name = form.cleaned_data.get("book_name")

                if book_name:
                    filter_conditions &= Q(
                        book_author_name__book_name__icontains=book_name
                    )

                author_name = form.cleaned_data.get("author_name")
                if author_name:
                    filter_conditions &= Q(
                        book_author_name__author_name__icontains=author_name
                    )

                price_min = form.cleaned_data.get("price_min")
                if price_min:
                    filter_conditions |= Q(price__gte=price_min)

                price_max = form.cleaned_data.get("price_max")
                if price_max:
                    filter_conditions &= Q(price__lte=price_max)

                if is_new_available:
                    filter_conditions |= Q(is_new_available=is_new_available)

                if is_used_available:
                    filter_conditions |= Q(is_used_available=is_used_available)

                publisher_name = form.cleaned_data.get("publisher_name")

                if publisher_name:
                    filter_conditions |= Q(publisher_name__icontains=publisher_name)

                rating_min = form.cleaned_data.get("rating_min")
                if rating_min:
                    filter_conditions |= Q(rating_format__rating__gte=rating_min)

                rating_max = form.cleaned_data.get("rating_max")
                if rating_max:
                    filter_conditions &= Q(rating_format__rating__lte=rating_max)

                queryset = (
                    BookFormat.objects.filter(filter_conditions, user=self.request.user)
                    .annotate(avg_rating=Avg("rating_format__rating"))
                    .annotate(num_users_rated=Count("rating_format__user"))
                )

                context = {"item_list": queryset}
        return render(self.request, "partial_book_seller.html", context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_add_product_permission_required, name="dispatch")
class List_Of_Monitors_For_User(ListView):
    model = Monitors
    template_name = "list_of_products_for_update.html"
    context_object_name = "monitors"

    def get_queryset(self):
        user = self.request.user
        try:
            monitors = (
                Monitors.objects.filter(user=user)
                .annotate(avg_rating=Avg("product_review__rating"))
                .annotate(num_users_rated=Count("product_review__user"))
            )
        except Monitors.DoesNotExist:
            messages.error(self.request, "You have not added a Monitor-type product")
            monitors = Monitors.objects.none()

        return monitors

    def get_context_data(self):
        context = super().get_context_data()

        filter_form = MonitorsFilter()
        context["filter_form"] = filter_form.form
        context["monitors"] = self.get_queryset()
        return context

    def post(self, request):
        item_list = Monitors.objects.filter(user=self.request.user)

        if self.request.method == "POST":
            filter_form = MonitorsFilter(self.request.POST, queryset=item_list)

            # if self.request.POST is None, meaning seller clicks on filter button without selecting any field
            # then due to presence of queryset, all monitors of self.request.user will be displayed
            if filter_form.is_valid():
                item_list = filter_form.qs
                item_ratings, rating_count = Calculate_Ratings.calculate_ratings(
                    item_list
                )

            context = {
                "form": filter_form,
                "item_list": item_list,
                "item_ratings": item_ratings,
                "rating_count": rating_count,
            }

        return render(self.request, "partial_monitor_seller.html", context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_add_product_permission_required, name="dispatch")
class Create_Monitors_Product(SuccessMessageMixin, CreateView):
    template_name = "subsubcategory_form.html"
    form_class = MonitorsForm
    success_url = reverse_lazy("i:success_page")
    success_message = "All forms submitted successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["subsubcategory_form"] = None
        context["monitor_form"] = MonitorsForm()
        # context["special_features_form"] = SpecialFeaturesForm()
        return context

    def all_images_uploaded_by_user(self, uploaded_images):
        if all(uploaded_images.values()):
            return True
        else:
            False

    def form_valid(self, form):
        if form.is_valid():
            monitor = form.save(commit=False)
            uploaded_images = {
                "image_1": self.request.FILES["image_1"],
                "image_2": self.request.FILES["image_2"],
                "image_3": self.request.FILES["image_3"],
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
                        setattr(monitor, f"image_{key[-1]}", resized_image_url)
                    else:
                        messages.info(
                            self.request, "images did not uploaded properly, Try again!"
                        )
                        return self.form_invalid(form)

                product_category_name = "COMPUTER"
                sub_category_name = "MONITORS"
                product_category = ProductCategory.objects.get(
                    name=product_category_name
                )
                sub_category = ComputerSubCategory.objects.get(name=sub_category_name)

                monitor.Product_Category = product_category
                monitor.Computer_SubCategory = sub_category
                monitor.user = self.request.user

                monitor.save()
                # Set self.object to the newly created monitor object
                self.object = monitor

                selected_features_ids = self.request.POST.getlist(
                    "choose_special_features"
                )

                print(f"selected features ids------------: {selected_features_ids}")

                # Fetch the Special_Features objects corresponding to the selected IDs
                selected_features = Special_Features.objects.filter(
                    id__in=selected_features_ids
                )

                # Assuming 'monitor' is your Monitors object
                for feature in selected_features:
                    print(f"Adding feature------------: {feature}")
                    monitor.special_features.add(feature)

                # To confirm the features have been added correctly
                print(
                    f"features added to monitor---------:{monitor.special_features.all().values_list('name', flat=True)}"
                )

                return HttpResponseRedirect(self.get_success_url())
            else:
                messages.error(self.request, "please upload all images!")
                return self.form_invalid(form)
        else:
            messages.error(self.request, "Form is not valid")
            return self.form_invalid(form)
        # return super().form_valid(form)


class Update_Monitor_Product(View):
    template_name = "update_monitor.html"

    def all_images_uploaded_by_user(self, uploaded_images):
        if any(uploaded_images.values()):
            return True
        else:
            False

    def get(self, request, product_id):
        monitor = get_object_or_404(
            Monitors, monitor_id=product_id, user=self.request.user
        )

        monitor_features = monitor.special_features.all()

        # Get a list of special feature names for the monitor
        monitor_feature_names = [feature.name for feature in monitor_features]

        # Get the initial data for the form to preselect checkboxes
        initial_data = {
            "special_features": monitor_feature_names,
        }

        form = MonitorsForm(instance=monitor, initial=initial_data)

        context = {
            "form": form,
            "monitor": monitor,
            # "special_features_form": special_features_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, product_id):
        monitor = Monitors.objects.get(monitor_id=product_id, user=request.user)

        form = MonitorsForm(self.request.POST, self.request.FILES, instance=monitor)

        if form.is_valid():
            monitor = form.save(commit=False)
            # Same logic as before for Cloudinary upload and processing
            selected_features_names = form.cleaned_data.get("special_features")

            uploaded_images = {
                "image_1": self.request.FILES.get("image_1"),
                "image_2": self.request.FILES.get("image_2"),
                "image_3": self.request.FILES.get("image_3"),
            }
            # Clear all existing special features associated with the monitor
            monitor.special_features.clear()

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
                        setattr(monitor, f"image_{key[-1]}", resized_image_url)
                    else:
                        messages.info(
                            self.request, "images did not uploaded properly, Try again!"
                        )
                        return redirect("i:update_monitor", monitor_id=product_id)

                product_category_name = "COMPUTER"
                sub_category_name = "MONITORS"
                product_category = ProductCategory.objects.get(
                    name=product_category_name
                )
                sub_category = ComputerSubCategory.objects.get(name=sub_category_name)

                monitor.Product_Category = product_category
                monitor.Computer_SubCategory = sub_category
                monitor.user = self.request.user

                monitor.save()

                for feature_name in selected_features_names:
                    feature, created = Special_Features.objects.get_or_create(
                        name=feature_name
                    )
                    monitor.special_features.add(feature)
            else:
                product_category_name = "COMPUTER"
                sub_category_name = "MONITORS"
                product_category = ProductCategory.objects.get(
                    name=product_category_name
                )
                sub_category = ComputerSubCategory.objects.get(name=sub_category_name)

                monitor.Product_Category = product_category
                monitor.Computer_SubCategory = sub_category
                monitor.user = self.request.user

                monitor.save()

                for feature_name in selected_features_names:
                    feature, created = Special_Features.objects.get_or_create(
                        name=feature_name
                    )
                    monitor.special_features.add(feature)
            messages.success(request, "Monitor details updated successfully!")
            return render(
                self.request,
                "success_page.html",
                {"user_email": self.request.user.email},
            )
        else:
            messages.error(request, "Form is not valid")
            context = {"form": form, "monitor": monitor}
            return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_add_product_permission_required, name="dispatch")
class Delete_Monitors_Product(View):
    def get(self, request, **kwargs):
        monitor_id = kwargs["product_id"]
        try:
            monitor = Monitors.objects.get(monitor_id=monitor_id)

            if monitor.user == self.request.user:
                monitor.delete()
                messages.success(self.request, "Your Product has been deleted.")
                return redirect("i:list_of_monitors_for_user")
            else:
                messages.error(
                    self.request, "You do not have permission to delete this product."
                )
                return redirect("i:list_of_monitors_for_user")
        except monitor.DoesNotExist:
            messages.error(self.request, "this monitor does not exist")
            return redirect("i:list_of_monitors_for_user")


def List_View(request, model, filter_form, template_name):
    item_list = model.objects.all()
    filter = filter_form(request.GET, queryset=item_list)

    item_ratings, rating_count = Calculate_Ratings.calculate_ratings(item_list)

    paginated_items = paginate_items(request, item_list, 3)

    content_id = ContentType.objects.get(app_label="i", model="monitors").id

    context = {
        "item_list": paginated_items,
        "item_ratings": item_ratings,
        "rating_count": rating_count,
        "filter": filter,
        "content_id": content_id,
    }
    return render(request, template_name, context)


def Filter_List_View(request, model, filter_form_class, template_name):
    if request.method == "POST":
        filter_form = filter_form_class(request.POST or None)
        filtered_queryset = None

        if filter_form.is_valid():
            filtered_queryset = filter_form.qs

            item_ratings, rating_count = Calculate_Ratings.calculate_ratings(
                filtered_queryset
            )
            paginated_items = (
                paginate_items(request, filtered_queryset, 3)
                if filtered_queryset
                else None
            )

            context = {
                "form": filter_form,
                "item_list": paginated_items,
                "item_ratings": item_ratings,
                "rating_count": rating_count,
            }

            return render(request, template_name, context)
        else:
            return JsonResponse({"error": "Form is not valid"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)


def paginate_items(request, items_list, num_items):
    paginator = Paginator(items_list, num_items)
    page_number = request.GET.get("page")
    try:
        paginated_items = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_items = paginator.page(1)
    except EmptyPage:
        paginated_items = paginator.page(paginator.num_pages)
    return paginated_items


def MonitorListView(request):
    return List_View(request, Monitors, MonitorsFilter, "monitor_list.html")


def monitor_filter_list(request):
    return Filter_List_View(request, Monitors, MonitorsFilter, "partial_monitor.html")


def monitor_detail_view(request, product_id):
    monitor = Monitors.objects.get(monitor_id=product_id)

    comments = monitor.product_review.all()

    # Calculate the average rating, total ratings, and star ratings
    average_rating = RatingCalculator.calculate_average_rating(monitor)
    total_ratings = RatingCalculator.count_users_who_rated(monitor)

    star_ratings = {}

    for rating in [5, 4, 3, 2, 1]:
        star_ratings[rating] = RatingCalculator.count_star_ratings(monitor, rating)
    print(f"star_ratings{star_ratings}")

    # Calculate the width of rating bars
    width_percentages = {}

    for rating in [5, 4, 3, 2, 1]:
        count = star_ratings.get(rating, 0)
        width_percentages[rating] = (
            count / total_ratings * 100 if total_ratings > 0 else 0
        )
    print(f"width_percentages{width_percentages}")

    # make list of special features to pass in cookie
    sp = monitor.special_features.all()
    print(f"&&&&&&&&&&&&{sp}")
    sp_list = []
    for i in range(len(sp)):
        sp_list.append(sp[i].name)

    # add product image URL to session cookie
    scheme = "https://" if request.is_secure() else "http://"
    path = scheme + str(request.get_host()) + str(request.get_full_path())

    # key, values in cookie
    product_details = {
        "name": monitor.name,
        "price": str(monitor.price),
        "rating": str(average_rating),
        "image_url": str(monitor.image_1),
        "path": path,
        "special_features": sp_list,
    }
    add_product_to_browsing_history(request, product_details)
    zipped = your_browsing_history(request)

    # Falt = True => queryset will be a list of objects else tuple
    # It's useful when you want to retrieve specific fields from the database rather than entire model instances.
    # When you use values_list(), you can specify which fields you want to retrieve

    print(
        f"features----------------: {monitor.special_features.all().values_list('name', flat=True)}"
    )

    context = {
        "monitor": monitor,
        "average_rating": average_rating,
        "total_ratings": total_ratings,
        "star_ratings": star_ratings,
        "width_percentages": width_percentages,
        # "sp": monitor.special_features.all(),  this will display names
        # this will display names
        # he get_name_display() method because it is a method available on the model instance.
        # The method get_name_display() is automatically generated by Django for fields with choices defined.
        "sp": [
            feature.get_name_display() for feature in monitor.special_features.all()
        ],
        "comments": comments,
        "zipped": zipped,
    }

    return render(request, "product_detail.html", context=context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_comment_permission_required, name="dispatch")
class Monitor_Detail_View_Add_Review_Form(View):
    def all_images_uploaded_by_user(self, uploaded_images):
        if all(uploaded_images.values()):
            return True
        else:
            False

    def post(self, request, **kwargs):
        monitor_id = kwargs["product_id"]

        monitor = Monitors.objects.get(monitor_id=monitor_id)
        existing_review = Review.objects.filter(
            user=request.user, product=monitor
        ).exists()
        if existing_review:
            messages.error(
                request,
                "You have already submitted a review for this book format.",
            )
            return redirect("i:monitor_detail_view", product_id=monitor.monitor_id)

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
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
                            self.request, "images did not uploaded properly, Try again!"
                        )
                        return redirect("i:monitor_add_review")

                new_review.user = request.user
                new_review.product = monitor
                new_review.save()
                messages.success(request, "Review submitted successfully.")
                return redirect("i:add_review", product_id=monitor.monitor_id)
            else:
                messages.info(
                    self.request, "Please upload all images properly, Try again!"
                )
                return redirect(
                    "i:monitor_detail_view_add_review_form",
                    product_id=monitor.monitor_id,
                )
        else:
            messages.error(request, "Form is not valid.")
            return redirect(
                "i:monitor_detail_view_add_review_form", product_id=monitor.monitor_id
            )

    def get(self, request, **kwargs):
        context = {"form": ReviewForm()}
        return render(request, "monitor_detail_view_add_review_form.html", context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_comment_permission_required, name="dispatch")
class Monitor_Detail_View_Update_Review_Form(View):
    def all_images_uploaded_by_user(self, uploaded_images):
        if any(uploaded_images.values()):
            return True
        else:
            False

    def post(self, request, **kwargs):
        monitor_id = kwargs["product_id"]
        review_id = kwargs["review_id"]

        monitor = Monitors.objects.get(monitor_id=monitor_id)
        review = Review.objects.get(
            user=self.request.user, product=monitor, id=review_id
        )

        review_form = ReviewForm(self.request.POST, self.request.FILES, instance=review)
        if review_form.is_valid():
            new_review = review_form.save(
                commit=False
            )  # new review is now Review object, not an instance of ReviewForm
            uploaded_images = {
                "image_1": self.request.FILES.get("image_1"),
                "image_2": self.request.FILES.get("image_2"),
            }
            print(f"$$$$$$$$$$$${uploaded_images}")

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
                            self.request, "images did not uploaded properly, Try again!"
                        )
                        return redirect(
                            "i:monitor_update_review",
                            product_id=monitor_id,
                            review_id=review_id,
                        )

                new_review.user = self.request.user
                new_review.product = monitor
                new_review.save()
                messages.success(request, "Review submitted successfully.")
                return redirect("i:add_review", product_id=monitor_id)
            else:
                new_review.user = self.request.user
                new_review.product = monitor
                new_review.save()
                messages.success(request, "Review submitted successfully.")
                return redirect("i:add_review", product_id=monitor_id)
        else:
            messages.error(request, "Form is not valid.")
            return redirect(
                "i:monitor_update_review_form",
                product_id=monitor_id,
                review_id=review_id,
            )

    def get(self, request, **kwargs):
        monitor_id = kwargs["product_id"]
        comment_id = kwargs["review_id"]

        monitor = Monitors.objects.get(monitor_id=monitor_id)
        comment = Review.objects.get(product=monitor, id=comment_id)

        if comment.user != request.user:
            messages.info(
                self.request,
                f"you do not have permission to update other's comment/review",
            )
            return redirect("i:add_review", product_id=monitor_id)

        context = {"form": ReviewForm(instance=comment)}
        return render(request, "monitor_detail_view_add_review_form.html", context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_comment_permission_required, name="dispatch")
class Monitor_Detail_View_Delete_Review_Form(View):
    def get(self, request, **kwargs):
        comment_id = kwargs["review_id"]
        monitor_id = kwargs["product_id"]

        monitor = Monitors.objects.get(monitor_id=monitor_id)
        comment = Review.objects.get(id=comment_id, product=monitor)

        if comment.user == self.request.user:
            comment.delete()
            messages.success(self.request, "Your comment has been deleted.")
            return redirect("i:add_review", product_id=monitor_id)
        else:
            messages.error(
                self.request, "You do not have permission to delete this comment."
            )
            return redirect("i:add_review", product_id=monitor_id)
