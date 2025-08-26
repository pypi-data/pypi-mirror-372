from django.urls import path

from .view_sets import (
    TestFacilityViewSet,
    FacilityImageDownloadView,
    FacilityImageUploadView,
)


def register_drf_views(router):
    router.register(r"facilities", TestFacilityViewSet)


urlpatterns = [
    path(
        r"facilities/<int:pk>/image",
        FacilityImageDownloadView.as_view(),
        name="facility_images",
    ),
    path(
        r"facilities/<int:pk>/image/upload",
        FacilityImageUploadView.as_view(),
        name="facility_images_upload",
    ),
]
