from rest_framework import viewsets, permissions

from ichec_django_core.view_sets import ObjectFileDownloadView, ObjectFileUploadView

from marinerg_facility.models import TestFacility
from marinerg_facility.serializers import TestFacilitySerializer


class TestFacilityViewSet(viewsets.ModelViewSet):
    queryset = TestFacility.objects.all()
    serializer_class = TestFacilitySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def get_queryset(self):
        queryset = TestFacility.objects.all()
        member_id = self.request.query_params.get("user")
        if member_id is not None:
            queryset = queryset.filter(members__id=member_id)
        return queryset


class FacilityImageDownloadView(ObjectFileDownloadView):
    model = TestFacility
    file_field = "image"


class FacilityImageUploadView(ObjectFileUploadView):
    model = TestFacility
    queryset = TestFacility.objects.all()
    file_field = "image"
