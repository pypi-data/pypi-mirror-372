import os

API_PORT = os.getenv("API_PORT", "/api")
ENGINE_PORT = os.getenv("ENGINE_PORT", "/engine")


def _endpoint_warehouse(atconn) -> str:
    return f"{atconn.server}{API_PORT}/data-warehouses/restricted"


# ## unused
# def _endpoint_warehouse_status(atconn, warehouse_id: str) -> str:
#     return f"{atconn.server}{API_PORT}/data-warehouses/{warehouse_id}/status"


def _endpoint_warehouse_databases(
    atconn,
    connection_id: str,
):
    return f"{atconn.server}{API_PORT}/data-sources/conn/{connection_id}/databases"


def _endpoint_warehouse_all_schemas(
    atconn,
    connection_id: str,
    database: str,
):
    return (
        f"{atconn.server}{API_PORT}/data-sources/conn/{connection_id}/databases/{database}/schemas"
    )


def _endpoint_warehouse_all_tables(
    atconn,
    connection_id: str,
    database: str,
    schema: str,
):
    return f"{atconn.server}{API_PORT}/data-sources/conn/{connection_id}/databases/{database}/schemas/{schema}/tables"


def _endpoint_warehouse_single_table_info(
    atconn,
    connection_id: str,
    schema: str,
    database: str,
    table: str,
):
    return f"{atconn.server}{API_PORT}/data-sources/conn/{connection_id}/databases/{database}/schemas/{schema}/tables/{table}/info"


# def _endpoint_warehouse_tables_cacheRefresh(
#     atconn,
#     warehouse_id: str,
# ):
#     """<engine_url>/data-sources/ordId/<organization>"""
#     return f"{atconn.engine_url}/data-sources/orgId/{atconn.organization}/conn/{warehouse_id}/tables/cacheRefresh"


def _endpoint_warehouse_query_info(
    atconn,
    connection_id: str,
):
    """<server>{API_PORT}/data-sources/conn/<connection_id>/query/info"""
    return f"{atconn.server}{API_PORT}/data-sources/conn/{connection_id}/query/info"


def _endpoint_warehouse_query_sample(
    atconn,
    connection_id: str,
):
    """<server>//api/data-sources/conn/<connection_id?/query/sample"""
    return f"{atconn.server}{API_PORT}/data-sources/conn/{connection_id}/query/sample"


def _endpoint_warehouse_validate_sql(
    atconn,
    connection_id: str,
):
    """<server>{API_PORT}/data-sources/conn/<connection_id>/validate-sql"""
    return f"{atconn.server}{API_PORT}/data-sources/conn/{connection_id}/validate-sql"


## unused
# def _endpoint_model_validation(
#     atconn,
# ):
#     return f"{atconn.server}{API_PORT}/catalog/validate-model"


def _endpoint_mdx_syntax_validation(
    atconn,
):
    return f"{atconn.server}{API_PORT}/catalog/mdx-expression/validate"


def _endpoint_dmv_query(atconn):
    return f"{atconn.server}{ENGINE_PORT}/xmla"


## unused
# def _endpoint_jdbc_port(
#     atconn,
#     suffix: str = "",
# ):
#     """Gets the jdbc port for the org"""
#     return f"{atconn.engine_url}/organizations/orgId/{atconn._organization}{suffix}"


def _endpoint_engine_version(server):
    """Gets the version of the AtScale instance"""
    return f"{server}{ENGINE_PORT}/version"


def _endpoint_installer_engine_version(server):
    """Gets the version of the AtScale instance"""
    return f"{server}:10502/version"


def _endpoint_license_entitlement(atconn, entitlement_code: str):
    """Gets the license for this instance"""
    return f"{atconn.server}{API_PORT}/license/entitlement/{entitlement_code}"


def _endpoint_atscale_query_submit(
    atconn,
):
    """Sends an AtScale query"""
    return f"{atconn.server}{API_PORT}/query/submit/json"


def _endpoint_query(atconn, query_id: str, is_subquery: bool):
    return f"{atconn.server}{API_PORT}/queries/{query_id}?isSubquery={str(is_subquery).lower()}"


def _endpoint_query_text(atconn, query_id: str, is_subquery: bool):
    return (
        f"{atconn.server}{API_PORT}/queries/{query_id}/text?isSubquery={str(is_subquery).lower()}"
    )


def _endpoint_auth(
    atconn,
):
    """Pings auth endpoint and generates a bearer token"""
    return f"{atconn.server}/auth/"


def _endpoint_auth_bearer(
    atconn,
):
    """Pings auth endpoint and generates a bearer token"""
    return f"{atconn.server}/auth/realms/atscale/protocol/openid-connect/token"


def _endpoint_catalog(atconn, catalog_id: str = None):
    """gets catalogs"""
    if catalog_id:
        suffix = f"/{catalog_id}"
    else:
        suffix = ""
    return f"{atconn.server}{API_PORT}/catalog{suffix}"


def _endpoint_repo(atconn, repo_id: str = None):
    """gets catalogs"""
    if repo_id:
        suffix = f"/{repo_id}"
    else:
        suffix = ""
    return f"{atconn.server}{API_PORT}/repo{suffix}"


## unused
# def _endpoint_engine_settings(atconn):
#     """Gets the engine settings for this instance"""
#     return f"{atconn.server}{API_PORT}/settings"
