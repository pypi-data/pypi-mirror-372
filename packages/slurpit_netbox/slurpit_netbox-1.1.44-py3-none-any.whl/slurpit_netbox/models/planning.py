from django.db import models
from netbox.models import PrimaryModel
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class SlurpitPlanning(PrimaryModel):
    name = models.CharField(max_length=255, unique=True)
    planning_id = models.BigIntegerField(unique=True)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"
    
    def get_absolute_url(self):
        return reverse("plugins:slurpit_netbox:slurpitplanning", args=[self.pk])

    class Meta:
        ordering = ('name',)
        verbose_name = _('Slurpit Planning')
        verbose_name_plural = _('Slurpit Plannings')

class SlurpitSnapshot(PrimaryModel):
    hostname = models.CharField(max_length=255)
    planning_id = models.BigIntegerField()
    content = models.JSONField()
    result_type = models.CharField(max_length=255, default="template_result")

    def __str__(self):
        return f"{self.hostname}#{self.planning_id}"

    class Meta:
        ordering = ('planning_id', 'hostname', )
        verbose_name = _('Slurpit Snapshot')
        verbose_name_plural = _('Slurpit Snapshots')