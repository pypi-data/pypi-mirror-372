from django.urls import path

from netbox.views.generic import ObjectChangeLogView
from . import models, views


urlpatterns = (
    path(
        "infrastructure-manager-sync-lists/",
        views.InfrastructureManagerSyncListView.as_view(),
        name="infrastructuremanagersync_list",
    ),
    path(
        "infrastructure-manager-sync-lists/add/",
        views.InfrastructureManagerSyncEditView.as_view(),
        name="infrastructuremanagersync_add",
    ),
    path(
        "infrastructure-manager-sync-lists/<int:pk>/",
        views.InfrastructureManagerSyncView.as_view(),
        name="infrastructuremanagersync",
    ),
    path(
        "infrastructure-manager-sync-lists/<int:pk>/edit/",
        views.InfrastructureManagerSyncEditView.as_view(),
        name="infrastructuremanagersync_edit",
    ),
    path(
        "infrastructure-manager-sync-lists/<int:pk>/delete/",
        views.InfrastructureManagerSyncDeleteView.as_view(),
        name="infrastructuremanagersync_delete",
    ),
    path(
        "infrastructure-manager-sync-lists/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="infrastructuremanagersync_changelog",
        kwargs={"model": models.InfrastructureManagerSync},
    ),
    path(
        "infrastructure-manager-sync-vm-lists/",
        views.InfrastructureManagerSyncVMInfoListView.as_view(),
        name="infrastructuremanagersyncvminfo_list",
    ),
    path(
        "infrastructure-manager-sync-vm-lists/add/",
        views.InfrastructureManagerSyncVMInfoEditView.as_view(),
        name="infrastructuremanagersyncvminfo_add",
    ),
    path(
        "infrastructure-manager-sync-vm-lists/<int:pk>/",
        views.InfrastructureManagerSyncVMInfoView.as_view(),
        name="infrastructuremanagersyncvminfo",
    ),
    path(
        "infrastructure-manager-sync-vm-lists/<int:pk>/edit/",
        views.InfrastructureManagerSyncVMInfoEditView.as_view(),
        name="infrastructuremanagersyncvminfo_edit",
    ),
    path(
        "infrastructure-manager-sync-vm-lists/<int:pk>/delete/",
        views.InfrastructureManagerSyncVMInfoDeleteView.as_view(),
        name="infrastructuremanagersyncvminfo_delete",
    ),
    path(
        "infrastructure-manager-sync-vm-lists/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="infrastructuremanagersyncvminfo_changelog",
        kwargs={"model": models.InfrastructureManagerSyncVMInfo},
    ),
    path(
        "infrastructure-manager-sync-host-lists/",
        views.InfrastructureManagerSyncHostInfoListView.as_view(),
        name="infrastructuremanagersynchostinfo_list",
    ),
    path(
        "infrastructure-manager-sync-host-lists/add/",
        views.InfrastructureManagerSyncHostInfoEditView.as_view(),
        name="infrastructuremanagersynchostinfo_add",
    ),
    path(
        "infrastructure-manager-sync-host-lists/<int:pk>/",
        views.InfrastructureManagerSyncHostInfoView.as_view(),
        name="infrastructuremanagersynchostinfo",
    ),
    path(
        "infrastructure-manager-sync-host-lists/<int:pk>/edit/",
        views.InfrastructureManagerSyncHostInfoEditView.as_view(),
        name="infrastructuremanagersynchostinfo_edit",
    ),
    path(
        "infrastructure-manager-sync-host-lists/<int:pk>/delete/",
        views.InfrastructureManagerSyncHostInfoDeleteView.as_view(),
        name="infrastructuremanagersynchostinfo_delete",
    ),
    path(
        "infrastructure-manager-sync-host-lists/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="infrastructuremanagersynchostinfo_changelog",
        kwargs={"model": models.InfrastructureManagerSyncHostInfo},
    ),
)
