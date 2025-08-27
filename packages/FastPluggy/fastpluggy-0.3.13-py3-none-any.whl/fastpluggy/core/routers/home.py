from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from fastpluggy.core.dependency import get_templates, get_fastpluggy
from fastpluggy.core.tools.system import trigger_reload

home_router = APIRouter()


@home_router.get("/", response_class=HTMLResponse)
def fast_pluggy_home(request: Request, templates=Depends(get_templates)):
    """
    Home page route that renders the index.html.j2 template.
    """
    from fastpluggy.fastpluggy import FastPluggy

    fp_widget_admin_home = FastPluggy.get_global('fp_widgets',{}).get('admin_home',None)

    return templates.TemplateResponse("index.html.j2", {
        "request": request,
        "fp_widget_admin_home":fp_widget_admin_home
    })
