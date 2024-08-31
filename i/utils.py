# utils/rating_utils.py

from django.db.models import Avg
from i.models import Review
from book_.models import Rating


class RatingCalculator:
    @staticmethod
    def calculate_average_rating(monitor):
        return (
            Review.objects.filter(product=monitor).aggregate(
                average_rating=Avg("rating")
            )["average_rating"]
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
        item_ratings = {}
        rating_count = {}

        for item in item_list:
            average_rating = RatingCalculator.calculate_average_rating(item)
            total_ratings = RatingCalculator.count_users_who_rated(item)

            item_ratings[item] = average_rating
            rating_count[item] = total_ratings

        return item_ratings, rating_count


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
