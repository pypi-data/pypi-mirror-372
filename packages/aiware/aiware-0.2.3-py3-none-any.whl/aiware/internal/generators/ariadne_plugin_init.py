import ast
import os
from typing import cast

from ariadne_codegen.plugins.base import Plugin

from aiware.internal.generators.aiware_graphql import AiwareClientGeneratorSettings

def module_name_from_path(file_path: str):
    return os.path.splitext(os.path.basename(file_path))[0]

class InitPlugin(Plugin):
    def generate_init_module(self, module: ast.Module) -> ast.Module:
        config = cast(AiwareClientGeneratorSettings, self.config_dict)
        async_base_client_module = module_name_from_path(config.async_base_client_file_path)
        sync_base_client_module = module_name_from_path(config.sync_base_client_file_path)

        import_list = list(filter(lambda stmt: isinstance(stmt, ast.ImportFrom) and stmt.module != async_base_client_module and stmt.module != sync_base_client_module and stmt.module != config.async_client_file_name and stmt.module != config.sync_client_file_name, module.body))
        assn_stmt = next(stmt for stmt in module.body if isinstance(stmt, ast.Assign))

        import_list.append(ast.ImportFrom(
            module=async_base_client_module,
            names=[ast.alias(name=config.async_base_client_name)],
            level=1
        ))

        import_list.append(ast.ImportFrom(
            module=config.async_client_file_name,
            names=[ast.alias(name=config.async_client_name)],
            level=1
        ))

        import_list.append(ast.ImportFrom(
            module=sync_base_client_module,
            names=[ast.alias(name=config.sync_base_client_name)],
            level=1
        ))

        import_list.append(ast.ImportFrom(
            module=config.sync_client_file_name,
            names=[ast.alias(name=config.sync_client_name)],
            level=1
        ))

        assn_stmt_list = cast(ast.List, assn_stmt.value)
        assn_stmt_elts = list(filter(lambda stmt: isinstance(stmt, ast.Constant) and stmt.value != config.async_base_client_name and stmt.value != config.sync_base_client_name and stmt.value != config.async_client_name and stmt.value != config.sync_client_name, assn_stmt_list.elts))
        
        assn_stmt_elts.append(
            ast.Constant(
                value=config.async_base_client_name
            )
        )
        assn_stmt_elts.append(
            ast.Constant(
                value=config.sync_base_client_name
            )
        )
        assn_stmt_elts.append(
            ast.Constant(
                value=config.async_client_name
            )
        )
        assn_stmt_elts.append(
            ast.Constant(
                value=config.sync_client_name
            )
        )

        assn_stmt_list.elts = assn_stmt_elts
        
        module.body = [
            *import_list,
            assn_stmt
        ]
        return module
