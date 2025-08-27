# src/plugins/debug_plugin/router.py

import os
import sys

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute

from fastpluggy.core.auth import require_authentication
from fastpluggy.core.database import Base
from fastpluggy.core.dependency import get_view_builder, get_fastpluggy
from fastpluggy.core.tools.fastapi import _extract_route_metadata
from fastpluggy.core.tools.install import is_installed
from fastpluggy.core.widgets.render_field_tools import RenderFieldTools
from fastpluggy.core.view_builer.components.table import TableView
from fastpluggy.core.widgets import TableWidget
from fastpluggy.core.widgets.categories.data.debug import DebugView
from fastpluggy.core.widgets.categories.input.button import AutoLinkWidget
from fastpluggy.core.widgets.categories.input.button_list import ButtonListWidget
from .menu_tools import menu_debug_router
from .module_tools import debug_module_router
from .pool_info import pool_router
from .psutil_analyzer import psutil_analyzer_router
from .requirements import requirements_router
from .task_thread_tools import task_thread_tools_router
from ..router.websocket_tool import websocket_notification_button

debug_plugin_router = APIRouter()
debug_plugin_router.include_router(menu_debug_router)
debug_plugin_router.include_router(debug_module_router)
debug_plugin_router.include_router(pool_router)
debug_plugin_router.include_router(psutil_analyzer_router)
debug_plugin_router.include_router(requirements_router)
debug_plugin_router.include_router(task_thread_tools_router)

if is_installed('pympler'):
    from .memory_tools import menu_memory_router
    debug_plugin_router.include_router(menu_memory_router)


@debug_plugin_router.get("/", response_class=HTMLResponse)
def list_tools(
        request: Request,
        view_builder=Depends(get_view_builder)
):
    """
    Main debug tools page listing available debug functions as buttons.
    """
    return view_builder.generate(
        request,
        widgets=[
            ButtonListWidget(
                buttons=[
                    AutoLinkWidget(route_name="list_tables", label="List Database Tables"),
                    AutoLinkWidget(route_name="list_env_vars", label="List Environment Variables"),
                    AutoLinkWidget(route_name="route_no_auth", label="List routes (with no auth,conflict)"),
                    AutoLinkWidget(route_name="list_session"),
                    AutoLinkWidget(route_name="pool_info"),
                    AutoLinkWidget(route_name="list_jinja2_templates", label="List Jinja2 Templates"),
                ]
            ),
            ButtonListWidget(
                title="Menu & Menu Entry",
                buttons=[
                    AutoLinkWidget(route_name="list_menu", label="List menu"),
                    AutoLinkWidget(route_name="list_menu_entry", label="List _menu_entry "),
                ],
            ),
            ButtonListWidget(
                title="Modules",
                buttons=[
                    AutoLinkWidget(route_name="list_modules_dependencies", label="Modules Dependencies"),
                    AutoLinkWidget(route_name="list_requirements", label="Python Packages"),
                    AutoLinkWidget(route_name="list_modules_package", label="Modules installed as package"),
                ],
            ),
            ButtonListWidget(
                title="WebSocket",
                buttons=[websocket_notification_button(request=request)],
            ),
            ButtonListWidget(
                buttons=[
                    AutoLinkWidget(route_name="list_global_registry"),
                ]
            ),
            ButtonListWidget(
                title="Threads & Coroutines",
                buttons=[
                    AutoLinkWidget(route_name="list_all_tasks"),
                    AutoLinkWidget(route_name="psutil_analyzer_dashboard", label="PSUtil Memory Analyzer"),
                ]
            ),
        ]
    )


@debug_plugin_router.get("/list_tables", response_class=HTMLResponse, name="list_tables")
def list_tables(
        request: Request,
        view_builder=Depends(get_view_builder)
):
    """
    Endpoint to list all database tables.
    """
    data = [{"table_name": table} for table in Base.metadata.tables.keys()]
    return view_builder.generate(
        request,
        widgets=[
            TableWidget(
                data=data,
                title="Database Tables"
            )
        ]
    )


