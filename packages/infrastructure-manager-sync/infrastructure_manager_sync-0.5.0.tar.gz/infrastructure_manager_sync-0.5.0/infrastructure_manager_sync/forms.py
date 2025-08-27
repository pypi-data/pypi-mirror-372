from django import forms

from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, TagFilterField, DynamicModelMultipleChoiceField
from .models import (
    CriticalityChoise,
    EnvironmentChoise,
    FinancialInfoChoise,
    InfrastructureManagerSync,
    InfrastructureManagerSyncVMInfo,
    LicensingChoise,
    SyncType,
    UpdatePrioChoise,
    InfrastructureManagerSyncHostInfo,
)
from utilities.forms.widgets import DatePicker, DateTimePicker
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from django.utils.translation import gettext as _
from tenancy.models import Tenant
from virtualization.models import Cluster
from utilities.forms.rendering import FieldSet

class InfrastructureManagerSyncForm(NetBoxModelForm):
    comments = CommentField()

    assign_by_default_to_cluster_tenant = forms.BooleanField(
        label=("Assign untagged vms to cluster tenant"),
        required=False,
        initial=False,
        help_text=_("Assign VMs without tenant tag automatically to the Cluster tenant"),
    )

    class Meta:
        model = InfrastructureManagerSync
        fields = (
            "name",
            "fqdn",
            "username",
            "password",
            "cluster_tenant",
            "entry_type",
            "primary_site",
            "enabled",
            "update_prio",
            "assign_by_default_to_cluster_tenant",
            "comments",
            "tags",
        )


class InfrastructureManagerSyncFilterForm(NetBoxModelFilterSetForm):
    model = InfrastructureManagerSync

    entry_type = forms.MultipleChoiceField(choices=SyncType, required=False)
    update_prio = forms.MultipleChoiceField(choices=UpdatePrioChoise, required=False)

    assign_by_default_to_cluster_tenant = forms.NullBooleanField(
        required=False, label=_("Assign default tenant"), widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES)
    )

    tag = TagFilterField(model)


class InfrastructureManagerSyncVMInfoSyncForm(NetBoxModelForm):
    class Meta:
        model = InfrastructureManagerSyncVMInfo
        fields = (
            "vm",
            "backup_plan",
            "backup_type",
            "criticality",
            "environment",
            "financial_info",
            "licensing",
            "owner",
            "service_info",
            "backup_status",
            "last_backup",
            "deployed_on",
            "deployed_by",
            "billing_reference",
            "ims",
            "vmware_tools_version",
            "vm_hardware_compatibility"
        )
        widgets = {
            "deployed_on": DatePicker(),
            "last_backup": DateTimePicker(),
        }


class InfrastructureManagerSyncVMInfoFilterForm(NetBoxModelFilterSetForm):
    model = InfrastructureManagerSyncVMInfo

    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('environment', 'criticality', 'financial_info', 'licensing', 'ims', 'owner', name=_('Attributes')),
        FieldSet('tenant_id', name=_('Tenant')),
        FieldSet('cluster_id', name=_('Cluster')),
    )

    environment = forms.MultipleChoiceField(choices=EnvironmentChoise, required=False)
    criticality = forms.MultipleChoiceField(choices=CriticalityChoise, required=False)
    financial_info = forms.MultipleChoiceField(choices=FinancialInfoChoise, required=False)
    licensing = forms.MultipleChoiceField(choices=LicensingChoise, required=False)

    ims = forms.ModelChoiceField(
        queryset=InfrastructureManagerSync.objects.all(),
        required=False,
        label=_('ims'),
    )

    owner = forms.CharField(max_length=100, required=False)

    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_('Tenants')
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Clusters')
    )


class InfrastructureManagerSyncHostInfoSyncForm(NetBoxModelForm):
    class Meta:
        model = InfrastructureManagerSyncHostInfo
        fields = ("host", "build_number")


class InfrastructureManagerSyncHostInfoFilterForm(NetBoxModelFilterSetForm):
    model = InfrastructureManagerSyncHostInfo

    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('tenant_id', name=_('Tenant')),
        FieldSet('cluster_id', name=_('Cluster')),
    )

    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_('Tenants')
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Clusters')
    )
