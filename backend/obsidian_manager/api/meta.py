"""Build metadata endpoint.

GET /meta → {version, commit, build_date}
"""

from fastapi import APIRouter
from pydantic import BaseModel

from .._buildinfo import get_build_info

router = APIRouter()


class BuildInfo(BaseModel):
    version: str
    commit: str
    build_date: str | None = None


@router.get("/meta", response_model=BuildInfo)
def meta() -> BuildInfo:
    return BuildInfo(**get_build_info())
