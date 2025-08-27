from fastapi import Depends, APIRouter
from fastapi.routing import APIRoute
from starlette.requests import Request

from fastpluggy.core.dependency import get_view_builder, get_fastpluggy
from fastpluggy.core.widgets.categories.data.debug import DebugView

menu_debug_router = APIRouter()

@menu_debug_router.get("/list_menu")
async def list_menu(
        request: Request,
        view_builder=Depends(get_view_builder),
        fast_pluggy=Depends(get_fastpluggy)):

    return view_builder.generate(
        request,
        title="List menu",
        widgets=[
            DebugView(
                data=fast_pluggy.menu_manager.menus,
            )
        ]
    )


@menu_debug_router.get("/list_menu_entry")
async def list_menu_entry(
        request: Request,
        view_builder=Depends(get_view_builder),
        fast_pluggy=Depends(get_fastpluggy)):
    app_routes = fast_pluggy.app.router.routes
    list_entry = []
    for route in app_routes:
        if isinstance(route, APIRoute) and hasattr(route.endpoint, "_menu_entry"):
            menu_entry = route.endpoint._menu_entry
            list_entry.append(menu_entry)

    return view_builder.generate(
        request,
        title="List _menu_entry",
        widgets=[
            DebugView(
                data=list_entry,
            )
        ]
    )

