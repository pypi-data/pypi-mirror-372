from core.events import OBJECT_UPDATED
from django.apps import apps
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import View
from extras.events import enqueue_event
from netbox.context import events_queue
from netbox.views import generic
from utilities.views import GetReturnURLMixin

from netbox_sync_status.filtersets import SyncStatusFilterForm, SyncStatusFilterSet

from .forms import SyncSystemForm
from .models import SyncStatus, SyncSystem
from .tables import SyncStatusListTable, SyncSystemListTable


class SyncSystemView(generic.ObjectView):
    queryset = SyncSystem.objects.all()


class SyncSystemListView(generic.ObjectListView):
    queryset = SyncSystem.objects.all()
    table = SyncSystemListTable


class SyncSystemEditView(generic.ObjectEditView):
    queryset = SyncSystem.objects.all()
    form = SyncSystemForm


class SyncSystemDeleteView(generic.ObjectDeleteView):
    queryset = SyncSystem.objects.all()
    filterset = SyncStatusFilterSet


class SyncStatusListView(generic.ObjectListView):
    queryset = SyncStatus.objects.order_by("-id")
    filterset = SyncStatusFilterSet
    filterset_form = SyncStatusFilterForm
    table = SyncStatusListTable


class ObjectSyncView(GetReturnURLMixin, View):
    def post(self, request, **kwargs):
        obj_type = kwargs.get("type")
        if not obj_type or "." not in obj_type:
            messages.error(request, "Invalid object type")
            return redirect(self.get_return_url(request))

        app_label, model_name = obj_type.split(".")
        self.queryset = apps.get_model(app_label, model_name).objects
        selected_objects = self.queryset.filter(
            pk=kwargs.get("pk"),
        )

        for obj in selected_objects:
            obj.snapshot()
            queue = events_queue.get()
            enqueue_event(queue, obj, request.user, request.id, OBJECT_UPDATED)
            events_queue.set(queue)

        messages.success(request, f"Manual sync started for {str(obj)}")
        return redirect(self.get_return_url(request))
