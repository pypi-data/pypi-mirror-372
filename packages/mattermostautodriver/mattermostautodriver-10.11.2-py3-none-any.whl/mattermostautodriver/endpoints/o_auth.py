from ._base import Base
from typing import Any, BinaryIO

__all__ = ["OAuth"]


class OAuth(Base):

    def create_o_auth_app(
        self,
        name: str,
        description: str,
        callback_urls: list[str],
        homepage: str,
        icon_url: str | None = None,
        is_trusted: bool | None = None,
    ):
        """Register OAuth app

        name: The name of the client application
        description: A short description of the application
        icon_url: A URL to an icon to display with the application
        callback_urls: A list of callback URLs for the appliation
        homepage: A link to the website of the application
        is_trusted: Set this to ``true`` to skip asking users for permission

        `Read in Mattermost API docs (o_auth - CreateOAuthApp) <https://developers.mattermost.com/api-documentation/#/operations/CreateOAuthApp>`_

        """
        __options = {
            "name": name,
            "description": description,
            "icon_url": icon_url,
            "callback_urls": callback_urls,
            "homepage": homepage,
            "is_trusted": is_trusted,
        }
        return self.client.post("""/api/v4/oauth/apps""", options=__options)

    def get_o_auth_apps(self, page: int | None = 0, per_page: int | None = 60):
        """Get OAuth apps

        page: The page to select.
        per_page: The number of apps per page.

        `Read in Mattermost API docs (o_auth - GetOAuthApps) <https://developers.mattermost.com/api-documentation/#/operations/GetOAuthApps>`_

        """
        __params = {"page": page, "per_page": per_page}
        return self.client.get("""/api/v4/oauth/apps""", params=__params)

    def get_o_auth_app(self, app_id: str):
        """Get an OAuth app

        app_id: Application client id

        `Read in Mattermost API docs (o_auth - GetOAuthApp) <https://developers.mattermost.com/api-documentation/#/operations/GetOAuthApp>`_

        """
        return self.client.get(f"/api/v4/oauth/apps/{app_id}")

    def update_o_auth_app(
        self,
        app_id: str,
        id: str,
        name: str,
        description: str,
        callback_urls: list[str],
        homepage: str,
        icon_url: str | None = None,
        is_trusted: bool | None = None,
    ):
        """Update an OAuth app

        app_id: Application client id
        id: The id of the client application
        name: The name of the client application
        description: A short description of the application
        icon_url: A URL to an icon to display with the application
        callback_urls: A list of callback URLs for the appliation
        homepage: A link to the website of the application
        is_trusted: Set this to ``true`` to skip asking users for permission. It will be set to false if value is not provided.

        `Read in Mattermost API docs (o_auth - UpdateOAuthApp) <https://developers.mattermost.com/api-documentation/#/operations/UpdateOAuthApp>`_

        """
        __options = {
            "id": id,
            "name": name,
            "description": description,
            "icon_url": icon_url,
            "callback_urls": callback_urls,
            "homepage": homepage,
            "is_trusted": is_trusted,
        }
        return self.client.put(f"/api/v4/oauth/apps/{app_id}", options=__options)

    def delete_o_auth_app(self, app_id: str):
        """Delete an OAuth app

        app_id: Application client id

        `Read in Mattermost API docs (o_auth - DeleteOAuthApp) <https://developers.mattermost.com/api-documentation/#/operations/DeleteOAuthApp>`_

        """
        return self.client.delete(f"/api/v4/oauth/apps/{app_id}")

    def regenerate_o_auth_app_secret(self, app_id: str):
        """Regenerate OAuth app secret

        app_id: Application client id

        `Read in Mattermost API docs (o_auth - RegenerateOAuthAppSecret) <https://developers.mattermost.com/api-documentation/#/operations/RegenerateOAuthAppSecret>`_

        """
        return self.client.post(f"/api/v4/oauth/apps/{app_id}/regen_secret")

    def get_o_auth_app_info(self, app_id: str):
        """Get info on an OAuth app

        app_id: Application client id

        `Read in Mattermost API docs (o_auth - GetOAuthAppInfo) <https://developers.mattermost.com/api-documentation/#/operations/GetOAuthAppInfo>`_

        """
        return self.client.get(f"/api/v4/oauth/apps/{app_id}/info")

    def get_authorized_o_auth_apps_for_user(self, user_id: str, page: int | None = 0, per_page: int | None = 60):
        """Get authorized OAuth apps

        user_id: User GUID
        page: The page to select.
        per_page: The number of apps per page.

        `Read in Mattermost API docs (o_auth - GetAuthorizedOAuthAppsForUser) <https://developers.mattermost.com/api-documentation/#/operations/GetAuthorizedOAuthAppsForUser>`_

        """
        __params = {"page": page, "per_page": per_page}
        return self.client.get(f"/api/v4/users/{user_id}/oauth/apps/authorized", params=__params)
