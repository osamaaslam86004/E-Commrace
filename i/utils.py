# utils/rating_utils.py

from django.db.models import Avg, Count, Q, F, Prefetch, When, Case, Value
from django.db import models
from book_.models import Rating
from i.models import Review, Monitors, Special_Features
from django.http import QueryDict
from urllib.parse import urlencode
from django.core import signing


def user_submitted_data_to_dictionary(filter_form):
    """Since QueryDict cannot be stored directly in cookie or redis cache,
    this View will extract user submitted data from Django filters forms and
    return a dictionary"""

    post_data_dictionary = {}

    monitor_type = filter_form.form.cleaned_data.get("monitor_type")
    mounting_type = filter_form.form.cleaned_data.get("mounting_type")
    max_display_resolution = filter_form.form.cleaned_data.get("max_display_resolution")
    refresh_rate = filter_form.form.cleaned_data.get("refresh_rate")
    brand = filter_form.form.cleaned_data.get("brand")
    special_features = filter_form.form.cleaned_data.get("special_features", None)
    choose_special_features = filter_form.form.cleaned_data.get(
        "choose_special_features", None
    )

    if monitor_type:
        post_data_dictionary["monitor_type"] = monitor_type
    if mounting_type:
        post_data_dictionary["mounting_type"] = mounting_type
    if max_display_resolution:
        post_data_dictionary["max_display_resolution"] = max_display_resolution
    if refresh_rate:
        post_data_dictionary["refresh_rate"] = refresh_rate
    if brand:
        post_data_dictionary["brand"] = brand
    if special_features:
        post_data_dictionary["special_features"] = str(special_features)
        print(
            f"post_data_dictionary['special_features']---------{post_data_dictionary['special_features']}"
        )
    else:
        post_data_dictionary["choose_special_features"] = str(special_features)
        print(
            f"post_data_dictionary['choose_special_features']---------{post_data_dictionary['choose_special_features']}"
        )
    return post_data_dictionary


def storing_filtered_conditions_in_cookie(
    request, response, post_data, content_type_id
):
    """Create, a either a sessionid or 'filtered_conditions' cookie storing the signed
    request.POST QueryDict in python dictionary. Returns cookie in Response"""

    # adding content type to post data dictionary
    post_data["content_type_id"] = content_type_id
    print(f"content type in cookie----- {post_data['content_type_id']}")

    # Store in session if the user is authenticated
    if request.session and request.user.is_authenticated:
        request.session["filtered_conditions"] = post_data
        request.session.modified = True
    else:

        signer = signing.TimestampSigner()
        post_data = signer.sign_object(post_data)

        # Store in a cookie for unauthenticated users, signed for security
        response.set_signed_cookie(
            "filtered_conditions",
            # json.dumps(post_data),
            post_data,
            salt="My_post_data",
            httponly=True,
            secure=True,  # Optional: Set to True if using HTTPS
            max_age=450,  # Set cookie expiry (e.g., 7.5 minutes)
            samesite="Lax",
        )
    return response


def fetching_filtered_conditions_from_cookie(request):
    """The View will fetch the cookie to extract filtered condtions in dictionary format.
    Returns a dictionary"""

    if request.session and request.user.is_authenticated:
        post_data = request.session.get("filtered_conditions")
    else:
        post_data = request.get_signed_cookie(
            "filtered_conditions", None, salt="My_post_data"
        )

        signer = signing.TimestampSigner()
        post_data = signer.unsign_object(post_data)
    return post_data


def py_dictionary_to_query_dictionary(filtered_conditions):
    """convert the filtered conditions in dictionary format to QueryDict so that we can
    provide as an input to django_filter form to render filtered results for
    page 2, page 3, and so on"""

    # Convert dictionary to a query string
    query_string = urlencode(filtered_conditions, doseq=True)
    print(f"query string--- {query_string}")

    # Create a mutable QueryDict from the query string
    query_dictionary = QueryDict(query_string, mutable=True)

    return query_dictionary


