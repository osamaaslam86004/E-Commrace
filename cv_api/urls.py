from django.urls import path
from cv_api import views
from cv_api.views import (
    CVApiPostRequest,
    CVApiSubmitForm,
    RetrieveCVDataToUpdate,
    WebHookEvent,
    ListOfCVForUser,
    DeleteCVForUser,
)


urlpatterns = [
    path(
        "cv_view/",
        CVApiPostRequest.as_view(),
        name="cv_view",
    ),
    path(
        "cv_submit_form/",
        CVApiSubmitForm.as_view(),
        name="submit_form",
    ),
    # display list of CV's in cards
    path(
        "list_of_cv_for_user/",
        ListOfCVForUser.as_view(),
        name="list_of_cv_for_user",
    ),
    # update a particular / specific cv
    path(
        "get_cv_to_update/<int:personal_info_id>/",
        RetrieveCVDataToUpdate.as_view(),
        name="get_cv_to_update",
    ),
    path(
        "get_cv_to_delete/<int:personal_info_id>/",
        DeleteCVForUser.as_view(),
        name="get_cv_to_delete",
    ),
    # webhook to confirm the status=[updated, failed, in_progress] of particular cv is
    path(
        "cv-webhook/",
        WebHookEvent.as_view(),
        name="cv-webhook",
    ),
]
