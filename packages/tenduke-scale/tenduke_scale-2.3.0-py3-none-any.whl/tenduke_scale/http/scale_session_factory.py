"""HTTP Session factory for the 10Duke Scale SDK."""

import importlib.metadata

from tenduke_core.config import TendukeConfig
from tenduke_core.http import SessionFactory


class ScaleSessionFactory(SessionFactory):
    """Creates HTTP session objects configured for use by the 10Duke Scale SDK."""

    def __init__(self, config: TendukeConfig, app_name: str, app_version: str):
        """Construct an instance of the ScaleSessionFactory."""
        super().__init__(
            config,
            app_name,
            app_version,
            "10Duke Scale SDK for Python",
            importlib.metadata.version("tenduke-scale"),
        )
