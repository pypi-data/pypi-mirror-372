import asyncio
import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from aiware.common.auth import EnvAuth


from aiware.graphql.async_client import AsyncAiwareGraphQL
from aiware.common.utils import not_none

import datamodel_code_generator.parser.jsonschema
import datamodel_code_generator.types
from datamodel_code_generator import (
    DataModelType,
    InputFileType,
    PythonVersion,
    generate,
    DatetimeClassType,
)

from aiware.tools.config import get_config_dict, get_config_file_path, get_section

# monkey patch in support for "dateTime" json schema type
datamodel_code_generator.parser.jsonschema.json_schema_data_formats["dateTime"] = {
    "default": datamodel_code_generator.types.Types.date_time
}

class GenerateAiwareSchemasOptions(BaseModel):
    core_graphql_url: str = "https://api.us-1.veritone.com/v3/graphql"
    mapping: dict[str, str]
    output: str
    json_output: Optional[str] = None


async def aiware_codegen_schemas():
    pyproject_path = get_config_file_path()
    pyproject_config = get_config_dict(pyproject_path.__str__())
    aiware_schemas_config_section = get_section(pyproject_config, scope_key="schemas")

    config = GenerateAiwareSchemasOptions.model_validate(aiware_schemas_config_section)

    schemas_dict: dict[str, str] = config.mapping
    model_output = Path(
        os.path.relpath(config.output, pyproject_path.parent)
    )
    json_output = Path(
        os.path.relpath(config.json_output, pyproject_path.parent)
    ) if config.json_output else None
    

    aiware_client = AsyncAiwareGraphQL(
        url=config.core_graphql_url,
        auth=EnvAuth(),
    )

    json_schemas = {"definitions": {}}

    for schema_name, schema_id in schemas_dict.items():
        schema_res = not_none((await aiware_client.get_schema(
            id=schema_id,
        )).sdoSchema)

        json_schema: dict = not_none(schema_res.definition).value
        json_schema["x-aiware-schema"] = schema_id
        json_schema["x-aiware-schema-version"] = f"{schema_res.majorVersion}.{schema_res.minorVersion}"
        json_schema["x-aiware-data-registry"] = schema_res.dataRegistryId
        json_schema["title"] = schema_name

        json_schemas["definitions"][schema_name] = json_schema

    if json_output:
        with open(json_output, "w") as json_file:
            json.dump(json_schemas, json_file, indent=2)

    generate(
        json.dumps(json_schemas),
        input_file_type=InputFileType.JsonSchema,
        # input_filename=f"{name}.json",
        output=model_output,
        # set up the output model types
        output_model_type=DataModelType.PydanticV2BaseModel,
        parent_scoped_naming=True,
        target_python_version=PythonVersion.PY_312,
        field_constraints=True,
        use_annotated=True,
        base_class="aiware.common.schemas.BaseSchema",
        output_datetime_class=DatetimeClassType.Datetime,
        disable_timestamp=True
    )


def main():
    asyncio.run(aiware_codegen_schemas())

if __name__ == "__main__":
    main()
