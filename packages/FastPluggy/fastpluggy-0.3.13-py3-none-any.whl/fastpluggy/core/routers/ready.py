from fastapi import APIRouter, Request, Depends
from starlette.responses import JSONResponse

from fastpluggy.core.dependency import get_fastpluggy
from fastpluggy.core.tools.system import trigger_reload

ready_router = APIRouter()


@ready_router.get("/ready", response_class=JSONResponse)
def fast_pluggy_ready(request: Request, fast_pluggy=Depends(get_fastpluggy)):
    """
    Readiness probe for Fast-Pluggy: returns 200 when fully initialized,
    503 otherwise.
    """
    if fast_pluggy.is_ready:
        # trigger reload if needed
        plugins_dir = fast_pluggy.get_folder_by_module_type('plugin')
        trigger_reload(plugins_dir)
        return JSONResponse(status_code=200, content={"status": "ready"})
    return JSONResponse(status_code=503, content={"status": "not_ready"})