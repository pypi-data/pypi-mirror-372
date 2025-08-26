from rest_framework import serializers
from django_countries.serializers import CountryFieldMixin

from marinerg_facility.models import TestFacility


class TestFacilitySerializer(CountryFieldMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TestFacility
        fields = [
            "name",
            "acronym",
            "description",
            "address",
            "website",
            "id",
            "url",
            "country",
            "is_active",
            "is_partner",
            "members",
            "image",
        ]
