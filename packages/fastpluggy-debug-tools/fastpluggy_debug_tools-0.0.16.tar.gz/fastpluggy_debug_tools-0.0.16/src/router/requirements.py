from fastapi import Depends, APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from ..requirements_tools import get_requirements_files, get_installed_packages, \
    check_multiple_requirements_files
from fastpluggy.core.dependency import get_view_builder, get_fastpluggy
from fastpluggy.core.widgets.categories.data.debug import DebugView
from ..widgets.packages_view import PackagesView

requirements_router = APIRouter()


@requirements_router.get("/list_requirements", response_class=HTMLResponse, name="list_requirements")
def list_requirements(
        request: Request,
        view_builder=Depends(get_view_builder),
        fast_pluggy=Depends(get_fastpluggy)
):
    list_requirements = get_requirements_files(fast_pluggy.module_manager.modules)
    installed_packages = get_installed_packages()
    missing_packages = check_multiple_requirements_files(list_requirements)
    widgets = [
        DebugView(
            title="Missing Requirements",
            data=missing_packages,
        ),
        DebugView(
            title="Requirements Files",
            data=list_requirements, collapsed=True
        ),
        PackagesView(
            packages=installed_packages,
            title="Installed Packages",
            collapsed=False
        )
    ]
    return view_builder.generate(
        request,
        title="Python Packages",
        widgets=widgets
    )
