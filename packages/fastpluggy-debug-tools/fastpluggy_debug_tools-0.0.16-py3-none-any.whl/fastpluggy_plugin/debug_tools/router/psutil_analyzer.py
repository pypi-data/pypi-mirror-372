from fastapi import APIRouter, Request, Depends
from fastpluggy.core.auth import require_authentication
from fastpluggy.core.dependency import get_view_builder, get_fastpluggy
from fastpluggy.core.widgets import ButtonListWidget, AutoLinkWidget

from ..widgets.psutil_analyzer import PsutilAnalyzerWidget

# Create router with authentication
psutil_analyzer_router = APIRouter(
    prefix="/psutil-analyzer",
    tags=["debug", "psutil"],
    dependencies=[Depends(require_authentication)],
)

@psutil_analyzer_router.get("/", name="psutil_analyzer_dashboard")
async def psutil_analyzer_dashboard(
    request: Request,
    view_builder=Depends(get_view_builder),
    fast_pluggy=Depends(get_fastpluggy)
):
    """
    Render the PSUtil Analyzer dashboard using the custom widget.
    """
    # Register the widget if not already registered
    #available_widgets = fast_pluggy.get_global('available_widget', {})
    #if PsutilAnalyzerWidget.widget_type not in available_widgets:
    #    from fastpluggy_plugin.website_builder.src.widgets import get_class_path
    #    available_widgets[PsutilAnalyzerWidget.widget_type] = get_class_path(PsutilAnalyzerWidget)
    #    fast_pluggy.set_global('available_widget', available_widgets)
    
    # Generate the view with the PSUtil Analyzer widget
    return view_builder.generate(
        request,
        title="PSUtil Memory Analysis Dashboard",
        widgets=[
            PsutilAnalyzerWidget(
                title="PSUtil Memory Analysis Dashboard"
            ),
            ButtonListWidget(buttons=[
                AutoLinkWidget(label="Back to Debug Tools", route_name="list_tools"),
            ]),
        ]
    )