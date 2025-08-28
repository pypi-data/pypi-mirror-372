import logging
from typing import Dict, List

from atscale.base import enums, private_enums
from atscale.data_model.dm_helpers import dmv_helpers


logger = logging.getLogger(__name__)


def _get_published_features(
    data_model,
    feature_list: List[str] = None,
    folder_list: List[str] = None,
    feature_type: enums.FeatureType = enums.FeatureType.ALL,
) -> Dict:
    """Gets the feature names and metadata for each feature in the published DataModel.

    Args:
        data_model (DataModel): The published AtScale data model to get the features of via dmv
        feature_list (List[str], optional): A list of features to return. Defaults to None to return all.
        folder_list (List[str], optional): A list of folders to filter by. Defaults to None to ignore folder.
        feature_type (enums.FeatureType, optional): The type of features to filter by. Options
            include enums.FeatureType.ALL, enums.FeatureType.CATEGORICAL, or enums.FeatureType.NUMERIC. Defaults to ALL.

    Returns:
        Dict: A dictionary of dictionaries where the feature names are the keys in the outer dictionary
                while the inner keys are the following:
                'atscale_type'(value is a level-type, 'Aggregate', or 'Calculated'),
                'description', 'expression', caption, 'folder', 'data_type', and 'feature_type'(value is Numeric or Categorical).
    """
    level_filter_by = {}
    metric_filter_by = {}
    hier_filter_by = {}
    if feature_list:
        feature_list = [feature_list] if isinstance(feature_list, str) else feature_list
        level_filter_by[private_enums.Level.name] = feature_list
        metric_filter_by[private_enums.Metric.name] = feature_list
    if folder_list:
        folder_list = [folder_list] if isinstance(folder_list, str) else folder_list
        hier_filter_by[private_enums.Hierarchy.folder] = folder_list
        metric_filter_by[private_enums.Metric.folder] = folder_list

    feature_dict = {}

    catalog_licensed = data_model.catalog.repo._atconn._validate_license("FEATURE_DATA_CATALOG_API")

    if feature_type is enums.FeatureType.ALL or feature_type is enums.FeatureType.CATEGORICAL:
        hier_dict = dmv_helpers._get_dmv_data(
            model=data_model, fields=[private_enums.Hierarchy.folder], filter_by=hier_filter_by
        )
        level_filter_by[private_enums.Level.hierarchy] = list(hier_dict.keys())
        query_fields = [
            private_enums.Level.type,
            private_enums.Level.description,
            private_enums.Level.hierarchy,
            private_enums.Level.dimension,
            private_enums.Level.caption,
            private_enums.Level.data_type,
        ]
        if catalog_licensed:
            query_fields.append(private_enums.Level.secondary_attribute)
        dimension_dict = dmv_helpers._get_dmv_data(
            model=data_model,
            fields=query_fields,
            filter_by=level_filter_by,
        )
        for name, info in dimension_dict.items():
            # if a level was duplicated we might have multiple hierarchies which could mean multiple folders
            folder = []
            if type(info[private_enums.Level.hierarchy.name]) is list:
                for hierarchy_name in info[private_enums.Level.hierarchy.name]:
                    if hier_dict.get(hierarchy_name):
                        folder.append(
                            hier_dict[hierarchy_name][private_enums.Hierarchy.folder.name]
                        )
            else:
                folder.append(
                    hier_dict[info[private_enums.Level.hierarchy.name]][
                        private_enums.Hierarchy.folder.name
                    ]
                )
                info[private_enums.Level.hierarchy.name] = [
                    info[private_enums.Level.hierarchy.name]
                ]

            feature_dict[name] = {
                "caption": info[private_enums.Level.caption.name],
                "atscale_type": info[private_enums.Level.type.name],
                "data_type": info[private_enums.Level.data_type.name],
                "description": info[private_enums.Level.description.name],
                "hierarchy": info[private_enums.Level.hierarchy.name],
                "dimension": info[private_enums.Level.dimension.name],
                "folder": folder,
                "feature_type": "Categorical",
            }
            if catalog_licensed:
                feature_dict[name]["secondary_attribute"] = info[
                    private_enums.Level.secondary_attribute.name
                ]
            else:
                feature_dict[name]["secondary_attribute"] = False
    if feature_type is enums.FeatureType.ALL or feature_type is enums.FeatureType.NUMERIC:
        query_fields = [
            private_enums.Metric.type,
            private_enums.Metric.description,
            private_enums.Metric.folder,
            private_enums.Metric.caption,
            private_enums.Metric.data_type,
        ]
        if catalog_licensed:
            query_fields.append(private_enums.Metric.expression)
        metric_dict = dmv_helpers._get_dmv_data(
            model=data_model, fields=query_fields, filter_by=metric_filter_by
        )
        for name, info in metric_dict.items():
            agg_type = info[private_enums.Metric.type.name]
            feature_dict[name] = {
                "caption": info[private_enums.Metric.caption.name],
                "atscale_type": agg_type if agg_type != "Calculated" else "Calculated",
                # "aggregation_type": agg_type,
                "data_type": info[private_enums.Metric.data_type.name],
                "description": info[private_enums.Metric.description.name],
                "folder": [info[private_enums.Metric.folder.name]],
                "feature_type": "Numeric",
            }
            if catalog_licensed:
                feature_dict[name]["expression"] = info[private_enums.Metric.expression.name]
            else:
                feature_dict[name]["expression"] = ""

    return feature_dict


