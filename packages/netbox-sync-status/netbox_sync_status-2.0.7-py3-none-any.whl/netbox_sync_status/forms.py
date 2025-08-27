from netbox.forms import NetBoxModelForm
from .models import SyncSystem


class SyncSystemForm(NetBoxModelForm):
    class Meta:
        model = SyncSystem
        fields = ("name", "description", "object_types", "tags")
