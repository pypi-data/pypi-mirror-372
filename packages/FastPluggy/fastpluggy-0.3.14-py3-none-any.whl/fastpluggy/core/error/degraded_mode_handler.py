# fastpluggy/core/degraded_mode_handler.py

import traceback
from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, PackageLoader


class DegradedModeHandler:
    def __init__(self, exception: Exception):
        self.exception = exception
        self.templates = Jinja2Templates(
            env=Environment(
                loader=PackageLoader("fastpluggy", "templates")
            )
        )

    @property
    def error_type(self) -> str:
        return type(self.exception).__name__

    @property
    def error_message(self) -> str:
        return str(self.exception)

    @property
    def traceback(self) -> str:
        return "".join(traceback.format_exception(type(self.exception), self.exception, self.exception.__traceback__))

    @property
    def suggestions(self) -> list[str]:
        msg = self.error_message.lower()
        if "no such table" in msg:
            return ["Run database migrations to create missing tables."]
        elif "configuration file" in msg:
            return ["Verify the presence of the configuration file and its format."]
        else:
            return ["Check the application logs for more details."]

    def get_router(self) -> APIRouter:
        fallback_router = APIRouter()

        @fallback_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], response_class=HTMLResponse)
        async def fallback_handler(request: Request):
            return self.templates.TemplateResponse(
                "degraded_mode.html.j2",
                {
                    "request": request,
                    "handler": self,
                },
                status_code=503,
            )

        return fallback_router
