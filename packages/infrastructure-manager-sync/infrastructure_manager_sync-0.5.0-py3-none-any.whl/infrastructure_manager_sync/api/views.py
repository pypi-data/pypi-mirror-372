from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import (
    InfrastructureManagerSyncSerializer,
    InfrastructureManagerSyncVMInfoSerializer,
    InfrastructureManagerSyncHostInfoSerializer,
)


class InfrastructureManagerSyncViewSet(NetBoxModelViewSet):
    # permission_required = 'netbox_vcenter_tag_sync.view_vcenters' #TODO
    queryset = models.InfrastructureManagerSync.objects.all()
    serializer_class = InfrastructureManagerSyncSerializer


class InfrastructureManagerSyncVMInfoViewSet(NetBoxModelViewSet):
    # permission_required = 'netbox_vcenter_tag_sync.view_vcenters' #TODO
    queryset = models.InfrastructureManagerSyncVMInfo.objects.all()
    serializer_class = InfrastructureManagerSyncVMInfoSerializer


class InfrastructureManagerSyncHostInfoViewSet(NetBoxModelViewSet):
    # permission_required = 'netbox_vcenter_tag_sync.view_vcenters' #TODO
    queryset = models.InfrastructureManagerSyncHostInfo.objects.all()
    serializer_class = InfrastructureManagerSyncHostInfoSerializer
