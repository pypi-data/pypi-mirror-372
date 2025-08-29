import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._models import AppConfigProtocol, AppSerializationSettings, Link

if TYPE_CHECKING:
    from ._models import App

logger = logging.getLogger(__name__)


@dataclass
class ArizeConfig(AppConfigProtocol):
    endpoint: str  # <host>/organizations/<org_id>/spaces/<space_id>/models[/<model_id>]

    def before_to_union_idl(self, app: "App", settings: AppSerializationSettings):
        """Modify app in place at the beginning of `App._to_union_idl`."""

        link = Link(path=self.endpoint, title="Arize Traces")
        app.links.append(link)


@dataclass
class PhoenixConfig(AppConfigProtocol):
    endpoint: str  # <host> or <host>/s/<space_id>
    project: str  # name of the project

    def before_to_union_idl(self, app: "App", settings: AppSerializationSettings):
        """Modify app in place at the beginning of `App._to_union_idl`."""
        app.env["PHOENIX_COLLECTOR_ENDPOINT"] = self.endpoint
        app.env["PHOENIX_PROJECT_NAME"] = self.project

        try:
            from phoenix.client import Client
        except ImportError:
            logger.warning(
                "Missing Phoenix client. "
                "You can install it with `pip install arize-phoenix-client`. Skipping link generation."
            )
            return

        api_key = os.environ.get("PHOENIX_API_KEY")
        if not api_key:
            logger.warning("PHOENIX_API_KEY not found locally. Skipping link generation.")
            return

        os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={api_key}"

        try:
            client = Client(base_url=self.endpoint)

            # Get list of projects and map names to IDs
            projects = client.projects.list()
            project_name_to_id = {p["name"]: p["id"] for p in projects}

            # Check if the project exists
            if self.project in project_name_to_id:
                project_id = project_name_to_id[self.project]
            else:
                logger.warning(f"Project does not exist: {self.project}. Creating project.")
                client.projects.create(name=self.project)

                # Retrieve the project ID after creation
                project = client.projects.get(project_name=self.project)
                project_id = project.get("id")

                if not project_id:
                    logger.warning(f"Failed to retrieve project ID for: {self.project}")
                    return

            phoenix_link = f"{self.endpoint.rstrip('/')}/projects/{project_id}/spans"
            link = Link(path=phoenix_link, title="Phoenix Traces")
            app.links.append(link)

        except Exception as e:
            logger.warning(f"Failed to generate Phoenix link: {e}")
