from netbox.api.routers import NetBoxRouter
from . import views


app_name = "infrastructure_manager_sync"

router = NetBoxRouter()
router.register("infrastructuremanagersync", views.InfrastructureManagerSyncViewSet)
router.register("infrastructuremanagersyncvminfo", views.InfrastructureManagerSyncVMInfoViewSet)
router.register("infrastructuremanagersynchostinfo", views.InfrastructureManagerSyncHostInfoViewSet)

urlpatterns = router.urls
