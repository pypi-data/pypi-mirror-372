from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import views
from .models import SyncSystem

urlpatterns = (
    path("sync-object/<str:type>/<int:pk>/", views.ObjectSyncView.as_view(), name="sync_object"),
    path("sync-events/", views.SyncStatusListView.as_view(), name="syncstatus_list"),
    path("sync-systems/", views.SyncSystemListView.as_view(), name="syncsystem_list"),
    path("sync-systems/add/", views.SyncSystemEditView.as_view(), name="syncsystem_add"),
    path("sync-systems/<int:pk>/", views.SyncSystemView.as_view(), name="syncsystem"),
    path("sync-systems/<int:pk>/edit/", views.SyncSystemEditView.as_view(), name="syncsystem_edit"),
    path("sync-systems/<int:pk>/delete/", views.SyncSystemDeleteView.as_view(), name="syncsystem_delete"),
    path("sync-systems/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="syncsystem_changelog", kwargs={
        "model": SyncSystem
    }),
)