def _get_dimensions(data_model, filter_by: Dict[private_enums.Dimension, List[str]] = None) -> Dict:
    """Gets a dictionary of dictionaries with the dimension names and metadata.

    Args:
        data_model (DataModel): The DataModel object to search through
        filter_by (Dict[private_enums.Dimension fields, str], optional): A dict with keys of fields and values of a list of that field's value
                to exclusively include in the return. Defaults to None for no filtering.

    Returns:
        Dict: A dictionary of dictionaries where the dimension names are the keys in the outer dictionary
              while the inner keys are the following: 'description', 'type'(value is Time
              or Standard).
    """
    dimension_dict = dmv_helpers._get_dmv_data(
        model=data_model,
        fields=[
            private_enums.Dimension.description,
            private_enums.Dimension.type,
        ],
        filter_by=filter_by,
    )
    dimensions = {}
    for name, info in dimension_dict.items():
        dimensions[name] = {
            "description": info[private_enums.Dimension.description.name],
            "type": info[private_enums.Dimension.type.name],
        }
    return dimensions


def _get_hierarchies(
    data_model,
    filter_by: Dict[private_enums.Hierarchy, List[str]] = None,
) -> Dict:
    """Gets a dictionary of dictionaries with the hierarchies names and metadata.
    Secondary attributes are treated as their own hierarchies.

    Args:
        data_model (DataModel): The DataModel object to search through
        filter_by (Dict[private_enums.Hierarchy fields, str], optional): A dict with keys of fields and values of a list of that field's value
                to exclusively include in the return. Defaults to None for no filtering.

    Returns:
        Dict: A dictionary of dictionaries where the hierarchy names are the keys in the outer dictionary
              while the inner keys are the following: 'dimension', 'description', 'caption', 'folder', 'type'(value is Time
              or Standard), 'secondary_attribute'.
    """
    hierarchy_dict = dmv_helpers._get_dmv_data(
        model=data_model,
        fields=[
            private_enums.Hierarchy.dimension,
            private_enums.Hierarchy.description,
            private_enums.Hierarchy.folder,
            private_enums.Hierarchy.caption,
            private_enums.Hierarchy.type,
            private_enums.Hierarchy.secondary_attribute,
        ],
        filter_by=filter_by,
    )
    hierarchies = {}
    for name, info in hierarchy_dict.items():
        hierarchies[name] = {
            "dimension": info[private_enums.Hierarchy.dimension.name],
            "description": info[private_enums.Hierarchy.description.name],
            "caption": info[private_enums.Hierarchy.caption.name],
            "folder": info[private_enums.Hierarchy.folder.name],
            "type": info[private_enums.Hierarchy.type.name],
            "secondary_attribute": info[private_enums.Hierarchy.secondary_attribute.name],
        }
    return hierarchies


def _get_hierarchy_levels(
    data_model,
    hierarchy_name: str,
) -> List[str]:
    """Gets a list of the levels of a given hierarchy

    Args:
        data_model (DataModel): The DataModel object the given hierarchy exists within.
        hierarchy_name (str): The name of the hierarchy

    Returns:
        List[str]: A list containing the hierarchy's levels
    """

    levels_from_hierarchy = dmv_helpers._get_dmv_data(
        model=data_model,
        fields=[private_enums.Level.name],
        id_field=private_enums.Level.hierarchy,
        filter_by={private_enums.Level.hierarchy: [hierarchy_name]},
    )

    hierarchy = levels_from_hierarchy.get(hierarchy_name)
    if hierarchy:
        levels = hierarchy.get(private_enums.Level.name.name, [])
        if type(levels) is list:
            return levels
        else:
            return [levels]
    else:
        return []


def _get_all_numeric_feature_names(
    data_model,
    folder: str = None,
) -> List[str]:
    """Returns a list of all numeric features (ie Aggregate and Calculated Metrics) in a given data model.

    Args:
        data_model (DataModel): The DataModel object to be queried.
        folder (str, optional): The name of a folder in the data model containing metrics to exclusively list.
            Defaults to None to not filter by folder.

    Returns:
        List[str]: A list of the query names of numeric features in the data model and, if given, in the folder.
    """
    folders = [folder] if folder else None
    return list(
        data_model.get_features(folder_list=folders, feature_type=enums.FeatureType.NUMERIC).keys()
    )


def _get_all_categorical_feature_names(
    data_model,
    folder: str = None,
) -> List[str]:
    """Returns a list of all categorical features (ie Hierarchy levels and secondary_attributes) in a given DataModel.

    Args:
        data_model (DataModel): The DataModel object to be queried.
        folder (str, optional): The name of a folder in the DataModel containing features to exclusively list.
            Defaults to None to not filter by folder.

    Returns:
        List[str]: A list of the query names of categorical features in the DataModel and, if given, in the folder.
    """
    folders = [folder] if folder else None
    return list(
        data_model.get_features(
            folder_list=folders, feature_type=enums.FeatureType.CATEGORICAL
        ).keys()
    )


def _get_folders(
    data_model,
) -> List[str]:
    """Returns a list of the available folders in a given DataModel.

    Args:
        data_model (DataModel): The DataModel object to be queried.

    Returns:
        List[str]: A list of the available folders
    """

    metric_dict = dmv_helpers._get_dmv_data(model=data_model, fields=[private_enums.Metric.folder])

    hierarchy_dict = dmv_helpers._get_dmv_data(
        model=data_model, fields=[private_enums.Hierarchy.folder]
    )

    folders = sorted(
        set(
            [metric_dict[key]["folder"] for key in metric_dict.keys()]
            + [hierarchy_dict[key]["folder"] for key in hierarchy_dict.keys()]
        )
    )
    if "" in folders:
        folders.remove("")
    return folders
