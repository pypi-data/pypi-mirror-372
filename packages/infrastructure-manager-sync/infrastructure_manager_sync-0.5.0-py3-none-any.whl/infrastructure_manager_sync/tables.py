import django_tables2 as tables
from django_tables2.utils import Accessor

from netbox.tables import NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin
from .models import (
    InfrastructureManagerSync,
    InfrastructureManagerSyncVMInfo,
    InfrastructureManagerSyncHostInfo,
)


class InfrastructureManagerSyncTable(NetBoxTable):
    name = tables.Column(linkify=True)

    enabled = columns.BooleanColumn()
    assign_by_default_to_cluster_tenant = columns.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = InfrastructureManagerSync
        fields = (
            "pk",
            "id",
            "name",
            "fqdn",
            "cluster_tenant",
            "entry_type",
            "primary_site",
            "enabled",
            "build_number",
            "version",
            "last_successful_sync",
            "update_prio",
            "assign_by_default_to_cluster_tenant"
        )
        default_columns = (
            "name",
            "fqdn",
            "cluster_tenant",
            "enabled",
            "entry_type",
            "primary_site",
            "build_number",
            "version",
            "last_successful_sync",
            "update_prio",
        )


class InfrastructureManagerSyncVMInfoTable(NetBoxTable):
    vm = tables.Column(linkify=True)

    ims = tables.Column(linkify=True)

    vm_tenant_name = tables.Column(
        accessor=Accessor('vm__tenant__name'),
        linkify=True,
        verbose_name='Tenant'
    )

    vm_cluster_name = tables.Column(
        accessor=Accessor('vm__cluster__name'),
        linkify=True,
        verbose_name='Cluster'
    )

    class Meta(NetBoxTable.Meta):
        model = InfrastructureManagerSyncVMInfo
        fields = (
            "id",
            "vm",
            "environment",
            "criticality",
            "financial_info",
            "licensing",
            "owner",
            "backup_plan",
            "backup_type",
            "service_info",
            "ims",
            "backup_status",
            "last_backup",
            "deployed_on",
            "deployed_by",
            "billing_reference",
            "vm_tenant_name",
            "vm_cluster_name",
            "vmware_tools_version",
            "vm_hardware_compatibility"
        )
        default_columns = (
            "id",
            "vm",
            "environment",
            "criticality",
            "financial_info",
            "owner",
            "ims",
            "vm_tenant_name",
            "vm_cluster_name"
        )


class InfrastructureManagerSyncHostInfoTable(NetBoxTable):
    host = tables.Column(linkify=True)

    ims = tables.Column(linkify=True)

    device_tenant_name = tables.Column(
        accessor=Accessor('host__tenant__name'),
        linkify=True,
        verbose_name='Tenant'
    )

    device_cluster_name = tables.Column(
        accessor=Accessor('host__cluster__name'),
        linkify=True,
        verbose_name='Cluster'
    )

    class Meta(NetBoxTable.Meta):
        model = InfrastructureManagerSyncHostInfo
        fields = (
            "id",
            "host",
            "ims",
            "memory",
            "build_number",
            "physical_cpu_count",
            "core_per_cpu",
            "cpu_type",
            "device_tenant_name",
            "device_cluster_name"
        )
        default_columns = (
            "id",
            "host",
            "ims",
            "build_number",
            "memory",
            "physical_cpu_count",
            "core_per_cpu",
            "cpu_type",
            "device_tenant_name",
            "device_cluster_name"
        )
