from netbox.plugins import PluginMenuButton, PluginMenuItem

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_sync_status:syncsystem_list",
        link_text="Sync Systems",
        buttons=[
            PluginMenuButton(
                link="plugins:netbox_sync_status:syncsystem_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
            )
        ]
    ),
)