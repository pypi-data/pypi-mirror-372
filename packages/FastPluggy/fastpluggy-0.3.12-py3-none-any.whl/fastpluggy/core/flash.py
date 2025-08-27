from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class FlashMessageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Initialize the flash messages container on request.state if it doesn't exist
        if not hasattr(request.state, "flash_messages"):
            request.state.flash_messages = request.session.get("flash_messages", [])

        response = await call_next(request)

        # Clear flash messages after they are used
        if hasattr(request.state, "flash_messages") and request.state.flash_messages:
            # Store flash messages in session before clearing for the next request
            request.session["flash_messages"] = request.state.flash_messages
            request.state.flash_messages = []  # Clear after use

        return response


class FlashMessage:

    def __init__(self, message, category='info', exception=None):
        self.message = message
        self.category = category
        self.exception = exception

    def to_dict(self):
        return {
            "message": self.message,
            "category": self.category,
            "exception": self.exception.__dict__ if isinstance(self.exception, Exception) else None,
        }

    @staticmethod
    def add(request: Request, message: str, category: str = "info", exception=None):
        if not hasattr(request.state, "flash_messages"):
            request.state.flash_messages = []

        flash = FlashMessage(message, category, exception)
        request.state.flash_messages.append(flash.to_dict())
        return flash

    @staticmethod
    def get_flash_messages(request: Request):
        flash_messages = request.state.flash_messages if hasattr(request.state, "flash_messages") else []
        # Clear the messages from the session after they are accessed
        request.session.pop("flash_messages", None)
        request.state.flash_messages = []  # Clear after use
        return flash_messages
