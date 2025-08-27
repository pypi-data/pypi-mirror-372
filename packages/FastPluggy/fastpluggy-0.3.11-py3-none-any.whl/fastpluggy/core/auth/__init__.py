# core/dependency.py
from fastapi import Request, HTTPException, Depends
from starlette import status
from starlette.authentication import UnauthenticatedUser


async def require_authentication(request: Request):
    auth_manager = request.app.state.fastpluggy.auth_manager
    if auth_manager:
        if isinstance(request.user, UnauthenticatedUser):
            # If a custom error handler is defined, call it.
            if hasattr(auth_manager, "on_authenticate_error") and callable(auth_manager.on_authenticate_error):
                result = await auth_manager.on_authenticate_error(request)
                if result is not None:
                    return result

            # Fallback to default behavior if no custom error handling was provided.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        return request.user


def require_role(role: str):
    async def dependency(request: Request):
        # your `require_authentication` should already have populated request.user & request.auth
        # (e.g. via an AuthenticationMiddleware + your backend)
        auth_manager = request.app.state.fastpluggy.auth_manager
        if auth_manager:
            scopes = getattr(request.auth, "scopes", [])
            if role not in scopes:
                raise HTTPException(status_code=403, detail=f"'{role}' role required")
    return Depends(dependency)