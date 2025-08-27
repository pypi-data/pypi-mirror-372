import asyncio
from dataclasses import dataclass
import dataclasses
import os
import ariadne_codegen.config
from ariadne_codegen.client_generators.scalars import ScalarData
from ariadne_codegen.settings import ClientSettings

from aiware.internal.utils import get_package_root

print("PACKAGE ROOT", get_package_root())

@dataclass
class AiwareClientGeneratorSettings(ClientSettings):
    core_graphql_url: str = "https://api.us-1.veritone.com/v3/graphql"
    # client_name: str = "AsyncAiwareGraphQL"
    # client_file_name: str = "client"
    # base_client_name: str = "AsyncAiwareGraphQLForCodegen"
    # base_client_file_path: str = os.path.abspath(os.path.join(get_package_src_root(),
    #     "src/aiware/graphql/async_client_ref.py"
    # ))
    async_client_name: str = "GeneratedAsyncAiwareGraphQL"
    async_client_file_name: str = "async_client"
    async_base_client_file_path: str = os.path.abspath(
                os.path.join(
                    get_package_root(), "graphql/base/async_base_client_ref.py"
                )
            )
    async_base_client_name: str = "AsyncBaseClient"

    sync_client_name: str = "GeneratedAiwareGraphQL"
    sync_client_file_name: str = "client"
    sync_base_client_file_path: str = os.path.abspath(
                os.path.join(
                    get_package_root(), "graphql/base/base_client_ref.py"
                )
            )
    sync_base_client_name: str = "BaseClient"

    include_all_inputs: bool = False
    include_all_enums: bool = False

    convert_to_snake_case: bool = False

    def __post_init__(self):
        if not self.remote_schema_url:
            self.remote_schema_url = self.core_graphql_url

        super().__post_init__()

    def async_client_settings(self):
        return dataclasses.replace(
            self,
            async_client=True,
            client_name=self.async_client_name,
            client_file_name=self.async_client_file_name,
            base_client_file_path=self.async_base_client_file_path,
            base_client_name=self.async_base_client_name
        )

    def sync_client_settings(self):
        return dataclasses.replace(
            self,
            async_client=False,
            client_name=self.sync_client_name,
            client_file_name=self.sync_client_file_name,
            base_client_file_path=self.sync_base_client_file_path,
            base_client_name=self.sync_base_client_name
        )


def get_settings() -> AiwareClientGeneratorSettings:
    return AiwareClientGeneratorSettings(
        core_graphql_url="https://api.us-1.veritone.com/v3/graphql",
        queries_path="src/aiware/graphql/operations",
        target_package_name="client_generated",
        target_package_path="src/aiware/graphql",
        convert_to_snake_case=False,
        include_all_inputs=False,
        include_all_enums=False,
        scalars={
            "JSONData": ScalarData(
                type_="aiware.common.schemas.JSONData",
                parse="aiware.common.schemas.parse_jsondata",
                serialize="aiware.common.schemas.serialize_jsondata",
            ),
            "DateTime": ScalarData(type_="datetime.datetime"),
        },
        plugins=["aiware.internal.generators.ariadne_plugin_init.InitPlugin"],
    )


async def aiware_codegen_client(settings: AiwareClientGeneratorSettings):
    for async_client in [True, False]:
        config = settings.async_client_settings() if async_client else settings.sync_client_settings()

        # monkey patch ariadne_codegen.config.get_client_settings
        ariadne_codegen.config.get_client_settings = lambda _: config

        from ariadne_codegen.main import client as ariadne_codegen_client

        ariadne_codegen_client(config)


def main():
    asyncio.run(aiware_codegen_client(get_settings()))


if __name__ == "__main__":
    main()
