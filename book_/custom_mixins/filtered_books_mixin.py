from django.db.models import Avg, Count, Q

from book_.forms import CustomBookFormatFilterForm
from book_.models import BookFormat


class FilteredBooksMixin:
    def get_queryset(self, form=None):
        queryset = BookFormat.objects.all().order_by("price")
        if form and form.is_valid():
            filter_conditions = Q()

            is_used_available = form.cleaned_data.get("is_used_available") == "on"
            is_new_available = form.cleaned_data.get("is_new_available") == "on"

            format = form.cleaned_data.get("format")
            if format:
                filter_conditions |= Q(format=format)

            book_name = form.cleaned_data.get("book_name")
            if book_name:
                filter_conditions &= Q(book_author_name__book_name__icontains=book_name)

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

            queryset = queryset.annotate(
                avg_rating=Avg("rating_format__rating"),
                num_users_rated=Count("rating_format__user", distinct=True),
            ).filter(filter_conditions, is_active="1")

        return queryset.order_by("-price")
