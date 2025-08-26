from django.db import models

from ichec_django_core.models import Organization


class TestFacility(Organization):

    is_active = models.BooleanField(default=True)
    is_partner = models.BooleanField(default=False)
    image = models.ImageField(blank=True)

    class Meta:
        verbose_name = "Test Facility"
        verbose_name_plural = "Test Facilities"
