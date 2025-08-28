import getpass
import json
import keycloak
import logging
import time
from typing import List, Tuple, Union
from cryptography.fernet import Fernet
import requests
from inspect import getfullargspec

from atscale.errors import atscale_errors
from atscale.utils import request_utils, input_utils, validation_utils
from atscale.base import endpoints, templates, private_enums
from atscale.utils.db_utils import _WarehouseInfo

import psycopg

logger = logging.getLogger(__name__)


class _Connection:
    """An object responsible for the fundamental level of connection and communication to AtScale in the explicit
    realm of a user and an instance."""

    def __init__(
        self,
        server: str,
        username: str = None,
        password: str = None,
        verify: Union[str, bool] = True,
        sso_login: bool = False,
    ):
        """Instantiates a Connection to an AtScale server given the associated parameters. After instantiating,
        _Connection.connect() needs to be called to attempt to establish and store the connection.

        Args:
            server (str): The address of the AtScale server. Be sure to exclude any accidental / or : at the end
            username (str, optional): The username to log in with. Leave as None to prompt if necessary upon calling connect().
            password (str, optional): The password to log in with. Leave as None to prompt if necessary upon calling connect().
            verify (str|bool, optional): Whether to verify ssl certs. Can also be the path to the cert to use. Defaults to True.
            sso_login (bool, optional): Whether to use sso to log in. Defaults to False.
        """
        inspection = getfullargspec(self.__init__)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        # use the setter so it can throw exception if server is None
        if len(server) > 0 and server[-1] == "/":
            server = server[:-1]
        self._server = server
        self.session = requests.Session()
        self.session.verify = verify
        # use the setter so it can throw exception if username is None
        self._username = username
        self._sso_login = sso_login
        self.__fernet = Fernet(Fernet.generate_key())
        if password:
            self._password = self.__fernet.encrypt(password.encode())
        else:
            self._password = None
        self.__token: str = None
        self.__refresh_token: str = None

    @property
    def server(self) -> str:
        """Getter for the server instance variable

        Returns:
            str: the server string
        """
        return self._server

    @server.setter
    def server(
        self,
        value: str,
    ):
        """Setter for the server instance variable. Resets connection

        Args:
            value (str): the new server string
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of server is final; it cannot be altered."
        )

    @property
    def sso_login(self) -> bool:
        """Getter for the sso_login instance variable

        Returns:
            bool: whether sso should be used for login
        """
        return self._sso_login

    @sso_login.setter
    def sso_login(
        self,
        value: bool,
    ):
        """Setter for the sso_login instance variable. Resets connection

        Args:
            value (bool): the new boolean value
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of sso_login is final; it cannot be altered."
        )

    @property
    def username(self) -> str:
        """Getter for the username instance variable

        Returns:
            str: the username string
        """
        return self._username

    @username.setter
    def username(
        self,
        value: str,
    ):
        """The setter for the username instance variable. Resets connection

        Args:
            value (str): the new username string
        """
        inspection = getfullargspec(self.username)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        if value is None:
            raise ValueError("Username cannot be null.")
        # set token to none to require (re)connect
        self.__set_tokens(None, None)
        self._username = value

    @property
    def password(self) -> str:
        """The getter for the password instance variable"""
        raise atscale_errors.UnsupportedOperationException(
            "Passwords are secure and cannot be retrieved."
        )

    @password.setter
    def password(
        self,
        value: str,
    ):
        """The setter for the password instance variable. Resets connection

        Args:
            value (str): the new password to try
        """
        inspection = getfullargspec(self.password)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        if value is None:
            raise ValueError("Password cannot be null.")
        # set token to none to require (re)connect
        self.__set_token(None, None)
        self._password = self.__fernet.encrypt(value.encode())

    def __set_token(self, access_token, refresh_token):
        """Private method as a convenience for maintaining headers when the token is changed.
        See https://docs.python.org/3/tutorial/classes.html#private-variables
        Args:
            access_tone (str): the new access token value
            refresh_tone (str): the new refresh token value
        """
        self.__token = access_token
        self.__refresh_token = refresh_token

    def __set_refresh_token(
        self,
        value,
    ):
        """Private method as a convenience for maintaining headers when the token is changed.
        See https://docs.python.org/3/tutorial/classes.html#private-variables
        Args:
            value (str): the new token value
        """
        self.__refresh_token = value

    def _get_postgres_conn(self, data_model):
        if self.sso_login:
            username = "\t\btoken"
            password = self.__token
        else:
            username = self._username
            password = self.__fernet.decrypt(self._password).decode()
        conn = psycopg.connect(
            host=self.server.split("//")[1].split(":")[0],
            dbname=data_model.catalog.name,
            user=username,
            password=password,
            port=15432,
        )
        return conn

    def _submit_request(
        self,
        request_type: private_enums.RequestType,
        url: str,
        content_type: str = "json",
        data: str = "",
        raises: bool = False,
    ):
        headers = request_utils.generate_headers(content_type, self.__token)
        if request_type == private_enums.RequestType.GET:
            response = request_utils.get_rest_request(
                url, data, headers, raises, session=self.session
            )
        elif request_type == private_enums.RequestType.PATCH:
            response = request_utils.patch_rest_request(
                url, data, headers, raises, session=self.session
            )
        elif request_type == private_enums.RequestType.POST:
            response = request_utils.post_rest_request(
                url, data, headers, raises, session=self.session
            )
        elif request_type == private_enums.RequestType.PUT:
            response = request_utils.put_rest_request(
                url, data, headers, raises, session=self.session
            )
        elif request_type == private_enums.RequestType.DELETE:
            response = request_utils.delete_rest_request(
                url, data, headers, raises, session=self.session
            )
        else:
            raise ValueError("Invalid request type.")

        # If we get a 401 re-auth and try again else just do the normal check response flow
        if response.status_code == 401 or response.status_code == 403:
            logger.info("Token expired reauthorizing")
            self._auth()
            return self._submit_request(request_type, url, content_type, data, raises=True)
        if not response.ok and json.loads(response.text).get("response", {}).get(
            "error", ""
        ).endswith("i/o timeout"):
            logger.info("I/O internal server error, retrying")
            return self._submit_request(request_type, url, content_type, data, raises=True)
        if not raises:
            request_utils.check_response(response)
        return response

    def _connect(self):
        """Connects to AtScale server using class variables necessary for authentication (which can be set directly, provided in constructor,
        or passed as a parameter here). Validates the license, and stores the api token.
        May ask for user input.

        """
        # if not self.password:
        #     self.password = getpass.getpass(prompt=f'Please enter your AtScale password for user \'{self.username}\': ')
        self.__token = None

        if not self.__token:
            self._auth()
        self._validate_license()

    def _auth(self):
        keycloak_openid = keycloak.KeycloakOpenID(
            server_url=endpoints._endpoint_auth(self),
            client_id="atscale-ai-link",
            realm_name="atscale",
            verify=self.session.verify,
        )
        if self.__refresh_token is not None:
            try:
                token_data = keycloak_openid.refresh_token(self.__refresh_token)
                self.__set_token(token_data.get("access_token"), token_data.get("refresh_token"))
                return
            except:
                pass
        if self._sso_login:
            device_info = keycloak_openid.device()
            print("Log in through the following url:")
            print(device_info.get("verification_uri_complete"))
            print("Waiting for user authorization...")
            authenticated = False
            interval = device_info.get("interval")
            expires_in = device_info.get("expires_in")
            while not authenticated and expires_in > 0:
                try:
                    token_data = keycloak_openid.token(
                        grant_type="urn:ietf:params:oauth:grant-type:device_code",
                        device_code=device_info["device_code"],
                        scope="openid",
                    )
                    self.__set_token(
                        token_data.get("access_token"), token_data.get("refresh_token")
                    )
                    authenticated = True
                    print("Authorization successful")
                    break
                except Exception as e:
                    # Handle pending or authorization_pending errors
                    if "authorization_pending" in str(e) or "pending" in str(e):
                        expires_in = expires_in - interval
                        time.sleep(device_info.get("interval", 5))  # Poll every 'interval' seconds
                    else:
                        raise atscale_errors.AuthenticationError(e)
            if not authenticated:
                print("Authorization expired")
        else:
            if not self.username:
                username = input_utils.get_string_input(msg=f"Please enter your AtScale username: ")
            else:
                username = self._username

            if self._password:
                password = self.__fernet.decrypt(self._password).decode()
            else:
                password = getpass.getpass(
                    prompt=f"Please enter your AtScale password for user '{username}': "
                )
            try:
                token_data = keycloak_openid.token(
                    username=username, password=password, grant_type="password", scope="openid"
                )
                self.__set_token(token_data.get("access_token"), token_data.get("refresh_token"))
                self._password = self.__fernet.encrypt(password.encode())
            except Exception as e:
                self._password = None
                raise atscale_errors.AuthenticationError(e)

    def _validate_license(
        self,
        specific_feature_flag=None,
    ) -> bool:
        """Validates that the AtScale server has the necessary flags in its license.

        Args:
            specific_feature_flag (str, optional): The specific feature flag to validate. Defaults to None to check all flags necessary for AI-Link.
        """

        # If we got a feature flag as an input we only check that and immediately return
        if specific_feature_flag:
            response = self._submit_request(
                request_type=private_enums.RequestType.GET,
                url=endpoints._endpoint_license_entitlement(self, specific_feature_flag),
            )
            return response.json().get("status", False)

        # If not we check the general flags we use
        response = self._submit_request(
            request_type=private_enums.RequestType.GET,
            url=endpoints._endpoint_license_entitlement(self, "FEATURE_AILINK"),
        )
        ai_link = response.json().get("status", False)

        response = self._submit_request(
            request_type=private_enums.RequestType.GET,
            url=endpoints._endpoint_license_entitlement(self, "FEATURE_DATA_CATALOG_API"),
        )
        data_catalog_api = response.json().get("status", False)

        # Not having the data catalog api is only a warning because we can still function
        if not data_catalog_api:
            logger.warning(
                "Data Catalog API not licensed for your server. You may have issues pulling metadata"
            )
        # Error if they don't have access to AI-Link
        if not ai_link:
            self.__set_token(None, None)
            raise atscale_errors.InaccessibleAPIError(
                "AI-Link is not licensed for your AtScale server."
            )
        return True

    def _connected(self) -> bool:
        """Convenience method to determine if this object has connected to the server and authenticated.
        This is determined based on whether a token has been stored locally after a connection with the
        server.

        Returns:
            bool: whether this object has connected to the server and authenticated.
        """
        if self.__token is not None:
            return True
        else:
            return False

    def _get_connection_groups(self) -> List[_WarehouseInfo]:
        self._check_connected()

        u = endpoints._endpoint_warehouse(self)

        # this call will handle or raise any errors
        response = self._submit_request(
            request_type=private_enums.RequestType.GET,
            url=u,
        )

        content = response.json()

        if len(content) < 1:
            raise atscale_errors.AtScaleServerError(
                "No connection groups found. Make sure there is a warehouse connection in the "
                "AtScale UI and you have the appropriate access to existing warehouses."
            )

        warehouse_info_list = []

        for dict in content:

            warehouse_info_list.append(
                _WarehouseInfo(
                    name=dict.get("name"),
                    platform_type=private_enums.PlatformType(dict.get("platformType")),
                    connection_id=dict.get("connectionId"),
                )
            )

        # return warehouses sorted alphabetically by name
        return sorted(warehouse_info_list, key=lambda o: o.name.upper())

    def _get_repos(self):
        """Gets the available repos on the server.

        Returns:
            Dict: full json spec of any repos
        """
        # construct the request url
        url = endpoints._endpoint_repo(self)
        # submit request, check for errors which will raise exceptions if there are any
        response = self._submit_request(request_type=private_enums.RequestType.GET, url=url)
        # if we get down here, no exceptions raised, so parse response
        return response.json()

    def _get_catalogs(self, include_soft_published: bool = False, repo_id: str = None):
        """Gets the available catalogs on the server.

        Returns:
            Dict: full json spec of any catalogs
        """
        # construct the request url
        url = endpoints._endpoint_catalog(self)
        # submit request, check for errors which will raise exceptions if there are any
        response = self._submit_request(request_type=private_enums.RequestType.GET, url=url)
        # if we get down here, no exceptions raised, so parse response
        catalog_list = response.json()
        if not include_soft_published:
            catalog_list = [x for x in catalog_list if x.get("publishType") == "normal_publish"]
        if repo_id is not None:
            catalog_list = [x for x in catalog_list if x.get("linkedCatalogId") == repo_id]
        return catalog_list

    def _post_atscale_query(
        self,
        query,
        catalog_name,
        use_aggs=True,
        gen_aggs=False,
        fake_results=False,
        use_local_cache=True,
        use_aggregate_cache=True,
        timeout=10,
    ):
        """Submits an AtScale SQL query to the AtScale server and returns the http requests.response object.

        Args:
            query (str): The query to submit.
            catalog_name (str): The name of the catalog being queried.
            use_aggs (bool, optional): Whether to allow the query to use aggs. Defaults to True.
            gen_aggs (bool, optional): Whether to allow the query to generate aggs. Defaults to False.
            fake_results (bool, optional): Whether to use fake results. Defaults to False.
            use_local_cache (bool, optional): Whether to allow the query to use the local cache. Defaults to True.
            use_aggregate_cache (bool, optional): Whether to allow the query to use the aggregate cache. Defaults to True.
            timeout (int, optional): The number of minutes to wait for a response before timing out. Defaults to 10.
        Returns:
            requests.response: A response with a status code, text, and content fields.
        """
        json_data = json.dumps(
            templates.create_query_for_post_request(
                query=query,
                catalog_name=catalog_name,
                use_aggs=use_aggs,
                gen_aggs=gen_aggs,
                fake_results=fake_results,
                use_local_cache=use_local_cache,
                use_aggregate_cache=use_aggregate_cache,
                timeout=timeout,
            )
        )
        attempts = 10
        done = False
        while attempts > 0 and done == False:
            response = self._submit_request(
                request_type=private_enums.RequestType.POST,
                url=endpoints._endpoint_atscale_query_submit(self),
                data=json_data,
            )
            data = json.loads(response.text)
            if data["metadata"]["succeeded"] == False and (
                "Error during query planning: no such vertex in graph"
                in data["metadata"]["error-message"]
                or "Error during query planning: key not found: AnonymousKey("
                in data["metadata"]["error-message"]
            ):
                time.sleep(1)
                attempts = attempts - 1
            else:
                done = True
        return response

    def _get_connected_databases(
        self,
        warehouse_id: str,
    ) -> List[str]:
        """Get a list of databases the instance can access in the provided warehouse.

        Args:
            warehouse_id (str): The AtScale warehouse connection to use.

        Returns:
            List[str]: The list of available databases
        """

        self._check_connected()

        u = endpoints._endpoint_warehouse_databases(self, warehouse_id)
        response = self._submit_request(request_type=private_enums.RequestType.GET, url=u)
        return response.json()

    def _get_connected_schemas(
        self,
        warehouse_id: str,
        database: str,
    ) -> List[str]:
        """Get a list of schemas the instance can access in the provided warehouse and database.

        Args:
            warehouse_id (str): The AtScale warehouse connection to use.
            database (str): The database to use.

        Returns:
            List[str]: The list of available tables
        """

        self._check_connected()

        u = endpoints._endpoint_warehouse_all_schemas(self, warehouse_id, database)
        response = self._submit_request(request_type=private_enums.RequestType.GET, url=u)
        return response.json()

    def _get_connected_tables(
        self,
        warehouse_id: str,
        database: str,
        schema: str,
    ) -> List[str]:
        """Get a list of tables the instance can access in the provided warehouse, database, and schema.

        Args:
            warehouse_id (str): The AtScale warehouse connection to use.
            database (str): The database to use.
            schema (str): The schema to use.

        Returns:
            List[str]: The list of available tables
        """

        self._check_connected()

        u = endpoints._endpoint_warehouse_all_tables(
            self,
            connection_id=warehouse_id,
            database=database,
            schema=schema,
        )
        response = self._submit_request(request_type=private_enums.RequestType.GET, url=u)
        return response.json()

    def _get_table_columns(
        self,
        warehouse_id: str,
        table_name: str,
        database: str = None,
        schema: str = None,
        expected_columns: List[str] = None,
    ) -> List[Tuple]:
        """Get all columns in a given table

        Args:
            warehouse_id (str): The AtScale warehouse to use.
            table_name (str): The name of the table to use.
            database (str, optional): The database to use. Defaults to None to use default database
            schema (str, optional): The schema to use. Defaults to None to use default schema
            expected_columns (List[str], optional): A list of expected column names to validate. Defaults to None

        Returns:
            List[Tuple]: Pairs of the columns and data-types (respectively) of the passed table
        """
        self._check_connected()

        url = endpoints._endpoint_warehouse_single_table_info(
            self,
            connection_id=warehouse_id,
            table=table_name,
            schema=schema,
            database=database,
        )
        response = self._submit_request(request_type=private_enums.RequestType.GET, url=url)
        table_columns = [(x["name"], x["dataType"]) for x in response.json()["columns"]]
        table_column_names = [x[0] for x in table_columns]
        if expected_columns is not None:
            for column in expected_columns:
                if column in table_column_names:
                    continue
                elif column.upper() in table_column_names:
                    logger.warning(f"Column name: {column} appears as {column.upper()}")
                elif column.lower() in table_column_names:
                    logger.warning(f"Column name: {column} appears as {column.lower()}")
                else:
                    logger.warning(f"Column name: {column} does not appear in table {table_name}")
        return table_columns

    def _get_query_columns(
        self,
        warehouse_id: str,
        query: str,
    ):
        """Get all columns of a direct query, to the given warehouse_id, as they are represented by AtScale.

        Args:
            warehouse_id (str): The AtScale warehouse to use.
            query (str): A valid query for the warehouse of the given id, of which to return the resulting columns

        Returns:
            List[Tuple]: A list of columns represented as Tuples of (name, data-type)
        """
        self._check_connected()

        # preview query
        url = endpoints._endpoint_warehouse_query_info(self, warehouse_id)
        payload = {"query": query}
        response = self._submit_request(
            request_type=private_enums.RequestType.POST, url=url, data=json.dumps(payload)
        )
        # parse response into tuples of name and data-type
        columns = [(x["name"], x["dataType"]) for x in response.json()["columns"]]
        return columns

    def _get_query_sample(
        self,
        warehouse_id: str,
        query: str,
    ):
        """Get all columns of a direct query, to the given warehouse_id, as they are represented by AtScale.

        Args:
            warehouse_id (str): The AtScale warehouse to use.
            query (str): A valid query for the warehouse of the given id, of which to return the resulting columns

        Returns:
            List[Tuple]: A list of columns represented as Tuples of (name, data-type)
        """
        self._check_connected()

        # preview query
        url = endpoints._endpoint_warehouse_query_sample(self, warehouse_id)
        payload = {"query": query, "udf": ""}
        response = self._submit_request(
            request_type=private_enums.RequestType.POST, url=url, data=json.dumps(payload)
        )
        return response.json()

    def _validate_sql(
        self,
        warehouse_id: str,
        database: str,
        schema: str,
        table_name: str,
        query: str,
    ):
        """Get all columns of a direct query, to the given warehouse_id, as they are represented by AtScale.

        Args:
            warehouse_id (str): The AtScale warehouse to use.
            query (str): A valid query for the warehouse of the given id, of which to return the resulting columns

        Returns:
            List[Tuple]: A list of columns represented as Tuples of (name, data-type)
        """
        self._check_connected()

        # preview query
        url = endpoints._endpoint_warehouse_validate_sql(self, warehouse_id)
        payload = {"sql": query, "database": database, "dbSchema": schema, "table": table_name}
        response = self._submit_request(
            request_type=private_enums.RequestType.POST, url=url, data=json.dumps(payload)
        )
        return response.json()

    def _check_connected(
        self,
        err_msg=None,
    ):
        outbound_error = "No connection established to AtScale, please establish a connection by calling Client.connect()."
        if err_msg:
            outbound_error = err_msg
        if not self._connected():
            raise atscale_errors.AuthenticationError(outbound_error)
