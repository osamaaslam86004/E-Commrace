# utils/rating_utils.py

from django.db.models import Avg, Count
from book_.models import Rating

class RatingCalculator:
    @staticmethod
    def calculate_average_rating(book):
        return Rating.objects.filter(
            book_format=book
        ).aggregate(average_rating=Avg('rating'))['average_rating'] or 0.0

    @staticmethod
    def count_users_who_rated(book):
        return Rating.objects.filter(
            book_format=book
        ).count()

    @staticmethod
    def count_star_ratings(book, star_rating):
        return Rating.objects.filter(
            book_format=book,
            rating=star_rating
        ).count()
    
    
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