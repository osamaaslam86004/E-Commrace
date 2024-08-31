from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps
from book_.models import Review


def user_add_product_permission_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            user_type = request.user.user_type

            if (
                user_type == "SELLER"
                and request.user.has_perm("Homepage.seller_add_product")
                and request.user.has_perm("Homepage.seller_update_product")
                and request.user.has_perm("Homepage.seller_delete_product")
            ):
                return view_func(request, *args, **kwargs)

            elif (
                user_type == "MANAGER"
                and request.user.has_perm("Homepage.manager_add_product")
                and request.user.has_perm("Homepage.manager_update_product")
                and request.user.has_perm("Hompage.manager_delete_product")
            ):
                return view_func(request, *args, **kwargs)

            elif user_type == "ADMIN" or user_type == "ADMINISTRATOR":
                return view_func(request, *args, **kwargs)
            else:
                return render(
                    request,
                    "permission_denied.html",
                    {
                        "user_email": request.user.email,
                        "user_permission": "add product",
                    },
                )
        else:
            messages.error(request, "Your are not logged in. Please Log-in!")
            return redirect("Homepage:login")

    return _wrapped_view


def user_comment_permission_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_type = request.user.user_type

        if (
            user_type == "CUSTOMER"
            and request.user.has_perm("Homepage.customer_add_comment")
            and request.user.has_perm("Homepage.customer_edit_comment")
            and request.user.has_perm("Homepage.customer_delete_comment")
        ):
            return view_func(request, *args, **kwargs)

        elif (
            user_type == "SELLER"
            and request.user.has_perm("Homepage.seller_add_comment")
            and request.user.has_perm("Homepage.seller_edit_comment")
            and request.user.has_perm("Homepage.seller_delete_comment")
        ):
            return view_func(request, *args, **kwargs)

        elif (
            user_type == "CUSTOMER REPRESENTATIVE"
            and request.user.has_perm("Homepage.csr_add_comment")
            and request.user.has_perm("Homepage.csr_edit_comment")
            and request.user.has_perm("Homepage.csr_delete_comment")
        ):
            return view_func(request, *args, **kwargs)

        elif (
            user_type == "MANAGER"
            and request.user.has_perm("Homepage.manager_add_comment")
            and request.user.has_perm("Homepage.manager_edit_comment")
            and request.user.has_perm("Homepage.manager_delete_comment")
        ):
            return view_func(request, *args, **kwargs)

        elif user_type == "ADMINISTRATOR" or user_type == "ADMIN":
            return view_func(request, *args, **kwargs)

        else:
            return render(
                request,
                "permission_denied.html",
                {
                    "user_email": request.user.email,
                    "user_permission": "add / Edit / Delete other's comment",
                },
            )

    return _wrapped_view


def check_user_linked_to_comment(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_type = request.user.user_type
        review_id = kwargs["review_id"]
        review = Review.objects.get(id=review_id)

        if user_type == "CUSTOMER" and review.user == request.user:
            return view_func(request, *args, **kwargs)

        elif user_type == "SELLER" and review.user == request.user:
            return view_func(request, *args, **kwargs)

        elif user_type == "CUSTOMER REPRESENTATIVE" and review.user == request.user:
            return view_func(request, *args, **kwargs)

        elif user_type == "MANAGER" and review.user == request.user:
            return view_func(request, *args, **kwargs)

        elif (
            user_type == "ADMINISTRATOR"
            or user_type == "ADMIN"
            and review.user == request.user
        ):
            return view_func(request, *args, **kwargs)

        else:
            return render(
                request,
                "permission_denied.html",
                {
                    "user_email": request.user.email,
                    "user_permission": "add / Edit / Delete other's comment",
                },
            )

    return _wrapped_view
