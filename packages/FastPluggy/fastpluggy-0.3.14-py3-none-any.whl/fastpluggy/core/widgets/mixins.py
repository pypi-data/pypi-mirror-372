from typing import Any

from starlette.requests import Request


class RequestParamsMixin:
    """
    Mixin that provides helpers around `self.request`,
    such as fetching typed query parameters.
    """
    request: Request | None = None

    def get_query_param(self, param: str, default: Any = None, param_type: type = str):
        """
        Helper method to get query parameters from request.
        """
        if not self.request or not self.request.query_params:
            return default

        value = self.request.query_params.get(param, default)
        if value != default and param_type != str:
            try:
                return param_type(value)
            except (ValueError, TypeError):
                return default
        return value
