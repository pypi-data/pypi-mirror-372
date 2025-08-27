from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class CurrentUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Obtain a DB session; in production you might want a better scoped session

        from fastpluggy.fastpluggy import FastPluggy

        # Retrieve the FastPluggy instance (assuming it's stored in app.state)
        fast_pluggy: FastPluggy = request.app.state.fastpluggy
        try:
            # Use the current auth manager to authenticate the user
            if fast_pluggy.auth_manager:
                user = await fast_pluggy.auth_manager.authenticate(request)
            else:
                user = None
        except Exception as e:
            logger.exception(e)
            user = None
        # Attach the user to request.state
        request.state.current_user = user[1] if user else None
        request.state.roles = user[0] if user else None
        if hasattr(fast_pluggy.auth_manager, 'get_user_menu_entries'):
            request.state.user_menu = fast_pluggy.auth_manager.get_user_menu_entries(request)
        else:
            request.state.user_menu = []
        response = await call_next(request)
        return response
