# plugin.py
from typing import Any, Annotated, Optional

from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.module_base import FastPluggyBaseModule
from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.core.tools.install import is_installed
from fastpluggy.fastpluggy import FastPluggy
from .config import DebugToolsConfig


def get_debug_router():
    from .router import debug_plugin_router
    return debug_plugin_router


class DebugToolsPlugin(FastPluggyBaseModule):
    module_name: str = "debug_tools"

    module_menu_name: str = "Debug Tools"
    module_menu_icon: str = "fas fa-tools"
    module_menu_type: str = "admin"

    module_router: Any = get_debug_router

    module_settings: Optional[Any] = DebugToolsConfig

    def on_load_complete(
            self,
            fast_pluggy: Annotated[FastPluggy, InjectDependency],
            plugin: Annotated["PluginState", InjectDependency],
    ) -> None:
        if not is_installed('pympler'):
            plugin.add_warning("pympler is not installed. Debug tools will not be available.")

        from .widgets.debug.debug_panel import DebugPanelWidget
        GlobalRegistry.extend_globals('list_widget_to_inject', items=[{
            'widget': DebugPanelWidget,
            'position': 0,
            'kwargs': {
                'inject_context': True,
            },
            'tag': '#ROOT#'
        }])
