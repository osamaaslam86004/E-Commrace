from django.urls import path
from blog import views
from blog.views import CreatePostView, Search_Results_For_Admin_My_Post

urlpatterns = [
    path("", views.PostListView, name="post_list"),
    path("my_posts/", views.my_posts_list, name="my_posts_list"),
    path("create/", CreatePostView.as_view(), name="blog_post_create"),
    path("search/", views.search_view, name="search_view"),
    path("search/results/", views.search_results_view, name="search_results_view"),
    path(
        "search/admin-search-results/",
        Search_Results_For_Admin_My_Post.as_view(),
        name="admin_search_results_view",
    ),
    path("<slug:slug>/", views.live_post, name="live_post"),
    path("<slug:slug>/update/", views.update_post, name="blog_post_update"),
    path("<slug:slug>/delete/", views.delete_post, name="blog_post_delete"),
    path("<slug:slug>/<int:comment_id>/", views.update_comment, name="update_comment"),
    path(
        "<slug:slug>/delete-comment/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),
]
