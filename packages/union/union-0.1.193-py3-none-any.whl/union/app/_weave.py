from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._models import AppConfigProtocol, AppSerializationSettings, Link

if TYPE_CHECKING:
    from ._models import App


@dataclass
class WeaveConfig(AppConfigProtocol):
    project: str
    entity: str
    api_host: str = "https://api.wandb.ai"
    host: str = "https://wandb.ai"

    def before_to_union_idl(self, app: "App", settings: AppSerializationSettings):
        """Modify app in place at the beginning of `App._to_union_idl`."""
        app.env["WANDB_BASE_URL"] = self.api_host
        app.env["WANDB_PROJECT"] = self.project

        weave_url = f"{self.host.rstrip('/')}/{self.entity}/{self.project}/weave/traces"

        link = Link(path=weave_url, title="Weave Traces")
        app.links.append(link)
