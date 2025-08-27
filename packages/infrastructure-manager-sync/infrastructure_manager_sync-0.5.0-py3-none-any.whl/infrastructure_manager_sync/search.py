from netbox.search import SearchIndex, register_search
from .models import InfrastructureManagerSync, InfrastructureManagerSyncVMInfo, InfrastructureManagerSyncHostInfo


@register_search
class InfrastructureManagerSyncIndex(SearchIndex):
    model = InfrastructureManagerSync
    fields = (
        ("name", 100),
        ("fqdn", 200),
    )


@register_search
class InfrastructureManagerSyncVMInfoIndex(SearchIndex):
    model = InfrastructureManagerSyncVMInfo
    fields = (
        ("backup_plan", 200),
        ("criticality", 300),
        ("environment", 400),
        ("financial_info", 500),
        ("licensing", 600),
        ("owner", 700),
    )


@register_search
class InfrastructureManagerSyncHostInfoIndex(SearchIndex):
    model = InfrastructureManagerSyncHostInfo
    fields = (("build_number", 200),)
