from core.models import ObjectType
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from utilities.api import get_serializer_for_model

from ..models import SyncStatus, SyncSystem


class SyncStatusSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_sync_status-api:syncstatus-detail"
    )

    object_id = serializers.IntegerField()
    object_type = ContentTypeField(
        queryset=ObjectType.objects.public(),
    )

    object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SyncStatus
        fields = (
            "created",
            "url",
            "system",
            "status",
            "message",
            "object_type",
            "object_id",
            "object",
        )
        brief_fields = (
            "created",
            "url",
            "system",
            "status",
            "message",
            "object_type",
            "object_id",
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_object(self, instance):
        if not instance.object:
            return None
        serializer = get_serializer_for_model(instance.object)
        context = {"request": self.context["request"]}
        return serializer(instance.object, nested=True, context=context).data


class SyncSystemSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_sync_status-api:syncsystem-detail"
    )

    display = serializers.SerializerMethodField(read_only=True)

    object_types = ContentTypeField(
        queryset=ObjectType.objects.public(), many=True, required=False
    )

    @extend_schema_field(OpenApiTypes.STR)
    def get_display(self, obj):
        return obj.name

    class Meta:
        model = SyncSystem
        fields = (
            "id",
            "created",
            "url",
            "name",
            "display",
            "description",
            "tags",
            "object_types",
        )
        brief_fields = (
            "id",
            "created",
            "url",
            "name",
            "display",
            "description",
            "object_types",
        )


class SyncSystemObjectStatusSerializer(serializers.Serializer):
    object_id = serializers.IntegerField()
    object_type = ContentTypeField(
        queryset=ObjectType.objects.public(),
    )
    status = serializers.CharField()
