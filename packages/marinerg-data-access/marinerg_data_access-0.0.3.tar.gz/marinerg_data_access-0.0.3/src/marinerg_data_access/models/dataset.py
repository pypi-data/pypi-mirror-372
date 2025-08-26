from django.db import models

from ichec_django_core.models import PortalMember, TimesStampMixin


class Dataset(TimesStampMixin):

    creator = models.ForeignKey(PortalMember, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    uri = models.CharField(max_length=250, blank=True)
    is_public = models.BooleanField(default=True)
    access_instructions = models.TextField(blank=True)