@debug_plugin_router.get("/list_modules", response_class=HTMLResponse, name="list_modules")
def list_modules(
        request: Request,
        view_builder=Depends(get_view_builder)
):
    """
    Endpoint to list all loaded Python modules.
    """
    modules_info = [
        {
            "module_name": name,
            "file_path": getattr(module, "__file__", "N/A"),
            "package": getattr(module, "__package__", "N/A"),
            "built_in": "yes" if name in sys.builtin_module_names else "no",
        }
        for name, module in sys.modules.items()
    ]
    return view_builder.generate(
        request,
        widgets=[
            TableView(
                data=modules_info,
                title="Loaded Modules"
            )
        ]
    )


@debug_plugin_router.get("/list_env_vars", response_class=HTMLResponse, name="list_env_vars")
def list_env_vars(
        request: Request,
        view_builder=Depends(get_view_builder)
):
    """
    Endpoint to list all environment variables.
    """
    env_vars = [{"key": key, "value": value} for key, value in os.environ.items()]
    return view_builder.generate(
        request,
        widgets=[
            TableView(
                data=env_vars,
                title="Environment Variables"
            )
        ]
    )


def have_auth(router):
    if router and hasattr(router, 'dependencies'):
        for dep in router.dependencies:
            if dep.dependency == require_authentication:
                return True
    return False


@debug_plugin_router.get("/route_no_auth")
async def route_no_auth(
        request: Request,
        view_builder=Depends(get_view_builder),
        fast_pluggy=Depends(get_fastpluggy),
):
    """
    List routes of the application, including authentication check and conflict detection.
    """
    seen_routes = {}
    route_items = []

    for route in fast_pluggy.app.routes:
        if not isinstance(route, APIRoute):
            continue

        metadata = _extract_route_metadata(route)
        metadata["auth_required"] = have_auth(route)  # You already use this
        metadata["conflict"] = False  # Default to no conflict

        # Check for conflicts: same path + method
        for method in metadata["methods"]:
            key = f"{metadata['path']}::{method}"
            if key in seen_routes:
                seen_routes[key]["conflict"] = True
                metadata["conflict"] = True
            else:
                seen_routes[key] = metadata

        route_items.append(metadata)

    return view_builder.generate(
        request,
        title="Routes without Auth + Conflict Detection",
        widgets=[
            TableView(
                data=route_items,
                field_callbacks={
                    "path": lambda v: f"<code>{v}</code>",
                    "methods": RenderFieldTools.render_http_verb_badges,
                    "auth_required": lambda v: "✅" if v else "❌",
                    "conflict": lambda v: "⚠️ Conflict" if v else "—",
                },
                fields=["name", "path", "methods", "auth_required", "conflict"]
            )
        ]
    )


@debug_plugin_router.get("/list_session")
async def list_session(
        request: Request,
        view_builder=Depends(get_view_builder)):
    return view_builder.generate(
        request,
        title="List session",
        widgets=[
            DebugView(
                data=request.session,
            )
        ]
    )


@debug_plugin_router.get("/list_global_registry")
async def list_global_registry(
        request: Request,
        view_builder=Depends(get_view_builder)):
    from fastpluggy.fastpluggy import FastPluggy
    return view_builder.generate(
        request,
        title="List global registry",
        widgets=[
            DebugView(
                data=FastPluggy.get_all_globals(),
            )
        ]
    )


@debug_plugin_router.get("/list_jinja2_templates")
async def list_jinja2_templates(
        request: Request,
        view_builder=Depends(get_view_builder),
        fast_pluggy=Depends(get_fastpluggy)):
    """
    List all Jinja2 templates registered in the application.
    """
    templates = fast_pluggy.templates.env.list_templates()
    templates_data = [{"template_path": template} for template in templates]

    return view_builder.generate(
        request,
        title="Registered Jinja2 Templates",
        widgets=[
            TableView(
                data=templates_data,
                title="Jinja2 Templates"
            )
        ]
    )
