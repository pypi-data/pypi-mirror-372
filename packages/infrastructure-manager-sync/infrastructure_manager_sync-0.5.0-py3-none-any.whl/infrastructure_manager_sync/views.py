from netbox.views import generic
from . import forms, models, tables
from .filtersets import (
    InfrastructureManagerSyncFilterSet,
    InfrastructureManagerSyncVMInfoFilterSet,
    InfrastructureManagerSyncHostInfoFilterSet,
)
from utilities.views import ViewTab, register_model_view
from netbox.plugins import PluginTemplateExtension


class InfrastructureManagerSyncListView(generic.ObjectListView):
    permission_required = "infrastructure_manager_sync.view_infrastructuremanagersync"
    queryset = models.InfrastructureManagerSync.objects.all()
    table = tables.InfrastructureManagerSyncTable
    filterset = InfrastructureManagerSyncFilterSet
    filterset_form = forms.InfrastructureManagerSyncFilterForm


class InfrastructureManagerSyncEditView(generic.ObjectEditView):
    permission_required = [
        "infrastructure_manager_sync.change_infrastructuremanagersync",
        "infrastructuremanagersync.add_infrastructuremanagersync",
    ]
    queryset = models.InfrastructureManagerSync.objects.all()
    form = forms.InfrastructureManagerSyncForm


class InfrastructureManagerSyncView(generic.ObjectView):
    permission_required = "infrastructure_manager_sync.view_infrastructuremanagersync"
    queryset = models.InfrastructureManagerSync.objects.all()


class InfrastructureManagerSyncDeleteView(generic.ObjectDeleteView):
    permission_required = "infrastructure_manager_sync.delete_infrastructuremanagersync"
    queryset = models.InfrastructureManagerSync.objects.all()


class InfrastructureManagerSyncVMInfoListView(generic.ObjectListView):
    permission_required = "infrastructure_manager_sync.view_infrastructuremanagersyncvminfo"
    queryset = models.InfrastructureManagerSyncVMInfo.objects.all()
    table = tables.InfrastructureManagerSyncVMInfoTable
    filterset = InfrastructureManagerSyncVMInfoFilterSet
    filterset_form = forms.InfrastructureManagerSyncVMInfoFilterForm


class InfrastructureManagerSyncVMInfoEditView(generic.ObjectEditView):
    permission_required = [
        "infrastructure_manager_sync.change_infrastructuremanagersyncvminfo",
        "infrastructuremanagersync.add_infrastructuremanagersyncvminfo",
    ]
    queryset = models.InfrastructureManagerSyncVMInfo.objects.all()
    form = forms.InfrastructureManagerSyncVMInfoSyncForm


class InfrastructureManagerSyncVMInfoView(generic.ObjectView):
    permission_required = "infrastructure_manager_sync.view_infrastructuremanagersyncvminfo"
    queryset = models.InfrastructureManagerSyncVMInfo.objects.all()


class InfrastructureManagerSyncVMInfoDeleteView(generic.ObjectDeleteView):
    permission_required = "infrastructure_manager_sync.delete_infrastructuremanagersyncvminfo"
    queryset = models.InfrastructureManagerSyncVMInfo.objects.all()


class InfrastructureManagerSyncHostInfoListView(generic.ObjectListView):
    permission_required = "infrastructure_manager_sync.view_infrastructuremanagersynchostinfo"
    queryset = models.InfrastructureManagerSyncHostInfo.objects.all()
    table = tables.InfrastructureManagerSyncHostInfoTable
    filterset = InfrastructureManagerSyncHostInfoFilterSet
    filterset_form = forms.InfrastructureManagerSyncHostInfoFilterForm


class InfrastructureManagerSyncHostInfoEditView(generic.ObjectEditView):
    permission_required = [
        "infrastructure_manager_sync.change_infrastructuremanagersynchostinfo",
        "infrastructuremanagersync.add_infrastructuremanagersynchostinfo",
    ]
    queryset = models.InfrastructureManagerSyncHostInfo.objects.all()
    form = forms.InfrastructureManagerSyncHostInfoSyncForm


class InfrastructureManagerSyncHostInfoView(generic.ObjectView):
    permission_required = "infrastructure_manager_sync.view_infrastructuremanagersynchostinfo"
    queryset = models.InfrastructureManagerSyncHostInfo.objects.all()


class InfrastructureManagerSyncHostInfoDeleteView(generic.ObjectDeleteView):
    permission_required = "infrastructure_manager_sync.delete_infrastructuremanagersynchostinfo"
    queryset = models.InfrastructureManagerSyncHostInfo.objects.all()
