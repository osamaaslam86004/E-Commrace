from django.urls import path
from book_ import views
from book_.views import (
    FilteredBooksView,
    Book_Detail_View,
    Book_Detail_View_Add_Review_Form,
    Book_Detail_View_Update_Review_Form,
    Custom_Delete_Comment,
    Create_Book_Formats_View,
    Update_Book_Formats_View,
    Delete_Book_Format_View,
)


urlpatterns = [
    # seller can create a book
    path(
        "create_book_formats/",
        Create_Book_Formats_View.as_view(),
        name="create_update_book_formats",
    ),
    # seller can delete a book
    path(
        "delete_book_formats/<int:pk>/",
        Delete_Book_Format_View.as_view(),
        name="delete_book_formats",
    ),
    # seller can update a book
    path(
        "update_book_formats/<int:pk>/",
        Update_Book_Formats_View.as_view(),
        name="update_book_formats",
    ),
    # display filter book results
    path("books/filters/", FilteredBooksView.as_view(), name="book_list_filters"),
    # add a review
    path(
        "books/book_detail_view/review/<int:book_author_name_id>/<int:format_id>/",
        Book_Detail_View_Add_Review_Form.as_view(),
        name="book_detail_view_add_review_form",
    ),
    # display book detail
    path(
        "books/book_detail_view/<int:pk>/<int:format_id>/",
        Book_Detail_View.as_view(),
        name="book_detail_view",
    ),
    # edit a review
    path(
        "books/book_detail_view/edit_review_rating/<int:review_id>/",
        Book_Detail_View_Update_Review_Form.as_view(),
        name="edit_review_rating",
    ),
    # delete comment
    path(
        "books/book_detail_view/<int:review_id>/",
        Custom_Delete_Comment.as_view(),
        name="delete_review_rating",
    ),
]
