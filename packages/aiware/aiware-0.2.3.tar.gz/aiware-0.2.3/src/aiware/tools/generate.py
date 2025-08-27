import asyncio

from aiware.tools.config import ConfigFileNotFound, MissingConfiguration, get_config_dict, get_config_file_path
from aiware.tools.client.generate import aiware_codegen_client
from aiware.tools.schemas.generate import aiware_codegen_schemas


async def aiware_codegen():
    try:
        pyproject_path = get_config_file_path()
        pyproject_config = get_config_dict(pyproject_path.__str__())
    except:
        raise ConfigFileNotFound

    try:
        await aiware_codegen_client()
    except MissingConfiguration:
        pass

    try:
        await aiware_codegen_schemas()
    except MissingConfiguration:
        pass

def main():
    asyncio.run(aiware_codegen())

if __name__ == "__main__":
    main()
