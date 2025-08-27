from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

ims_buttons = [
    PluginMenuButton(
        link="plugins:infrastructure_manager_sync:infrastructuremanagersync_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    )
]

imsvm_buttons = [
    PluginMenuButton(
        link="plugins:infrastructure_manager_sync:infrastructuremanagersyncvminfo_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    )
]

imshost_buttons = [
    PluginMenuButton(
        link="plugins:infrastructure_manager_sync:infrastructuremanagersynchostinfo_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    )
]


menu = PluginMenu(
    label="Infra Manager Sync",
    icon_class="mdi mdi-sync",
    groups=(
        (
            "IMS",
            (
                PluginMenuItem(
                    link="plugins:infrastructure_manager_sync:infrastructuremanagersync_list",
                    link_text="IMS Lists",
                    buttons=ims_buttons,
                ),
                PluginMenuItem(
                    link="plugins:infrastructure_manager_sync:infrastructuremanagersyncvminfo_list",
                    link_text="IMS VM Lists",
                    buttons=imsvm_buttons,
                ),
                PluginMenuItem(
                    link="plugins:infrastructure_manager_sync:infrastructuremanagersynchostinfo_list",
                    link_text="IMS Host Lists",
                    buttons=imshost_buttons,
                ),
            ),
        ),
    ),
)
