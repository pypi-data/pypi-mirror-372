from django.db import models
from netbox.models import NetBoxModel
from django.utils.translation import gettext_lazy as _

class SlurpitMapping(NetBoxModel):
    source_field = models.CharField(max_length=255, unique=True)
    target_field = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.source_field}"

    class Meta:
        ordering = ('source_field',)
        verbose_name = _('Slurpit Mapping')
        verbose_name_plural = _('Slurpit Mapping')