import logging
from typing import Dict, Any, List

from fastapi import APIRouter, Request
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette import status
from starlette.responses import RedirectResponse
from starlette.routing import WebSocketRoute


def _extract_route_metadata(route) -> Dict[str, Any]:
    """Extract metadata from a route, including parameter types and default.

    Args:
        route: The route to inspect (APIRoute or WebSocketRoute).

    Returns:
        Dict[str, Any]: A dictionary containing route metadata:
            - name (str): The route name
            - path (str): The route path
            - methods (List[str]): HTTP methods supported by the route or ["websocket"] for WebSocket routes
            - path_params (List[Dict[str, str]]): List of path parameter names,types,default
            - query_params (List[Dict[str, str]]): List of query parameter names,types,default
            - body_params (List[Dict[str, str]]): List of body parameter names,types,default
    """
    def param_info(param) -> Dict[str, Any]:
        return {
            "name": param.name,
            "type": param.type_.__name__ if hasattr(param.type_, '__name__') else str(param.type_),
            "default": param.default if param.default != ... else None  # Ellipsis means required
        }

    # Handle WebSocketRoute
    if isinstance(route, WebSocketRoute):
        return {
            "name": route.name,
            "path": route.path,
            "methods": ["websocket"],  # Use "websocket" as the method for WebSocket routes
            "path_params": [],  # WebSocketRoute doesn't have dependant attribute
            "query_params": [],
            "body_params": [],
        }

    # Handle APIRoute
    return {
        "name": route.name,
        "path": route.path,
        "methods": [method.lower() for method in route.methods],
        "path_params": [param_info(param) for param in route.dependant.path_params],
        "query_params": [param_info(param) for param in route.dependant.query_params],
        "body_params": [param_info(param) for param in route.dependant.body_params],
    }



def inspect_fastapi_route(app: FastAPI, route_name: str) -> Dict[str, Any]:
    """Inspect a specific FastAPI route to determine its HTTP method and parameters.

    Args:
        app (FastAPI): The FastAPI application instance.
        route_name (str): The name of the route to inspect.

    Returns:
        Dict[str, Any]: A dictionary containing route metadata including:
            - name (str): The route name
            - path (str): The route path
            - methods (List[str]): Lowercase HTTP methods supported by the route
            - path_params (List[str]): Names of path parameters
            - query_params (List[str]): Names of query parameters
            - body_params (List[str]): Names of request body parameters

    Raises:
        ValueError: If the route is not found or no HTTP methods are defined.
    """
    route = next(
        (r for r in app.routes if isinstance(r, APIRoute) and r.name == route_name),
        None
    )
    if not route:
        raise ValueError(f"Route '{route_name}' not found in the application.")
    return _extract_route_metadata(route)


def list_router_routes(router: APIRouter) -> List[Dict[str, Any]]:
    """Inspect all routes of an APIRouter to determine their HTTP methods, paths, and parameters.

    Args:
        router (APIRouter): The FastAPI APIRouter instance.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing route metadata for each route, including:
            - name (str): The route name
            - path (str): The route path
            - methods (List[str]): Lowercase HTTP methods supported by the route or ["websocket"] for WebSocket routes
            - path_params (List[str]): Names of path parameters
            - query_params (List[str]): Names of query parameters
            - body_params (List[str]): Names of request body parameters
    """
    routes_metadata: List[Dict[str, Any]] = []

    if hasattr(router, 'routes'):
        for route in router.routes:
            if not isinstance(route, (APIRoute, WebSocketRoute)):
                continue

            try:
                metadata = _extract_route_metadata(route)
                routes_metadata.append(metadata)
            except Exception as e:
                logging.warning(f"Failed to extract metadata for route {getattr(route, 'path', 'unknown')}: {e}")
    else:
        logging.warning(f"Router {router} does not have routes attribute (type): {type(router)}")
    return routes_metadata


def redirect_to_previous(request: Request, endpoint_name: str = 'fast_pluggy_home') -> RedirectResponse:
    """Redirect to the previous page based on the 'Referer' header.

    Args:
        request (Request): The incoming request object.

    Returns:
        RedirectResponse: A response that redirects to the previous page or a default page if 'referer' is not present.

    Raises:
        ValueError: If neither 'referer' nor any other method can be used to determine the redirect.
    """
    referer = request.headers.get("referer")

    if referer:
        # Redirect to the previous page
        return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    else:
        # Fallback: Redirect to a default page if 'referer' is not available
        url = request.url_for(endpoint_name)
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
