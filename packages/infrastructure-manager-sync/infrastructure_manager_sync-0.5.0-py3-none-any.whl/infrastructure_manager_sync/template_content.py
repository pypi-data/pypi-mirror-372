import logging
from netbox.plugins import PluginTemplateExtension
from . import models


class InfrastructureManagerSyncVMInfoView(PluginTemplateExtension):
    models = ["virtualization.virtualmachine"]

    def left_page(self):
        try:
            imsvm = models.InfrastructureManagerSyncVMInfo.objects.get(vm__id=self.context["object"].id)
        except models.InfrastructureManagerSyncVMInfo.DoesNotExist:
            imsvm = None
            return ""

        return self.render(
            "infrastructure_manager_sync/inc/vm_info.html",
            extra_context={
                "imsvm": imsvm,
            },
        )


class InfrastructureManagerSyncHostInfoView(PluginTemplateExtension):
    models = ["dcim.device"]

    def left_page(self):
        try:
            imsvm = models.InfrastructureManagerSyncHostInfo.objects.get(host__id=self.context["object"].id)

        except models.InfrastructureManagerSyncHostInfo.DoesNotExist:
            imsvm = None
            return ""

        return self.render(
            "infrastructure_manager_sync/inc/host_info.html",
            extra_context={"imshost": imsvm},
        )


template_extensions = [
    InfrastructureManagerSyncVMInfoView,
    InfrastructureManagerSyncHostInfoView,
]
