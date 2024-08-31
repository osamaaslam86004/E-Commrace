from django.urls import path
from checkout import views
from checkout.views import CheckOutView, View_Orders, Charge_Refund


urlpatterns = [
    path(
        "checkout-view/",
        CheckOutView.as_view(),
        name="check_out",
    ),
    path("view-orders-or-refund/", View_Orders.as_view(), name="view_orders"),
    path(
        "view-orders-or-refund/<int:id>/",
        Charge_Refund.as_view(),
        name="refund",
    ),
    path("stripe_webhook/", views.stripe_webhook, name="stripe_webhook"),
]
