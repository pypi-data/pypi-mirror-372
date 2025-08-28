import yaml
from typing import Dict, List
from os import walk
from json import dumps
import logging
import re

from atscale.errors import atscale_errors
from atscale.base import private_enums
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.sml_objects.yaml_object import YamlObject
from atscale.sml_objects.object_classes import (
    calculation_object,
    metric_object,
    catalog_object,
    connection_object,
    dataset_object,
    dimension_object,
    package_object,
)

logger = logging.getLogger(__name__)


class LevelAttributeRef:
    """Class that allows level attributes to be referenced/mutated up and down the
    Dimension/Hierarchy/Level inheritance ladder. Just a thin wrapper around a dict
    mapping unique names to their level attribute objects
    """

    def __init__(
        self,
        level_attributes: List["LevelAttributeObject"],
    ):
        ref = {}

        for level_attribute in level_attributes:
            ref[level_attribute.unique_name] = level_attribute

        self._ref = ref


def write_semantic_object_dict_to_yaml(
    input_dict: Dict,
):
    """Writes a dictionary representing a semantic object to a YAML file

    Args:
        input_dict (Dict): The dictionary representing the semantic object
    """
    path = input_dict.get("file_path")

    if path is not None:
        with open(path, "w") as file:
            yaml.safe_dump(input_dict, file)

    else:
        raise ValueError("File path cannot be None")


def validate_file_path(
    path: str,
    file_types: List[private_enums.FileType] = [
        private_enums.FileType.YAML,
        private_enums.FileType.YML,
    ],
) -> bool:
    """Validates that the given file path `path` leads to a type of file listed in the `file_types` parameter.

    Args:
        path (str): The file path.
        file_types (List[private_enums.FileType], optional): A list of file types. Defaults to a list containing
        both valid file extensions for YAML files.

    Returns:
        bool: True if `path` leads to a file whose type is in `file_types` and False otherwise.
    """
    if not all(isinstance(x, private_enums.FileType) for x in file_types):
        raise ValueError(
            "Please make sure all list elements passed to `file_types` are of type `private_enums.FileType`."
        )

    return any(path[-len(ft.value) :] == ft.value for ft in file_types)


def construct_semantic_object_from_dict(
    input_dict: Dict,
    file_path: str,
) -> "SemanticObject":
    """Constructs a SemanticObject from a given dict `d`.

    Args:
        input_dict (Dict): The dict representing the YAML file in question.
        file_path (str): The file path where the YAML file resides.

    Returns:
        SemanticObject: The SemanticObject constructed.
    """
    file_type = input_dict.get("object_type")

    if file_type is None:
        # check possibility that this is a package object. package objects don't have an
        # object type parameter, so we check whether the name of the file is `package.yml`
        # instead

        # grab part of file after last `/` character if the file path exists
        if file_path is not None:
            search_result = re.search(r"[^/]+$", file_path)

            if search_result:
                file_name = search_result.group(0)

                if file_name == "package.yml":
                    return package_object.PackageObject.parse_dict(
                        object_dict=input_dict,
                        file_path=file_path,
                    )

        raise atscale_errors.SMLError(
            "SML file without `object_type` field encountered."
        )

    match file_type:
        case private_enums.SemanticObjectTypes.CALCULATION.value:
            return calculation_object.CalculationObject.parse_dict(
                object_dict=input_dict,
                file_path=file_path,
            )

        case private_enums.SemanticObjectTypes.CATALOG.value:
            return catalog_object.CatalogObject.parse_dict(
                object_dict=input_dict,
                file_path=file_path,
            )

        case private_enums.SemanticObjectTypes.CONNECTION.value:
            return connection_object.ConnectionObject.parse_dict(
                object_dict=input_dict,
                file_path=file_path,
            )

        case private_enums.SemanticObjectTypes.DATASET.value:
            return dataset_object.DatasetObject.parse_dict(
                object_dict=input_dict,
                file_path=file_path,
            )

        case private_enums.SemanticObjectTypes.DIMENSION.value:
            return dimension_object.DimensionObject.parse_dict(
                object_dict=input_dict,
                file_path=file_path,
            )

        case private_enums.SemanticObjectTypes.METRIC.value:
            return metric_object.MetricObject.parse_dict(
                object_dict=input_dict,
                file_path=file_path,
            )

        case private_enums.SemanticObjectTypes.MODEL.value:
            # TODO: add model object once it's implemented
            return None

        # case private_enums.SemanticObjectTypes.PACKAGE.value:
        #     return package_object.PackageObject.parse_dict(
        #         object_dict=input_dict,
        #         file_path=file_path,
        #     )

        case _:
            logger.warning(f"Object encountered with unsupported type: `{file_type}`.")
            return None


def construct_semantic_objects_in_repo(
    repo_path: str,
) -> Dict:
    """Constructs all semantic objects described in a given repo.

    Args:
        repo_path (str): The path to the given repo.

    Returns:
        Dict: A dict of strings mapping object names to YamlObjects where each object
        fully captures the information in its corresponding YAML file.
    """
    file_paths = []

    for root, _, files in walk(repo_path):
        if files != []:
            file_paths += [f"{root}/{file}" for file in files]

    # only grab paths to YAML files
    file_paths = [x for x in file_paths if validate_file_path(x)]

    semantic_objs = {}

    for file_path in file_paths:
        # construct semantic object
        with open(file_path, "r") as file:
            obj_dict = yaml.safe_load(file)

            file_name = obj_dict.get("unique_name")

            semantic_objs[file_name] = construct_semantic_object_from_dict(
                input_dict=obj_dict,
                file_path=file_path,
            )

    # NOTE: below is here to filter out NoneType objects pending the implementation of ModelObject
    # TODO: remove once ModelObject is implemented
    semantic_objs = {
        key: semantic_objs[key]
        for key in semantic_objs
        if semantic_objs[key] is not None
    }

    return semantic_objs
