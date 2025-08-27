from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet


class SyncType(ChoiceSet):
    CHOICES = [
        ("vcenter", "VMWare vCenter", "blue"),
    ]


class CriticalityChoise(ChoiceSet):
    CHOICES = [
        ("low", "Low", "white"),
        ("medium", "Medium", "yellow"),
        ("DR", "Disaster Recovery", "blue"),
        ("high", "High", "red"),
    ]


class EnvironmentChoise(ChoiceSet):
    CHOICES = [
        ("acceptance", "Acceptance", "white"),
        ("test", "Test", "yellow"),
        ("demo", "Demo", "blue"),
        ("production", "Production", "red"),
    ]


class FinancialInfoChoise(ChoiceSet):

    STATUS_NON_BILLABLE = "non-billable"
    STATUS_BILLABLE = "billable"

    CHOICES = [
        (STATUS_NON_BILLABLE, "Non Billable", "yellow"),
        (STATUS_BILLABLE, "Billable", "blue"),
        ("billable-by-service", "Billable by Service (DEPRECATED)", "white"),
        ("billable x2", "Billable X2 (DEPRECATED)", "red"),
    ]


class LicensingChoise(ChoiceSet):
    CHOICES = [
        ("win-desktop", "Windows Desktop", "white"),
        ("other", "Other (linux)", "yellow"),
        ("ms-sql", "Microsoft SQL", "blue"),
        ("win-server", "Windows Server", "red"),
    ]


class ServiceInfoChoise(ChoiceSet):

    STATUS_PAY_PER_USE = "pay-per-use"
    STATUS_OFFSHARE = "offshare"
    STATUS_EVISION = "evision"
    STATUS_BACKUP = "backup"
    STATUS_MONITORING = "monitoring"
    STATUS_CITRIX = "citrix"
    SERVICE_INFO = "internal-it"

    CHOICES = [
        (STATUS_PAY_PER_USE, "Pay Per Use", "yellow"),
        (STATUS_OFFSHARE, "Offshare", "green"),
        (STATUS_EVISION, "e-Vision", "blue"),
        (STATUS_BACKUP, "Backup", "orange"),
        (STATUS_MONITORING, "Monitoring", "red"),
        (STATUS_CITRIX, "Citrix", "white"),
        (SERVICE_INFO, "Internal IT", "purple"),
        ("customer-services", "Customer Services (DEPRECATED)", "white"),
        ("shared-services", "Shared Services (DEPRECATED)", "yellow"),
    ]


class UpdatePrioChoise(ChoiceSet):

    PRIO_NORMAL = "normal"
    PRIO_HIGH = "high"

    CHOICES = [(PRIO_NORMAL, "Normal Update Prio", "yellow"), (PRIO_HIGH, "High Update Prio", "orange")]


class InfrastructureManagerSync(NetBoxModel):
    name = models.CharField(max_length=100)
    fqdn = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100, default="ChangeMe")
    last_successful_sync = models.DateTimeField(
        auto_now=False, auto_now_add=False, blank=True, default=None, null=True
    )
    update_prio = models.CharField(max_length=30, choices=UpdatePrioChoise, default=UpdatePrioChoise.PRIO_NORMAL)

    cluster_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="infrastructuremanagersync",
        blank=True,
        null=True,
    )

    primary_site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.PROTECT,
        related_name="infrastructuremanagersync_sync",
        blank=True,
        null=True,
    )

    entry_type = models.CharField(max_length=30, choices=SyncType, blank=True)

    enabled = models.BooleanField(
        default=True,
        verbose_name="Enabled",
        help_text=_("Enable so the info from this entry is synced"),
    )

    comments = models.TextField(blank=True)

    build_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Filled in by the script, do not edit manualy"),
    )
    version = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Filled in by the script, do not edit manualy"),
    )

    assign_by_default_to_cluster_tenant = models.BooleanField(
        default=False,
        help_text=_("Assign VM's without tenant tag automatically to the Cluster tenant"),
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "plugins:infrastructure_manager_sync:infrastructuremanagersync",
            args=[self.pk],
        )


class InfrastructureManagerSyncHostInfo(NetBoxModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A copy of the PK to be used by __str__ in case the object is deleted
        self._pk = self.pk

    ims = models.ForeignKey(
        to="InfrastructureManagerSync",
        on_delete=models.CASCADE,
        related_name="InfrastructureManagerSyncHost",
        null=True,
    )

    host = models.OneToOneField(
        to="dcim.device",
        on_delete=models.CASCADE,
        related_name="InfrastructureManagerSyncHostInfo",
        blank=False,
    )

    physical_cpu_count = models.PositiveIntegerField(blank=True, null=True)
    core_per_cpu = models.PositiveIntegerField(blank=True, null=True)
    cpu_type = models.CharField(max_length=100, blank=True)

    build_number = models.CharField(max_length=100, blank=True)

    memory = models.PositiveIntegerField(blank=True, null=True, verbose_name="Memory (MB)")

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        pk = self.pk or self._pk
        return f"#{pk}"

    def get_absolute_url(self):
        return reverse(
            "plugins:infrastructure_manager_sync:infrastructuremanagersynchostinfo",
            args=[self.pk],
        )


class InfrastructureManagerSyncVMInfo(NetBoxModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A copy of the PK to be used by __str__ in case the object is deleted
        self._pk = self.pk

    vm = models.OneToOneField(
        to="virtualization.VirtualMachine",
        on_delete=models.CASCADE,
        related_name="InfrastructureManagerSyncVMInfo",
        blank=False,
    )

    ims = models.ForeignKey(
        to="InfrastructureManagerSync",
        on_delete=models.CASCADE,
        related_name="InfrastructureManagerSync",
        null=True,
    )

    backup_plan = models.CharField(max_length=100, blank=True)

    backup_type = models.CharField(max_length=100, blank=True)

    criticality = models.CharField(max_length=30, choices=CriticalityChoise, blank=True)

    environment = models.CharField(max_length=30, choices=EnvironmentChoise, blank=True)

    financial_info = models.CharField(max_length=30, choices=FinancialInfoChoise, blank=True)

    licensing = models.CharField(max_length=30, choices=LicensingChoise, blank=True)

    owner = models.CharField(max_length=100, blank=True)

    service_info = models.CharField(max_length=30, choices=ServiceInfoChoise, blank=True)

    billing_reference = models.CharField(max_length=100, blank=True)

    deployed_by = models.CharField(max_length=100, blank=True)

    deployed_on = models.DateField(blank=True, null=True)

    last_backup = models.DateTimeField(blank=True, null=True)

    backup_status = models.CharField(max_length=200, blank=True)

    vmware_tools_version = models.CharField(max_length=25, blank=True)

    vm_hardware_compatibility = models.CharField(max_length=25, blank=True)

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        pk = self.pk or self._pk
        return f"#{pk}"

    def get_absolute_url(self):
        return reverse(
            "plugins:infrastructure_manager_sync:infrastructuremanagersyncvminfo",
            args=[self.pk],
        )