class MonitorDetailViewHelperFunctions:

    @staticmethod
    def getting_data(product_id):
        monitor_data = (
            Monitors.objects.filter(monitor_id=product_id)
            .prefetch_related(
                Prefetch(
                    "special_features",
                    queryset=Special_Features.objects.all().only("name"),
                ),
                Prefetch(
                    "product_review",
                    queryset=Review.objects.filter(
                        status=True, product_id__monitor_id=product_id
                    ).select_related("user"),
                ),
            )
            .annotate(
                five_star_count=Count(
                    "product_review", filter=Q(product_review__rating=5)
                ),
                four_star_count=Count(
                    "product_review", filter=Q(product_review__rating=4)
                ),
                three_star_count=Count(
                    "product_review", filter=Q(product_review__rating=3)
                ),
                two_star_count=Count(
                    "product_review", filter=Q(product_review__rating=2)
                ),
                one_star_count=Count(
                    "product_review", filter=Q(product_review__rating=1)
                ),
            )
            .annotate(
                rating_count=F("five_star_count")
                + F("four_star_count")
                + F("three_star_count")
                + F("two_star_count")
                + F("one_star_count"),
                average_rating=Case(
                    When(rating_count=0, then=Value(0)),  # Avoid division by zero
                    default=(
                        (
                            F("five_star_count") * 5
                            + F("four_star_count") * 4
                            + F("three_star_count") * 3
                            + F("two_star_count") * 2
                            + F("one_star_count") * 1
                        )
                        / F("rating_count")
                    ),
                    output_field=models.DecimalField(
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
            )
        )
        return monitor_data  # Ensure this returns the queryset directly

    @staticmethod
    def calculate_width_percentages_for_rating_progress_bar(monitor_data):
        # fetching the first instance from queryset

        width_percentages = {}

        for rating in [(5, "five"), (4, "four"), (3, "three"), (2, "two"), (1, "one")]:
            count = getattr(monitor_data, f"{rating[1]}_star_count", 0)
            rating = rating[0]
            width_percentages[rating] = (
                (count / monitor_data.rating_count * 100)
                if monitor_data.rating_count > 0
                else 0
            )
            print(f"width percentage---- {width_percentages}")
        return width_percentages

    @staticmethod
    def creating_star_ratings_dictionary(monitor_data):
        star_ratings = {
            "5": monitor_data.five_star_count,
            "4": monitor_data.four_star_count,
            "3": monitor_data.three_star_count,
            "2": monitor_data.two_star_count,
            "1": monitor_data.one_star_count,
        }
        return star_ratings

    @staticmethod
    def preparing_data_for_browsing_history_cookie(request, monitor_data):
        scheme = "https://" if request.is_secure() else "http://"
        path = scheme + str(request.get_host()) + str(request.get_full_path())

        # key, values in cookie
        product_details = {
            "name": monitor_data.name,
            "price": str(monitor_data.price),
            "rating": str(monitor_data.average_rating),
            "image_url": str(monitor_data.image_1),
            "path": path,
            "special_features": [
                feature.get_name_display()
                for feature in monitor_data.special_features.all()
            ],
        }
        print(f"-------------{product_details}")
        return product_details

    @staticmethod
    def prepare_context(monitor_data, star_ratings, width_percentages, zipped):
        context = {
            "monitor": monitor_data,
            "average_rating": monitor_data.average_rating,
            "total_ratings": monitor_data.rating_count,
            "star_ratings": star_ratings,
            "width_percentages": width_percentages,
            "sp": [
                feature.get_name_display()
                for feature in monitor_data.special_features.all()
            ],
            "comments": monitor_data.product_review.all(),
            "zipped": zipped,
        }
        return context


class MonitorDetailViewAddReviewHelper:

    @staticmethod
    def getting_data(product_id):
        monitor_data = Monitors.objects.filter(monitor_id=product_id).prefetch_related(
            Prefetch(
                "product_review",
                queryset=Review.objects.filter(
                    status=True, product_id__monitor_id=product_id
                ).select_related("user"),
            ),
        )
        return monitor_data


class UpdateMonitorProduct:

    @staticmethod
    def get_monitor_instance(product_id):
        monitor_data = (
            Monitors.objects.filter(monitor_id=product_id)
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "special_features",
                    queryset=Special_Features.objects.all().only("id"),
                )
            )
            .first()
        )
        return monitor_data


class RatingCalculator:
    @staticmethod
    def calculate_average_rating(item):
        # Calculate the average rating for the reviews associated with the specific monitor item
        return (
            item.product_review.aggregate(average_rating=Avg("rating"))[
                "average_rating"
            ]
            or 0.0
        )

    @staticmethod
    def count_users_who_rated(monitor):
        return Review.objects.filter(product=monitor).count()

    @staticmethod
    def count_star_ratings(monitor, star_rating):
        return Review.objects.filter(product=monitor, rating=star_rating).count()


class Calculate_Ratings:
    @staticmethod
    def calculate_ratings(item_list):

        # Get all monitors with their average rating and rating count precomputed
        item_list = item_list.annotate(
            average_rating=Avg(
                "product_review__rating"
            ),  # Average rating for each monitor
            rating_count=Count(
                "product_review__rating"
            ),  # Total number of ratings for each monitor
        )

        return item_list


class BookRatingCalculator:
    @staticmethod
    def calculate_average_rating(item):
        return (
            Rating.objects.filter(book_format=item).aggregate(
                average_rating=Avg("rating")
            )["average_rating"]
            or 0.0
        )

    @staticmethod
    def count_users_who_rated(item):
        return Rating.objects.filter(book_format=item).count()

    @staticmethod
    def count_star_ratings(item, star_rating):
        return Review.objects.filter(product=item, rating=star_rating).count()


class Book_Calculate_Ratings:
    @staticmethod
    def calculate_ratings(item_list):
        item_ratings = {}
        rating_count = {}

        for item in item_list:
            average_rating = BookRatingCalculator.calculate_average_rating(item)
            total_ratings = BookRatingCalculator.count_users_who_rated(item)

            item_ratings[item] = average_rating
            rating_count[item] = total_ratings

        return item_ratings, rating_count
