import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from .models import SyncStatus, SyncSystem


class SyncStatusListTable(NetBoxTable):
    actions = columns.ActionsColumn(actions=())

    system = tables.Column(linkify=True)

    object = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = SyncStatus
        fields = ("status", "object_type", "object", "system", "message", "created")


class SyncSystemListTable(NetBoxTable):
    name = tables.Column(linkify=True)

    tags = columns.TagColumn(url_name="plugins:netbox_sync_status:syncsystem_list")

    class Meta(NetBoxTable.Meta):
        model = SyncSystem
        fields = ("name", "description", "tags")
