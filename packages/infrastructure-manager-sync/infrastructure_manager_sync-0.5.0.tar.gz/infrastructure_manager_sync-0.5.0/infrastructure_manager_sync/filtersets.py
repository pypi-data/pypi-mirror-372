import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from .models import (
    InfrastructureManagerSync,
    InfrastructureManagerSyncVMInfo,
    InfrastructureManagerSyncHostInfo,
)
from tenancy.models import Tenant
from virtualization.models import Cluster

class InfrastructureManagerSyncFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = InfrastructureManagerSync
        fields = ("name", "fqdn", "username", "primary_site", "build_number", "version", "enabled", "update_prio")

        assign_by_default_to_cluster_tenant = django_filters.BooleanFilter(
            label="Assigned tenant by default",
        )


class InfrastructureManagerSyncVMInfoFilterSet(NetBoxModelFilterSet):

    tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vm__tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )

    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vm__cluster',
        queryset=Cluster.objects.all(),
        label='Cluster (ID)',
    )


    class Meta:
        model = InfrastructureManagerSyncVMInfo
        fields = (
            "environment",
            "criticality",
            "financial_info",
            "licensing",
            "owner",
            "backup_status",
            "deployed_by",
            "billing_reference",
            "ims",
            "vmware_tools_version",
            "vm_hardware_compatibility"
        )


class InfrastructureManagerSyncHostInfoFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = InfrastructureManagerSyncHostInfo
        fields = ("memory", "build_number")

    tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name='host__tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )

    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name='host__cluster',
        queryset=Cluster.objects.all(),
        label='Cluster (ID)',
    )