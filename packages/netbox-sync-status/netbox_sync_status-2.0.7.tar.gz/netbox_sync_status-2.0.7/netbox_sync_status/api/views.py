from core.events import OBJECT_UPDATED
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from drf_spectacular.utils import extend_schema
from extras.events import enqueue_event
from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import BaseViewSet, NetBoxModelViewSet
from netbox.context import events_queue
from rest_framework import mixins as drf_mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from netbox_sync_status.filtersets import SyncStatusFilterSet

from .. import models
from .serializers import (
    SyncStatusSerializer,
    SyncSystemObjectStatusSerializer,
    SyncSystemSerializer,
)


class ObjectSyncView(APIView):
    queryset = models.SyncStatus.objects.all()
    serializer_class = None

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request, obj_type, pk, format=None):
        if not obj_type or "." not in obj_type:
            return Response(
                {"detail": "Invalid object type"}, status=status.HTTP_400_BAD_REQUEST
            )

        app_label, model_name = obj_type.split(".")
        self.queryset = apps.get_model(app_label, model_name).objects
        selected_objects = self.queryset.filter(
            pk=pk,
        )

        for obj in selected_objects:
            obj.snapshot()
            queue = events_queue.get()
            enqueue_event(queue, obj, request.user, request.id, OBJECT_UPDATED)
            events_queue.set(queue)

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class SyncStatusViewSet(
    drf_mixins.CreateModelMixin,
    drf_mixins.RetrieveModelMixin,
    drf_mixins.ListModelMixin,
    BaseViewSet,
):
    metadata_class = ContentTypeMetadata
    queryset = models.SyncStatus.objects.all()
    serializer_class = SyncStatusSerializer
    filterset_class = SyncStatusFilterSet


class SyncSystemViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = models.SyncSystem.objects.all()
    serializer_class = SyncSystemSerializer

    def _get_model(self, app_label, model_name):
        try:
            content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
        except (ValueError, ObjectDoesNotExist):
            return None
        
        return content_type.model_class()

    @extend_schema(responses=SyncSystemObjectStatusSerializer(many=True), request=None)
    @action(
        detail=True,
        methods=["get"],
        url_path="sync-status",
        renderer_classes=[JSONRenderer],
    )
    def render_system_sync_status(self, request, pk):
        """
        Resolve and render the sync status of all devices
        """
        system = self.get_object()
        sync_events = list(models.SyncStatus.objects.filter(is_latest=True, system__id=system.id))

        objects = []
        for obj in system.object_types.all():
            model = self._get_model(obj.app_label, obj.model)
            objects.extend(list(model.objects.all()))

        results = []
        for obj in objects:
            object_type = f"{obj._meta.app_label}.{obj._meta.model_name}"
            events = [
                event for event in sync_events
                if event.object_id == obj.id and event.object_type.model == obj._meta.model_name
                and event.object_type.app_label == obj._meta.app_label
            ]

            if len(events) > 0:
                results.append(
                    {"object_id": obj.id, "object_type": object_type, "status": events[0].status}
                )
            else:
                results.append({"object_id": obj.id, "object_type": object_type, "status": "not-started"})

        return Response(results)
