from fastapi import Depends, APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from fastpluggy.core.database import get_engine
from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.view_builer.components.model import ModelView
from fastpluggy.core.widgets.categories.data.debug import DebugView


# Create a FastAPI router for pool inspection
pool_router = APIRouter(prefix="/pool", tags=["pool"])


@pool_router.get(
    "/info",
    response_class=HTMLResponse,
    name="pool_info"
)
def pool_info_html(
    request: Request,
    view_builder=Depends(get_view_builder),
    engine=Depends(get_engine)
):
    """
    Renders detailed SQLAlchemy connection pool information as an HTML page.
    """
    pool = engine.pool

    # Gather key metrics
    metrics = {
        "checked_out": pool.checkedout(),  # connections currently in use
        "pool_size": pool.size(),          # configured max size
        "overflow": pool.overflow(),       # connections opened beyond pool_size
        "status": pool.status(),           # human-readable status
    }

    # Access internal connections for deep debugging (use with caution)
    raw_pool = []
    if hasattr(pool, "_pool"):
        try:
            inner_queue = pool._pool
            # queue.Queue uses .queue attr to store widgets
            if hasattr(inner_queue, "queue"):
                raw_pool = list(inner_queue.queue)
        except Exception:
            raw_pool = []

    # Render via fastpluggy's view builder
    return view_builder.generate(
        request,
        widgets=[
            ModelView(model=metrics, title="Connection Pool Metrics"),
            DebugView(data={
                "raw_pool_connections": len(raw_pool),
                "raw_pool": raw_pool
            })
        ]
    )
