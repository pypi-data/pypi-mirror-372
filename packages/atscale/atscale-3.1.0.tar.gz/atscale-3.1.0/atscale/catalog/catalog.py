import logging
from typing import Dict, List
from inspect import getfullargspec

from atscale.errors import atscale_errors
from atscale.utils import input_utils, validation_utils
from atscale.base import endpoints, private_enums

logger = logging.getLogger(__name__)


class Catalog:
    """Creates an object corresponding to an AtScale catalog. References an AtScale Repo and takes a catalog ID
    to construct an object that houses DataModels, data sets, and any
    functionality pertaining to catalog maintenance.
    """

    def __init__(
        self,
        repo: "Repo",
        catalog_id: str,
    ):
        """The Catalog constructor

        Args:
            repo (Repo): The Repo object that the catalog's interactions with the semantic layer will leverage
            id (str): The draft catalog's ID
        """
        from atscale.client.client import Client

        inspection = getfullargspec(self.__init__)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        repo._atconn._check_connected()
        self.__repo = repo

        self.__id: str = catalog_id
        url = endpoints._endpoint_catalog(self.__repo._atconn, catalog_id=self.__id)
        response = self.__repo._atconn._submit_request(
            request_type=private_enums.RequestType.GET, url=url
        ).json()
        self.__name: str = response.get("name")
        self.__caption: str = response.get("caption")

    @property
    def id(self) -> str:
        """Getter for the id instance variable

        Returns:
            str: The catalog id
        """
        return self.__id

    @id.setter
    def id(
        self,
        value,
    ):
        """Setter for the id instance variable. This property is final; it cannot be reset

        Args:
            value (Any): Setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "Value of id is final; it cannot be altered."
        )

    @property
    def name(self) -> str:
        """Getter for the name instance variable

        Returns:
            str: The catalog name
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
    def caption(self) -> str:
        """Getter for the caption instance variable

        Returns:
            str: The catalog caption
        """
        return self.__caption

    @caption.setter
    def caption(
        self,
        value,
    ):
        """Setter for the caption instance variable. This property is final; it cannot be reset

        Args:
            value (Any): Setter cannot be used
        """
        raise atscale_errors.UnsupportedOperationException(
            "Value of caption is final; it cannot be altered."
        )

    @property
    def repo(self):
        """Getter for the repo instance variable

        Returns:
            str: The repo
        """
        return self.__repo

    @repo.setter
    def repo(
        self,
        value,
    ):
        """Setter for the repo instance variable. This property is final; it cannot be reset

        Args:
            value (Any): Setter cannot be used
        """
        raise atscale_errors.UnsupportedOperationException(
            "Value of repo is final; it cannot be altered."
        )

    def get_data_model(
        self,
        model_name: str = None,
    ):
        """Returns the DataModel associated with this Catalog with the given name. If no
        name is provided and there is only one DataModel associated with this Catalog, then that
        one DataModel will be returned. However, if no name is given and there is more than one
        DataModel associated with this Catalog, then None will be returned.

        Args:
            model_name (str, optional): the name of the DataModel to be retrieved. Defaults to None.

        Returns:
            DataModel: a DataModel associated with this Catalog.
        """
        from atscale.data_model import DataModel

        inspection = getfullargspec(self.get_data_model)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        data_model_dict_list = self.get_data_models()
        data_model_dict = None
        # if there's only one and they didn't specify a name, we'll just return the one we have
        if model_name is None and len(data_model_dict_list) == 1:
            data_model_dict = data_model_dict_list[0]
        # otherwise, let's look for the name
        elif model_name is None and len(data_model_dict_list) > 1:
            raise ValueError("There is more than one data_model. Please provide a model_name.")
        else:
            for dmd in data_model_dict_list:
                if dmd.get("name") == model_name:
                    data_model_dict = dmd
                    break
        if data_model_dict is None:
            logger.warning(f"No data model was found with the name {model_name}")
            return None
        data_model_id = data_model_dict.get("id")
        data_model = DataModel(catalog=self, data_model_id=data_model_id)
        return data_model

    def select_data_model(
        self,
        data_model_id: str = None,
        name_contains: str = None,
    ):
        """Prompts the user to select a DataModel that the catalog can access.

        Args:
            data_model_id (str, optional): A data model id, will select the model with the matching id.
                If None, asks user to select from list. Defaults to None.
            name_contains (str, optional): A string to use for string comparison to filter the found data model names.
                Defaults to None.

        Returns:
            DataModel: the selected DataModel
        """
        from atscale.data_model.data_model import DataModel

        inspection = getfullargspec(self.select_data_model)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        if data_model_id is None:
            data_model_dict_list = self.get_data_models()
            # if they have an idea of the name we can limit the return list
            if name_contains is not None:
                filtered_data_model_dict_list = [
                    x for x in data_model_dict_list if name_contains.lower() in x["name"].lower()
                ]
                if len(filtered_data_model_dict_list) == 0:
                    raise ValueError(
                        f"No data models found with name containing '{name_contains}'. "
                        f"Here are all the model names: {[data_model['name'] for data_model in data_model_dict_list]}"
                    )
                data_model_dict_list = filtered_data_model_dict_list

            data_model_dict_list = sorted(data_model_dict_list, key=lambda d: d["name"].upper())
            data_model_dict = input_utils.choose_id_and_name_from_dict_list(
                data_model_dict_list, "Please choose a data model:", id_key="id", name_key="name"
            )
            if data_model_dict is None:
                return None
            data_model_id = data_model_dict.get("id")
            if data_model_id is None:
                msg = "data_model_id was None in Catalog.select_data_model after getting a non None data_model_dict"
                raise atscale_errors.ModelingError(msg)
        data_model = DataModel(self, data_model_id)
        return data_model

    def get_data_models(self) -> List[Dict[str, str]]:
        """Returns a list of metadata dicts for each of the data models in the catalog.

        Returns:
            List[Dict[str,str]]: List of 'id':'name' pairs of available Data Models.
        """

        url = endpoints._endpoint_catalog(self.repo._atconn, catalog_id=self.id)
        response = self.repo._atconn._submit_request(
            request_type=private_enums.RequestType.GET, url=url
        )
        data_model_list = response.json()["models"]
        if data_model_list is None:
            return []
        ret_list = []
        for dct in data_model_list:
            ret_dict = {}
            ret_dict["id"] = dct["id"]
            ret_dict["name"] = dct["name"]
            ret_list.append(ret_dict)
        return sorted(ret_list, key=lambda d: d["name"].upper())
