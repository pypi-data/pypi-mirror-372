import django_filters
from core.models import ObjectType
from django import forms
from django.db.models import Q
from django.utils.translation import gettext as _
from netbox.filtersets import BaseFilterSet
from netbox.forms import NetBoxModelFilterSetForm
from utilities.filters import ContentTypeFilter
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import (
    ContentTypeMultipleChoiceField,
    DynamicModelMultipleChoiceField,
)

from .models import StatusChoices, SyncStatus, SyncSystem


class SyncStatusFilterForm(NetBoxModelFilterSetForm):
    model = SyncStatus
    q = None  # remove search field

    object_id = forms.CharField(
        label=_("Object ID"),
        required=False,
    )

    object_type_id = ContentTypeMultipleChoiceField(
        queryset=ObjectType.objects.public(),
        required=False,
        label=_("Object Type"),
    )

    system = DynamicModelMultipleChoiceField(
        queryset=SyncSystem.objects.all(), required=False, label=_("System")
    )

    status = forms.MultipleChoiceField(
        required=False, label="Status", choices=StatusChoices
    )

    is_latest = forms.NullBooleanField(
        required=False,
        label="Show last sync only for each object/system only",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )


class SyncStatusFilterSet(BaseFilterSet):
    class Meta:
        model = SyncStatus
        fields = ("system", "status", "message", "is_latest", "object_type_id", "object_type")

    object_id = django_filters.CharFilter(
        method="search",
        label=_("Object ID"),
    )

    object_type = ContentTypeFilter()

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset

        return queryset.filter(Q(object_id=value))
