from i import views
from django.urls import path
from i.views import (
    List_Of_Products_Category,
    List_Of_Books_For_User,
    Create_Monitors_Product,
    Update_Monitor_Product,
    Delete_Monitors_Product,
    List_Of_Monitors_For_User,
    Monitor_Detail_View_Add_Review_Form,
    Monitor_Detail_View_Update_Review_Form,
    Monitor_Detail_View_Delete_Review_Form,
)

urlpatterns = [
    # create a product of any category
    path("success_page/", views.success_page, name="success_page"),
    path(
        "select_product_category/",
        views.select_product_category,
        name="select_product_category",
    ),
    path(
        "load_subcategory_form/",
        views.load_subcategory_form,
        name="load_subcategory_form",
    ),
    path(
        "load_subsubcategory_form/",
        views.load_subsubcategory_form,
        name="load_subsubcategory_form",
    ),
    path(
        "load_sub_subsubcategory_form/",
        views.load_sub_subsubcategory_form,
        name="load_sub_subsubcategory_form",
    ),
    path(
        "load_sub_sub_subsubcategory_form/",
        views.load_sub_sub_subsubcategory_form,
        name="load_sub_sub_subsubcategory_form",
    ),
    # update a product of any category
    path(
        "profile/update-product/",
        List_Of_Products_Category.as_view(),
        name="list_of_products_category",
    ),
    # List of books for logged-in seller only
    path(
        "profile/update-product/books/",
        List_Of_Books_For_User.as_view(),
        name="list_of_books_for_user",
    ),
    # List of monitors for logged-in seller only
    path(
        "profile/update-product/monitors/",
        List_Of_Monitors_For_User.as_view(),
        name="list_of_monitors_for_user",
    ),
    # Seller can add a Monitors product
    path("add_monitor/", Create_Monitors_Product.as_view(), name="add_monitor"),
    path(
        "profile/update-product/monitors/<int:product_id>/",
        Update_Monitor_Product.as_view(),
        name="update_monitor",
    ),
    # Delete monitor product
    path(
        "profile/update-product/monitors/delete/<int:product_id>/",
        Delete_Monitors_Product.as_view(),
        name="delete_monitor",
    ),
    # Monitor category
    path("monitor/", views.MonitorListView, name="MonitorListView"),
    # filter results for Monitor
    path("monitor-filtered-results/", views.monitor_filter_list, name="filter"),
    # Monitor detail view with reviews
    path(
        "monitor-detail-view/<int:product_id>/",
        views.monitor_detail_view,
        name="add_review",
    ),
    # add review in Monitor product
    path(
        "monitor-detail-view/add-review-form/<int:product_id>/",
        Monitor_Detail_View_Add_Review_Form.as_view(),
        name="monitor_add_review",
    ),
    # update review in Monitor product
    path(
        "monitor-detail-view/update-review-form/<int:product_id>/<int:review_id>/",
        Monitor_Detail_View_Update_Review_Form.as_view(),
        name="monitor_update_review",
    ),
    # delete review in Monitor product
    path(
        "monitor-detail-view/delete-review-form/<int:product_id>/<int:review_id>/",
        Monitor_Detail_View_Delete_Review_Form.as_view(),
        name="monitor_delete_review",
    ),
]
