import asyncio
import pkgutil

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from fastpluggy.core.dependency import get_view_builder, get_module_manager
from fastpluggy.core.widgets import TableWidget

task_thread_tools_router = APIRouter()

# ── your application’s own prefixes ──────────────────────────────────────────
# Adjust these two to match your real code’s top‐level package names.
USER_PREFIXES = ["fastpluggy", "fastpluggy_plugin"]

def gather_top_level_packages() -> set[str]:
    """
    Scan sys.path once and return all importable top-level module/package names.
    """
    return {info.name for info in pkgutil.iter_modules()}


ALL_PACKAGES = gather_top_level_packages()

@task_thread_tools_router.get(
    "/list_tasks",
    response_class=HTMLResponse,
    name="list_all_tasks"
)
async def list_all_tasks(
    request: Request,
    view_builder=Depends(get_view_builder),
        module_manager = Depends(get_module_manager)
):
    """
    Endpoint to list all running asyncio.Tasks in the current event loop.
    """

    for item in module_manager.modules.values():
        if item.package_name:
            USER_PREFIXES.append(item.package_name)

    clean_user_prefixes = list(set(USER_PREFIXES))

    # 1. Grab every Task in the loop
    all_tasks = asyncio.all_tasks()
    user_rows = []
    system_rows = []

    for t in all_tasks:
        coro = t.get_coro()

        # 1) Try to grab the module from the live frame, if still running:
        module_name = ""
        if hasattr(coro, "cr_frame") and coro.cr_frame is not None:
            module_name = coro.cr_frame.f_globals.get("__name__", "")
        else:
            # 2) If the coroutine is already finished, fallback to __module__ or empty
            module_name = getattr(coro, "__module__", "") or ""

        # Extract just the top‐level prefix (e.g. "uvicorn", "starlette", "myapp"):
        top_level = module_name.split(".", 1)[0] if module_name else ""

        # Prepare a common row format
        entry = {
            "coro_name": coro.__qualname__,
            "module":    module_name,
            "top_level": top_level,
            "done":      t.done(),
            "cancelled": t.cancelled(),
            "repr":      repr(coro),
        }

        if top_level in clean_user_prefixes:
            user_rows.append(entry)
        else:
            system_rows.append(entry)

    return view_builder.generate(
        request,
        widgets=[
            TableWidget(
                data=user_rows,
                title=(
                    "User‐Defined Asyncio Tasks "
                    f"(top_level ∈ {sorted(clean_user_prefixes)})"
                )
            ),
            TableWidget(
                data=system_rows,
                title="System/Library Asyncio Tasks"
            )
        ]
    )
