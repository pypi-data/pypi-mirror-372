from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel
from netbox.models.features import (
    CustomValidationMixin,
    EventRulesMixin,
    ExportTemplatesMixin,
    TagsMixin,
)
from utilities.choices import ChoiceSet
from utilities.querysets import RestrictedQuerySet


class StatusChoices(ChoiceSet):
    key = "SyncStatus.status"

    CHOICES = [
        ("success", "Success", "green"),
        ("failed", "Failed", "red"),
        ("skip", "Skipped", "primary"),
    ]


class SyncSystem(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    object_types = models.ManyToManyField(
        to="core.ObjectType",
        related_name="+",
        blank=True,
        help_text=_(
            "The object type(s) to which this system can report sync status to."
        ),
    )

    def get_absolute_url(self):
        return reverse("plugins:netbox_sync_status:syncsystem", args=[self.pk])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = "Sync System"
        verbose_name_plural = "Sync Systems"


class SyncStatus(
    CustomValidationMixin,
    ExportTemplatesMixin,
    TagsMixin,
    EventRulesMixin,
    models.Model,
):
    objects = RestrictedQuerySet.as_manager()

    object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
    )

    object_id = models.PositiveBigIntegerField(blank=True, null=True)

    object = GenericForeignKey(ct_field="object_type", fk_field="object_id")

    created = models.DateTimeField(
        verbose_name=_("created"), auto_now_add=True, blank=True, null=True
    )

    status = models.CharField(
        max_length=30,
        choices=StatusChoices,
    )

    system = models.ForeignKey(
        to=SyncSystem, on_delete=models.CASCADE, related_name="sync_events"
    )

    message = models.TextField(blank=True)

    is_latest = models.BooleanField(default=True)

    def get_status_color(self):
        return StatusChoices.colors.get(self.status)

    class Meta:
        ordering = ("system",)
        verbose_name = "Sync Status"
        verbose_name_plural = "Sync Status"

    def __str__(self):
        return f"{self.system} - {self.status}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            old_items = SyncStatus.objects.filter(
                Q(is_latest=True)
                & Q(object_id=self.object_id)
                & Q(object_type=self.object_type)
                & Q(system=self.system)
            )

            for status in old_items:
                status.is_latest = False
                super(SyncStatus, status).save()

            super(SyncStatus, self).save(*args, **kwargs)
