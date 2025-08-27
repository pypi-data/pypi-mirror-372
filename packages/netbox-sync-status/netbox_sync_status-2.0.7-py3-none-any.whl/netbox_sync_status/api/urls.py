from django.urls import path
from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_sync_status"

router = NetBoxRouter()
router.register("sync-events", views.SyncStatusViewSet)
router.register("sync-systems", views.SyncSystemViewSet)

urlpatterns = router.urls + [
    path(
        "sync-object/<str:obj_type>/<int:pk>/",
        views.ObjectSyncView.as_view(),
        name="sync-object",
    ),
]
