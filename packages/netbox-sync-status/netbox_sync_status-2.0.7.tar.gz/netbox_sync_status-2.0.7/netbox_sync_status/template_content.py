from django.db.models import Q
from netbox.plugins import PluginTemplateExtension

from netbox_sync_status.models import SyncStatus, SyncSystem


class SyncStatusExtension(PluginTemplateExtension):
    excluded_apps = ["netbox_sync_status", "extras"]

    def buttons(self):
        obj = self.context["object"]
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name

        return self.render(
            "netbox_sync_status/sync_status_buttons.html",
            extra_context={
                "render": True if app_label not in self.excluded_apps else False,
                "object_type": f"{app_label}.{model_name}",
                "view_name": f"{app_label}:{model_name}",
            },
        )

    def right_page(self):
        obj = self.context["object"]
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name

        sync_systems = SyncSystem.objects.filter(
            Q(object_types__app_label=app_label) & Q(object_types__model=model_name)
        )
        sync_status = SyncStatus.objects.order_by("system", "-id").filter(
            Q(is_latest=True)
            & Q(object_id=obj.id)
            & Q(object_type__app_label=app_label)
            & Q(object_type__model=model_name)
        )
        items = []
        for system in sync_systems:
            data = {"system": system, "last_event": None}

            events = [
                event for event in sync_status if event.system.name == system.name
            ]
            if len(events) > 0:
                data["last_event"] = events[0]

            items.append(data)

        sync_system = sync_systems.first()
        object_type_id = None
        if sync_system:
            object_type_id = (
                sync_system.object_types.filter(
                    Q(app_label=app_label) & Q(model=model_name)
                )
                .first()
                .id
                or None
            )

        return self.render(
            "netbox_sync_status/sync_status.html",
            extra_context={"sync_systems": items, "object_type_id": object_type_id},
        )


template_extensions = [SyncStatusExtension]
