from abc import abstractmethod
from typing import Type

from fastapi import Request
from starlette.authentication import BaseUser, AuthenticationBackend, AuthCredentials
from starlette.requests import HTTPConnection


class AuthInterface(AuthenticationBackend):

    async def on_authenticate_error(self, request: Request):
        """
        Handle authentication errors when a user fails to authenticate.

        This method is invoked when authentication fails (e.g., due to missing or invalid credentials).
        It examines the request's 'Accept' header and, if the client expects HTML and login redirection is enabled,
        returns a redirect response to the login page. Otherwise, it raises an HTTP 401 Unauthorized exception with
        a WWW-Authenticate header, which can trigger the browser's Basic Authentication popup.

        Args:
            request (Request): The incoming FastAPI request object containing details such as headers.

        Returns:
            A RedirectResponse if HTML is accepted and redirection is enabled. If not, this method raises an
            HTTPException and does not return normally.

        Raises:
            HTTPException: Raised with status code 401 if authentication fails and the client does not accept HTML,
            prompting the Basic Auth dialog.
        """
        pass

    @property
    @abstractmethod
    def user_model(self) -> Type[BaseUser]:
        """
        Returns the SQLAlchemy model class representing a user.
        Implementations can override this property to use a different model.
        """
        pass

    @abstractmethod
    async def authenticate(self, conn: HTTPConnection) -> tuple[AuthCredentials, BaseUser] | None:
        """
        Check if the user is authenticated.
        Should return a User object if authenticated.
        Otherwise, it can either raise an HTTPException or return a Response (e.g. a redirect).
        """
        pass

    def get_user_menu_entries(self, request: Request) -> list:
        """
        Returns menu items for the user dropdown based on whether a user is logged in.
            If a user is logged in, the menu is obtained from the FastPluggy menu manager (using the "user" menu).
            Otherwise, a default login entry is returned.

        Each menu item should be a dictionary containing keys such as:
            - "name": the display text
            - "icon": (optional) an icon class
            - "url": the destination URL


            """
        # Check if a user is attached to request.state (set by middleware)
        user = getattr(request.state, "current_user", None)
        if user:
            from fastpluggy.fastpluggy import FastPluggy

            # Retrieve the menu manager from the app state.
            fast_pluggy: FastPluggy = request.app.state.fastpluggy

            menu_manager = fast_pluggy.menu_manager
            # Try to get the "user" menu from the manager.
            user_menu = menu_manager.get_menu("user")
            return user_menu
        else:
            # If no user is logged in, return a default login entry.
            return [{'router': {"name": "Login", "icon": "fa-solid fa-sign-in-alt", "url": "/login"}}]
