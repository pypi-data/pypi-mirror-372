import logging
import requests
from typing import List, Dict, Tuple, Union
from requests import Session
from inspect import getfullargspec

from atscale.base import config, endpoints
from atscale.connection.connection import _Connection
from atscale.errors import atscale_errors
from atscale.repo import Repo
from atscale.utils import input_utils, validation_utils

logger = logging.getLogger(__name__)


class Client:
    """Creates a Client with a connection to an AtScale server to allow for interaction with the the server."""

    def __init__(
        self,
        config_path: str = None,
        server: str = None,
        username: str = None,
        password: str = None,
        verify: Union[str, bool] = None,
        sso_login: bool = False,
    ):
        """All parameters are optional. If none are provided, this method will attempt to use values from the following, local configuration files:
        - ~/.atscale/config - for server
        - ~/.atscale/credentials - for username and password

        If a config_path parameter is provided, all values will be read from that file.

        Any values provided in addition to a config_path parameter will take precedence over values read in from the file at config_path.

        Args:
            config_path (str, optional): path to a configuration file in .INI format with values for the other parameters. Defaults to None.
            server (str, optional): the AtScale server instance. Defaults to None.
            username (str, optional): username. Defaults to None.
            password (str, optional): password. Defaults to None.
            verify (str|bool, optional): Whether to verify ssl certs. Can also be the path to the cert to use. Defaults to True.
            sso_login (bool, optional): Whether to use sso to log in. Defaults to False.

        Returns:
            Client: an instance of this class
        """
        inspection = getfullargspec(self.__init__)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        # Config will load default config files config.ini, ~/.atscale/config and ~/.atscale/credentials on first call to constructor.
        # It's a singleton, so subsequent calls to it's constructor will simply obtain a reference to the existing instance.
        if config_path is not None:
            cfg = config.Config()
            # Any keys in here that are already in Config will get new values from this file
            cfg.read(config_path)
        # go ahead nad grab the connection values from config
        s, u, p, dc, dp, v, l = self._get_connection_parameters_from_config()
        # finally, we'll overwrite values with any they passed in
        if server is not None:
            s = server
        if username is not None:
            u = username
        if password is not None:
            p = password

        if verify is not None:
            v = verify
        elif v is None:
            v = True

        if sso_login is not None:
            l = sso_login
        elif l is None:
            l = False

        # if we didn't find these values in the Config work above and they weren't passed in, then we didn't get enough info
        if s is None:
            raise ValueError(f"Value for server cannot be null.")

        # check we are connected to the containerized AtScale
        self._version_check(s, v)

        # otherwise we'll go ahead and make the connection object
        self._atconn = _Connection(server=s, username=u, password=p, verify=v, sso_login=l)

    @property
    def session(self) -> Session:
        return self._atconn.session

    def get_version(self) -> str:
        """A getter function for the current version of the library

        Returns:
            str: The current version of the library
        """
        return config.Config().version

    def connect(self):
        """Initializes the Client object's connection"""
        self._atconn._connect()

    def _get_connection_parameters_from_config(self):
        cfg = config.Config()
        # should be placed in ~/.atscale/credentials then config will grab them
        username = cfg.get("username")
        password = cfg.get("password")
        # Config reads these first from config.ini in project root and then ~/.atscale/config.
        # Would be overwritten with any values from subsequent config_path read in.
        server = cfg.get("server")
        jdbc_driver_class = cfg.get(
            "jdbc_driver_class", default_value="org.apache.hive.jdbc.HiveDriver"
        )
        jdbc_driver_path = cfg.get("jdbc_driver_path", default_value="")
        verify = cfg.get("verify")
        sso_login = cfg.get("sso_login")
        return (server, username, password, jdbc_driver_class, jdbc_driver_path, verify, sso_login)

    def _version_check(self, server: str, verify: bool):
        if server[-1] == "/":
            server = server[:-1]
        # try to hit the installer engine version endpoint
        try:
            resp = requests.get(
                endpoints._endpoint_engine_version(server), timeout=5, verify=verify
            )
        except:
            try:
                resp = requests.get(
                    endpoints._endpoint_installer_engine_version(server), timeout=5, verify=verify
                )
            except:
                # if it didn't work then we can't reach the server for some reason
                logger.warn("Unable to verify AtScale server version.")
                return False
        if resp.ok and not resp.text.startswith("202"):
            # if that worked and the version does not start with 202 then they have the container AtScale
            return True
        elif resp.ok and resp.text.startswith("202"):
            # if that worked but the version starts with 202 then they have the installer AtScale but this version of AI-Link only supports the container version
            logger.error(
                "AtScale server is runnning installer version which requires downgrading to AI-Link version less than 3.0.0"
            )
            return False
        else:
            # if it didn't work then we can't reach the server for some reason
            logger.warn("Unable to verify AtScale server version.")
            return False

    def select_repo(self, repo_id: str = None, name_contains: str = None) -> Repo:
        """Prompts the user to select a repo that the client can access.

        Args:
            repo_id (str, optional): A repo id, will select the repo with the matching id.
                If None, asks user to select from list. Defaults to None.
            name_contains (str, optional): A string to use for string comparison to filter the found repo names.
                Defaults to None.

        Returns:
            Repo: the selected Repo
        """
        inspection = getfullargspec(self.select_repo)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        self._atconn._check_connected()

        if repo_id is None:
            # repos is a list of dicts where each is a repo
            repo_dict_list = self.get_repos()

            # if they have an idea of the name we can limit the return list
            if name_contains is not None:
                filtered_repo_dict_list = [
                    x for x in repo_dict_list if name_contains.lower() in x["name"].lower()
                ]
                if len(filtered_repo_dict_list) == 0:
                    raise ValueError(
                        f"No repos found with name containing '{name_contains}'. "
                        f"Here are all the repo names: {[repo['name'] for repo in repo_dict_list]}"
                    )
                repo_dict_list = filtered_repo_dict_list

            repo_dict_list = sorted(repo_dict_list, key=lambda d: d["name"].upper())
            # ask the user to select one of the repos, return dict result
            repo_dict = input_utils.choose_id_and_name_from_dict_list(
                repo_dict_list, "Please choose a repo:", id_key="id", name_key="name"
            )
            if repo_dict is None:
                return None
            repo_id = repo_dict.get("id")
            if repo_id is None:
                msg = "repo_id was None in Client.select_repo after getting a non None repo_dict"
                raise atscale_errors.ModelingError(msg)

        repo = Repo(client=self, repo_id=repo_id)
        return repo

    def get_catalogs(self, include_soft_published: bool = False) -> List[Dict[str, str]]:
        """Returns a list of dicts for each of the listed catalogs and their repos.

        Args:
            include_soft_publish (bool, optional): Whether to include soft published catalogs. Defaults to False.

        Returns:
            List[Dict[str,str]]: List of 4 item dicts where keys are 'catalog_id', 'catalog_name', 'repo_id', 'repo_name' of available catalogs.
        """
        inspection = getfullargspec(self.get_catalogs)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())
        self._atconn._check_connected(),

        catalog_list = self._atconn._get_catalogs(include_soft_published)
        repo_list = self._atconn._get_repos()
        if catalog_list is None:
            return []

        ret_list = []
        for repo in repo_list:
            for catalog in catalog_list:
                if repo["id"] == catalog["linkedCatalogId"]:
                    ret_dict = {}
                    ret_dict["catalog_id"] = catalog["id"]
                    ret_dict["catalog_name"] = catalog["name"]
                    ret_dict["repo_id"] = repo["id"]
                    ret_dict["repo_name"] = repo["name"]
                    ret_list.append(ret_dict)
        return sorted(ret_list, key=lambda d: (d["repo_name"].upper(), d["catalog_name"].upper()))

    def get_repos(self) -> List[Dict[str, str]]:
        """Returns a list of dicts for each of the available repos.

        Returns:
            List[Dict[str,str]]: List of 2 item dicts where keys are 'id', 'name' of available repos.
        """
        inspection = getfullargspec(self.get_repos)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())
        self._atconn._check_connected(),

        repo_list = self._atconn._get_repos()
        if repo_list is None:
            return []

        ret_list = []
        for dct in repo_list:
            ret_dict = {}
            ret_dict["id"] = dct["id"]
            ret_dict["name"] = dct["name"]
            ret_list.append(ret_dict)
        return sorted(ret_list, key=lambda d: d["name"].upper())

    def get_connected_warehouses(self) -> List[Dict]:
        """Returns metadata on all warehouses visible to the connected client

        Returns:
            List[Dict]: The list of available warehouses
        """
        connection_groups = self._atconn._get_connection_groups()

        out_list = []

        for ind, wh in enumerate(connection_groups):
            ret_dict = wh.__dict__
            ret_dict["platform"] = ret_dict["platform_type"]._value_
            del ret_dict["platform_type"]

            out_list.append(ret_dict)

        return out_list

    def get_connected_databases(
        self,
        warehouse_id: str,
    ) -> List[str]:
        """Get a list of databases the client can access in the provided warehouse.

        Args:
            warehouse_id (str): The AtScale warehouse connection to use.

        Returns:
            List[str]: The list of available databases
        """
        inspection = getfullargspec(self.get_connected_databases)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        ret_list = self._atconn._get_connected_databases(warehouse_id=warehouse_id)
        return sorted(ret_list, key=lambda d: d.upper())

    def get_connected_schemas(
        self,
        warehouse_id: str,
        database: str,
    ) -> List[str]:
        """Get a list of schemas the client can access in the provided warehouse and database.

        Args:
            warehouse_id (str): The AtScale warehouse connection to use.
            database (str): The database to use.

        Returns:
            List[str]: The list of available tables
        """
        inspection = getfullargspec(self.get_connected_schemas)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        ret_list = self._atconn._get_connected_schemas(warehouse_id=warehouse_id, database=database)
        return sorted(ret_list, key=lambda d: d.upper())

    def get_connected_tables(
        self,
        warehouse_id: str,
        database: str,
        schema: str,
    ) -> List[str]:
        """Get a list of tables the client can access in the provided warehouse, database, and schema.

        Args:
            warehouse_id (str): The AtScale warehouse connection to use.
            database (str): The database to use.
            schema (str): The schema to use.

        Returns:
            List[str]: The list of available tables
        """
        inspection = getfullargspec(self.get_connected_tables)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        ret_list = self._atconn._get_connected_tables(
            warehouse_id=warehouse_id, database=database, schema=schema
        )
        return sorted(ret_list, key=lambda d: d.upper())

    def get_table_columns(
        self,
        warehouse_id: str,
        database: str,
        schema: str,
        table_name: str,
    ) -> List[Tuple]:
        """Get a list of columns the client can access in the provided warehosue, database, schema, and table.

        Args:
            warehouse_id (str): The AtScale warehouse to use.
            database (str): The database to use.
            schema (str): The schema to use.
            table_name (str): The name of the table to use.

        Returns:
             List[Tuple]: Pairs of the columns and data-types (respectively) of the passed table
        """
        inspection = getfullargspec(self.get_table_columns)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        ret_list = self._atconn._get_table_columns(
            warehouse_id=warehouse_id,
            table_name=table_name,
            database=database,
            schema=schema,
        )
        return sorted(ret_list, key=lambda d: d[0].upper())

    def get_query_columns(
        self,
        warehouse_id: str,
        query: str,
    ):
        """Returns a list of all columns involved in the provided query against the given warehouse_id. The columns are returned as they are represented by AtScale.

        Args:
            warehouse_id (str): The AtScale warehouse to use.
            query (str): A valid query for the warehouse of the given id, of which to return the resulting columns

        Returns:
            List[Tuple]: A list of columns represented as Tuples of (name, data-type)
        """
        inspection = getfullargspec(self.get_query_columns)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        ret_list = self._atconn._get_query_columns(warehouse_id=warehouse_id, query=query)
        return sorted(ret_list, key=lambda d: d[0].upper())

    # def get_query_sample(
    #     self,
    #     warehouse_id: str,
    #     query: str,
    # ):
    #     """Get all columns of a direct query, to the given warehouse_id, as they are represented by AtScale.

    #     Args:
    #         warehouse_id (str): The AtScale warehouse to use.
    #         query (str): A valid query for the warehouse of the given id, of which to return the resulting columns

    #     Returns:
    #         List[Tuple]: A list of columns represented as Tuples of (name, data-type)
    #     """
    #     inspection = getfullargspec(self.get_query_columns)
    #     validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

    #     ret_list = self._atconn._get_query_columns(warehouse_id=warehouse_id, query=query)
    #     return sorted(ret_list, key=lambda d: d[0].upper())

    # def validate_sql(
    #     self,
    #     warehouse_id: str,
    #     database: str,
    #     schema: str,
    #     table_name: str,
    #     query: str,
    # ):
    #     """Get all columns of a direct query, to the given warehouse_id, as they are represented by AtScale.

    #     Args:
    #         warehouse_id (str): The AtScale warehouse to use.
    #         query (str): A valid query for the warehouse of the given id, of which to return the resulting columns

    #     Returns:
    #         List[Tuple]: A list of columns represented as Tuples of (name, data-type)
    #     """
    #     inspection = getfullargspec(self.get_query_columns)
    #     validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

    #     ret_list = self._atconn._get_query_columns(warehouse_id=warehouse_id, query=query)
    #     return sorted(ret_list, key=lambda d: d[0].upper())
