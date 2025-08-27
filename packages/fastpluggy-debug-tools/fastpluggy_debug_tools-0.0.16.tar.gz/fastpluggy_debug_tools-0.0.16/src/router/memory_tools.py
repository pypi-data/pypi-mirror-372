from typing import List

import psutil
from fastapi import Query
from pydantic import BaseModel
from pympler import muppy, summary


from fastapi import APIRouter


menu_memory_router = APIRouter()

class MemTypeStat(BaseModel):
    type: str
    count: int
    size_bytes: float
    size_percent: float

class MemModuleStat(BaseModel):
    module: str
    count: int
    size_bytes: float
    size_percent: float

class MemOverview(BaseModel):
    total_objects: int
    total_size_bytes: float
    process_rss_bytes: int
    stats_by_type: List[MemTypeStat]
    stats_by_module: List[MemModuleStat]


@menu_memory_router.get("/memory/overview", response_model=MemOverview)
def memory_overview(
    type_limit: int = Query(10, description="Top N types to return"),
    module_limit: int = Query(10, description="Top N modules to return")
):
    # gather live objects
    all_objs = muppy.get_objects()
    # summary by type
    sum_type = summary.summarize(all_objs)
    sum_type.sort(key=lambda row: row[2], reverse=True)
    top_types = sum_type[:type_limit]
    # summary by module
    sum_mod = summary.summarize(all_objs, groupby='module')
    sum_mod.sort(key=lambda row: row[2], reverse=True)
    top_modules = sum_mod[:module_limit]

    # total counts and sizes
    total_objects = len(all_objs)
    total_size = sum(row[2] for row in sum_type)

    # process RSS
    process_rss = psutil.Process().memory_info().rss

    # build response lists
    stats_by_type = [
        MemTypeStat(
            type=row[0], count=row[1], size_bytes=row[2],
            size_percent=(row[2] / total_size * 100 if total_size else 0)
        ) for row in top_types
    ]
    stats_by_module = [
        MemModuleStat(
            module=row[0], count=row[1], size_bytes=row[2],
            size_percent=(row[2] / total_size * 100 if total_size else 0)
        ) for row in top_modules
    ]

    return MemOverview(
        total_objects=total_objects,
        total_size_bytes=total_size,
        process_rss_bytes=process_rss,
        stats_by_type=stats_by_type,
        stats_by_module=stats_by_module,
    )
