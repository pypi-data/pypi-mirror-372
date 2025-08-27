from fastpluggy.core.config import BaseDatabaseSettings
from typing import Optional


class DebugToolsConfig(BaseDatabaseSettings):
    # Enable/disable the Debug Panel Widget
    show_debug_panel_widget: Optional[bool] = True
    
    # Additional debug panel widget configuration options
    debug_panel_max_depth: Optional[int] = 10
    debug_panel_show_attributes: Optional[bool] = True
    debug_panel_show_warnings: Optional[bool] = True
    debug_panel_show_context: Optional[bool] = True
    debug_panel_auto_expand: Optional[bool] = False