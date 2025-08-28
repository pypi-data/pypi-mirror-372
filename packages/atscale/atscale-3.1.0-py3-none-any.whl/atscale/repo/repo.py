import logging
from typing import Dict, List
from inspect import getfullargspec

from atscale.errors import atscale_errors
from atscale.connection.connection import _Connection
from atscale.utils import input_utils
from atscale.utils import input_utils, validation_utils
from atscale.base import endpoints, private_enums

logger = logging.getLogger(__name__)


class Repo:
    """Creates an object corresponding to an AtScale repo. References an AtScale Client and takes a repo ID
    to construct an object that houses catalogs and any
    functionality pertaining to repo maintenance.
    """

    def __init__(
        self,
        client: "Client",
        repo_id: str,
    ):
        """The Repo constructor

        Args:
            client (Client): The Client object that the repo's interactions with the semantic layer will leverage
            repo_id (str): The repo's ID
        """
        from atscale.client.client import Client

        inspection = getfullargspec(self.__init__)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        if not client:
            raise atscale_errors.WorkFlowError(
                "Please create a Client and connect before constructing a repo."
            )
        client._atconn._check_connected()
        self._atconn: _Connection = client._atconn

        # check name/id against client, error out if invalid
        client_repos = client.get_repos()

        # check validity of id
        if repo_id not in [repo["id"] for repo in client_repos]:
            raise atscale_errors.ObjectNotFoundError(f"There is no repo with id: {repo_id}.")

        self.__id: str = repo_id
        url = endpoints._endpoint_repo(self._atconn, repo_id=self.__id)
        response = self._atconn._submit_request(
            request_type=private_enums.RequestType.GET, url=url
        ).json()
        self.__name: str = response.get("name")
        self.__url: str = response.get("url")

    @property
    def id(self) -> str:
        """Getter for the id instance variable

        Returns:
            str: The repo id
        """
        return self.__id

    @id.setter
    def id(
        self,
        value,
    ):
        """Setter for the id instance variable. This property is final; it cannot be reset

        Args:
            value (Any): Setter cannot be used
        """
        raise atscale_errors.UnsupportedOperationException(
            "Value of id is final; it cannot be altered."
        )

    @property
    def name(self) -> str:
        """Getter for the name instance variable

        Returns:
            str: The repo name
        """
        return self.__name

    @name.setter
    def name(
        self,
        value,
    ):
        """Setter for the name instance variable. This property is final; it cannot be reset

        Args:
            value (Any): Setter cannot be used
        """
        raise atscale_errors.UnsupportedOperationException(
            "Value of name is final; it cannot be altered."
        )

    @property
    def url(self) -> str:
        """Getter for the url instance variable

        Returns:
            str: The repo url
        """
        return self.__url

    @url.setter
    def url(
        self,
        value,
    ):
        """Setter for the url instance variable. This property is final; it cannot be reset

        Args:
            value (Any): Setter cannot be used
        """
        raise atscale_errors.UnsupportedOperationException(
            "Value of url is final; it cannot be altered."
        )

    def select_catalog(
        self,
        catalog_id: str = None,
        name_contains: str = None,
        include_soft_published: bool = False,
    ):
        """Prompts the user to select a catalog that the repo can access.

        Args:
            catalog_id (str, optional): A data model id, will select the catalog with the matching id.
                If None, asks user to select from list. Defaults to None.
            name_contains (str, optional): A string to use for string comparison to filter the found catalog names.
                Defaults to None.
            include_soft_published (bool, optional): Whether to include soft published catalogs.
                Defaults to None.

        Returns:
            Catalog: the selected Catalog
        """
        from atscale.catalog.catalog import Catalog

        inspection = getfullargspec(self.select_catalog)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        if catalog_id is None:
            catalog_dict_list = self._atconn._get_catalogs(include_soft_published, self.id)
            if name_contains is not None:
                filtered_catalog_dict_list = [
                    x for x in catalog_dict_list if name_contains.lower() in x["name"].lower()
                ]
                if len(filtered_catalog_dict_list) == 0:
                    raise ValueError(
                        f"No catalogs found with name containing '{name_contains}'. "
                        f"Here are all the catalog names: {[catalog['name'] for catalog in catalog_dict_list]}"
                    )
                catalog_dict_list = filtered_catalog_dict_list

            catalog_dict_list = sorted(catalog_dict_list, key=lambda d: d["name"].upper())
            catalog_dict = input_utils.choose_id_and_name_from_dict_list(
                catalog_dict_list, "Please choose a catalog:", id_key="id", name_key="name"
            )
            if catalog_dict is None:
                return None
            catalog_id = catalog_dict.get("id")
            if catalog_id is None:
                msg = "catalog_id was None in Repo.select_catalog after getting a non None catalog_dict"
                raise atscale_errors.ModelingError(msg)
        return Catalog(self, catalog_id)

    def get_catalogs(self, include_soft_published: bool = False) -> List[Dict[str, str]]:
        """Returns a list of dicts for each of the catalogs in the repo.

        Returns:
            List[Dict[str,str]]: List of 'id':'name' pairs of available Catalogs.
        """

        catalog_list = self._atconn._get_catalogs(include_soft_published, self.id)
        ret_list = []
        for dct in catalog_list:
            catalog_dict = {}
            catalog_dict["id"] = dct["id"]
            catalog_dict["name"] = dct["name"]
            ret_list.append(catalog_dict)
        return sorted(ret_list, key=lambda d: d["name"].upper())
