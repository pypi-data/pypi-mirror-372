from inspect import getfullargspec
from typing import Dict

from atscale.utils import validation_utils


class _WarehouseInfo:
    """Stores metadata regarding a connected warehouse"""

    def __init__(
        self,
        name: str,
        platform_type: "PlatformType",
        connection_id: str,
    ):
        """The constructor for the _WarehouseInfo object

        Args:
            name (str): The warehouse name
            platform_type (private_enums.PlatformType): The type of warehouse
            connection_id (str): The warehouse's connection id
        """

        inspection = getfullargspec(self.__init__)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        self.name = name
        self.platform_type = platform_type
        self.connection_id = connection_id

    def to_dict(
        self,
    ) -> Dict:
        """Renders the contents of the _WarehouseInfo object as a dictionary

        Returns:
            Dict: The dictionary describing the _WarehouseInfo object
        """
        return {
            "name": self.name,
            "platform_type": self.platform_type.value,
            "connection_id": self.connection_id,
        }
