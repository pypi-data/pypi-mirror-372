from netbox.plugins import PluginConfig


class InfrastructureManagerSync(PluginConfig):
    name = "infrastructure_manager_sync"
    verbose_name = "Infrastructure Manager Sync"
    description = "Plugin that configures the vcenter import for VM, clusters & hosts"
    version = "0.5"
    base_url = "infrastructure-manager-sync"
    min_version = "3.4.0"


config = InfrastructureManagerSync
