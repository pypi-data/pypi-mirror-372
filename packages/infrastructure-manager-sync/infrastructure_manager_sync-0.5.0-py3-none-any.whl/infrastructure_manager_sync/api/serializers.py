from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from ..models import (
    InfrastructureManagerSync,
    InfrastructureManagerSyncVMInfo,
    InfrastructureManagerSyncHostInfo,
)


#
# Regular serializers
#


class InfrastructureManagerSyncSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:infrastructure_manager_sync-api:infrastructuremanagersync-detail"
    )

    class Meta:
        model = InfrastructureManagerSync
        fields = (
            "id",
            "fqdn",
            "name",
            "username",
            "password",
            "cluster_tenant",
            "entry_type",
            "url",
            "primary_site",
            "enabled",
            "build_number",
            "version",
            "last_successful_sync",
            "update_prio",
            "assign_by_default_to_cluster_tenant",
        )


class InfrastructureManagerSyncVMInfoSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:infrastructure_manager_sync-api:infrastructuremanagersyncvminfo-detail"
    )

    class Meta:
        model = InfrastructureManagerSyncVMInfo
        fields = (
            "id",
            "vm",
            "backup_plan",
            "backup_type",
            "criticality",
            "environment",
            "financial_info",
            "licensing",
            "owner",
            "service_info",
            "url",
            "ims",
            "backup_status",
            "last_backup",
            "deployed_on",
            "deployed_by",
            "billing_reference",
            "vmware_tools_version",
            "vm_hardware_compatibility"
        )


class InfrastructureManagerSyncHostInfoSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:infrastructure_manager_sync-api:infrastructuremanagersynchostinfo-detail"
    )

    class Meta:
        model = InfrastructureManagerSyncHostInfo
        fields = (
            "id",
            "host",
            "url",
            "ims",
            "physical_cpu_count",
            "core_per_cpu",
            "cpu_type",
            "build_number",
            "memory",
        )
