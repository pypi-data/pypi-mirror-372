from importlib.metadata import entry_points

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastpluggy.core.dependency import get_view_builder, get_fastpluggy
from fastpluggy.core.plugin.dependency_resolver import PluginDependencyResolver
from fastpluggy.core.widgets.categories.data.debug import DebugView
from fastpluggy.core.view_builer.components.model import ModelView
from fastpluggy.core.view_builer.components.table import TableView

debug_module_router = APIRouter()


@debug_module_router.get("/list_modules_dependencies", response_class=HTMLResponse, name="list_modules_dependencies")
def list_modules_dependencies(
        request: Request,
        view_builder=Depends(get_view_builder),
        fast_pluggy=Depends(get_fastpluggy)
):
    """
    """

    modules_info = fast_pluggy.module_manager.modules
    dependency = PluginDependencyResolver.get_sorted_modules_by_dependency(modules_info)

    return view_builder.generate(
        request,
        widgets=[
            ModelView(
                model=dependency['modules'],
                title="Modules Dependencies"
            ),
            DebugView(data=dependency)
        ]
    )


@debug_module_router.get("/list_modules_package", response_class=HTMLResponse, name="list_modules_package")
def list_modules_package(
        request: Request,
        view_builder=Depends(get_view_builder),
):
    """
    Endpoint to list all plugins declared via entry point group 'fastpluggy.plugins'.
    """
    try:
        eps = entry_points(group="fastpluggy.plugins")
    except TypeError:
        # For Python <3.10 compat (not strictly needed here since you're on 3.10+)
        eps = entry_points().get("fastpluggy.plugins", [])

    data = [{
        "name": ep.name,
        "module": ep.module,
        "attr": ep.attr,
        "value": ep.value,
        "dist": getattr(ep, "dist", None).name if hasattr(ep, "dist") else None,
        "version": getattr(ep, "dist", None).version if hasattr(ep, "dist") else None,
    } for ep in eps]

    return view_builder.generate(
        request,
        widgets=[
            TableView(
                data=data,
                title="Discovered FastPluggy Plugins",
                fields=["name", "module", "attr", "value", "dist", "version"]
            )
        ]
    )
