from functools import cached_property
from pathlib import Path
from string import Template
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

TEMPLATE = Template(
    'project_name = __project_name__ = distribution_name = __distribution_name__ = "${name}"\n',
)


class ProjectNameBuildHook(BuildHookInterface):
    PLUGIN_NAME = "project-name"

    @cached_property
    def config_name_file(
        self,
    ) -> str:
        name_file = self.config.get("name-file")
        if not name_file:
            msg = f"Option `name-file` for build hook `{self.PLUGIN_NAME}` is required"
            raise ValueError(msg)
        if not isinstance(name_file, str):
            msg = f"Option `name-file` for build hook `{self.PLUGIN_NAME}` must be a string"
            raise TypeError(msg)
        return name_file

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, Any],
    ) -> None:  # pragma: no cover
        name: str = self.metadata.name
        content = TEMPLATE.substitute(
            name=name,
        )
        target_path = Path(self.root) / self.config_name_file
        target_path.write_text(
            content,
            encoding="utf-8",
        )
        build_data["artifacts"].append(
            self.config_name_file,
        )
