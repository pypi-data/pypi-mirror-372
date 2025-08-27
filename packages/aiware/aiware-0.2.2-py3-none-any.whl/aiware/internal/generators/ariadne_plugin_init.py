import ast
from typing import cast

from ariadne_codegen.plugins.base import Plugin


class InitPlugin(Plugin):
    def generate_init_module(self, module: ast.Module) -> ast.Module:
        import_list = list(filter(lambda stmt: isinstance(stmt, ast.ImportFrom) and stmt.module != "async_base_client_ref" and stmt.module != "base_client_ref" and stmt.module != "client" and stmt.module != "async_client", module.body))
        assn_stmt = next(stmt for stmt in module.body if isinstance(stmt, ast.Assign))

        import_list.append(ast.ImportFrom(
            module="async_base_client_ref",
            names=[ast.alias(name="AsyncBaseClient")],
            level=1
        ))

        import_list.append(ast.ImportFrom(
            module="async_client",
            names=[ast.alias(name="GeneratedAsyncAiwareGraphQL")],
            level=1
        ))

        import_list.append(ast.ImportFrom(
            module="base_client_ref",
            names=[ast.alias(name="BaseClient")],
            level=1
        ))

        import_list.append(ast.ImportFrom(
            module="client",
            names=[ast.alias(name="GeneratedAiwareGraphQL")],
            level=1
        ))

        assn_stmt_list = cast(ast.List, assn_stmt.value)
        assn_stmt_elts = list(filter(lambda stmt: isinstance(stmt, ast.Constant) and stmt.value != "AsyncBaseClient" and stmt.value != "BaseClient" and stmt.value != "GeneratedAsyncAiwareGraphQL" and stmt.value != "GeneratedAiwareGraphQL", assn_stmt_list.elts))
        
        assn_stmt_elts.append(
            ast.Constant(
                value="AsyncBaseClient"
            )
        )
        assn_stmt_elts.append(
            ast.Constant(
                value="BaseClient"
            )
        )
        assn_stmt_elts.append(
            ast.Constant(
                value="GeneratedAsyncAiwareGraphQL"
            )
        )
        assn_stmt_elts.append(
            ast.Constant(
                value="GeneratedAiwareGraphQL"
            )
        )

        assn_stmt_list.elts = assn_stmt_elts
        
        module.body = [
            *import_list,
            assn_stmt
        ]
        return module
