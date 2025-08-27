import asyncio
import os
from typing import Dict, cast
from ariadne_codegen.client_generators.scalars import ScalarData
from ariadne_codegen.exceptions import MissingConfiguration
from ariadne_codegen.settings import CommentsStrategy
from warnings import warn

from aiware.internal.generators.aiware_graphql import AiwareClientGeneratorSettings, aiware_codegen_client as base_aiware_codegen_client
from aiware.internal.utils import get_package_root
from aiware.tools.config import get_config_dict, get_config_file_path, get_section

from dataclasses import dataclass, fields


@dataclass
class DownstreamAiwareClientGeneratorSettings(AiwareClientGeneratorSettings):
    async_base_client_name: str = "AsyncBaseAiwareGraphQL"
    async_base_client_file_path: str = os.path.abspath(os.path.join(get_package_root(), 
        "graphql/async_client_ref.py"
    ))
    sync_base_client_name: str = "BaseAiwareGraphQL"
    sync_base_client_file_path: str = os.path.abspath(os.path.join(get_package_root(), 
        "graphql/client_ref.py"
    ))
    convert_to_snake_case: bool = False

    def __post_init__(self):
        if not self.remote_schema_url:
            self.remote_schema_url = self.core_graphql_url

        super().__post_init__()


# adapted from ariadne_codegen.config.get_client_settings
def get_settings(section: Dict) -> DownstreamAiwareClientGeneratorSettings:
    """Parse configuration dict and return instance."""
    section = section.copy()
    settings_fields_names = {f.name for f in fields(DownstreamAiwareClientGeneratorSettings)}

    section["plugins"] = [
        "aiware.internal.generators.ariadne_plugin_init.InitPlugin",
        *section.get("plugins", [])
    ]

    try:
        section["scalars"] = {
            "JSONData": ScalarData(
                type_="aiware.common.schemas.JSONData",
                serialize="aiware.common.schemas.serialize_jsondata",
                parse="aiware.common.schemas.parse_jsondata",
            ),
            "DateTime": ScalarData(
                type_="datetime.datetime"
            ),
            **{
                name: ScalarData(
                    type_=data["type"],
                    serialize=data.get("serialize"),
                    parse=data.get("parse"),
                    import_=data.get("import"),
                )
                for name, data in cast(
                    dict[str, dict], section.get("scalars", {})
                ).items()
            },
        }
    except KeyError as exc:
        raise MissingConfiguration(
            "Missing 'type' field for scalar definition"
        ) from exc

    try:
        if "include_comments" in section and isinstance(
            section["include_comments"], bool
        ):
            section["include_comments"] = (
                CommentsStrategy.TIMESTAMP.value
                if section["include_comments"]
                else CommentsStrategy.NONE.value
            )
            options = ", ".join(strategy.value for strategy in CommentsStrategy)
            warn(
                "Support for boolean 'include_comments' value has been deprecated "
                "and will be dropped in future release. "
                f"Instead use one of following options: {options}",
                DeprecationWarning,
                stacklevel=2,
            )

        return DownstreamAiwareClientGeneratorSettings(
            **{
                key: value
                for key, value in section.items()
                if key in settings_fields_names
            }
        )
    except TypeError as exc:
        missing_fields = settings_fields_names.difference(section)
        raise MissingConfiguration(
            f"Missing configuration fields: {', '.join(missing_fields)}"
        ) from exc


async def aiware_codegen_client():
    pyproject_path = get_config_file_path()
    pyproject_config = get_config_dict(pyproject_path.__str__())
    aiware_client_config_section = get_section(pyproject_config, scope_key="client")

    config = get_settings(aiware_client_config_section)

    await base_aiware_codegen_client(config)

def main():
    asyncio.run(aiware_codegen_client())


if __name__ == "__main__":
    main()
