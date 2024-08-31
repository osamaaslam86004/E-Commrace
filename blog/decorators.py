from django.contrib.auth.decorators import user_passes_test
from Homepage.models import CustomUser
from django.shortcuts import render


def can_update_blogpost(user):
    # Check if the user has the 'update_blogpost' permission
    return user.has_perm("Homepage.update_blogpost")


update_blogpost_required = user_passes_test(can_update_blogpost)


def create_update_delete_blogpost_permission_required(view_func):
    """
    Custom decorator to check if the user has 'update_blogpost' permission.
    """

    def _wrapped_view(request, *args, **kwargs):
        if (
            request.user.has_perm("Homepage.admin_create_blog")
            and request.user.has_perm("Homepage.admin_update_blog")
            and request.user.has_perm("Homepage.admin_delete_blog")
        ):
            return view_func(request, *args, **kwargs)
        else:
            user_email = request.user.email  # Get the user's name (or email)
            user_permission = "update blog"
            return render(
                request,
                "permission_denied.html",
                {"user_email": user_email, "user_permission": user_permission},
            )

    return _wrapped_view
