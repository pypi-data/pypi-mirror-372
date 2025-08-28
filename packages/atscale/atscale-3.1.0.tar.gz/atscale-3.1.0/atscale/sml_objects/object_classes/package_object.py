from copy import deepcopy
from typing import List, Dict

from atscale.errors import atscale_errors
from atscale.sml_objects.yaml_object import YamlObject
from atscale.sml_objects.object_classes.sub_package_object import SubPackageObject
from atscale.base.private_enums import SemanticObjectTypes


class PackageObject(YamlObject):
    _required_keys = [
        "version",
        "packages",
    ]
    _optional_keys = []

    def __init__(
        self,
        version: str,
        packages: List[SubPackageObject],
    ):
        """An object for defining additional Git repositories whose objects can be used in the current repository

        Args:
            version (str): The schema version for the file; value should be `1`
            packages (List[SubPackageObject]): A list of the Git repositories that the current repository can use objects from
        """
        self._object_type = SemanticObjectTypes.PACKAGE

        self._version = version
        self._packages = packages

        object_dict = {
            "version": self._version,
            "packages": self._packages,
        }

        self._object_dict = object_dict
        self._file_path = None

    @property
    def version(self) -> str:
        """Getter for the version instance variable

        Returns:
            str: The schema version for the file
        """
        return self._version

    @version.setter
    def version(
        self,
        value,
    ):
        """Setter for the version instance variable. This variable is final, you must construct a new PackageObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of version is final; it cannot be altered."
        )

    @property
    def packages(self) -> List[SubPackageObject]:
        """Getter for the packages instance variable

        Returns:
            List[SubPackageObject]: A list of the Git repositories that the current repository can use objects from
        """
        return self._packages

    @packages.setter
    def packages(
        self,
        value,
    ):
        """Setter for the packages instance variable. This variable is final, you must construct a new PackageObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of packages is final; it cannot be altered."
        )

    @property
    def unique_name(self) -> str:
        """Getter for the unique_name instance variable. Not implemented for this object

        Returns:
            str: Nothing
        """
        raise NotImplementedError

    @unique_name.setter
    def unique_name(
        self,
        value,
    ):
        """Setter for the unique_name instance variable. Not implemented for this object.

        Args:
            value: Nothing
        """
        raise NotImplementedError

    @property
    def label(self) -> str:
        """Getter for the label instance variable. Not implemented for this object

        Returns:
            str: Nothing
        """
        raise NotImplementedError

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable. Not implemented for this object.

        Args:
            value: Nothing
        """
        raise NotImplementedError

    @classmethod
    def parse_dict(
        cls,
        object_dict=Dict,
        file_path=str,
    ) -> "PackageObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a PackageObject
            file_path (str): the file location of the source
        Returns:
            PackageObject: a new column object
        """
        approved_dict = cls._get_required(
            inbound_dict=object_dict, req_keys=cls._required_keys, file_path=file_path
        )

        optionals_existing = {
            key: object_dict[key] for key in cls._optional_keys if key in object_dict
        }

        approved_dict.update(optionals_existing)

        approved_dict["packages"] = []
        for package in object_dict.get("packages", []):
            typedDict = SubPackageObject.parse_dict(package, file_path)
            approved_dict["packages"].append(typedDict)

        retObject = cls(**approved_dict)

        retObject._file_path = file_path
        retObject._object_dict = object_dict

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the package object back into a dictionary
        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)
        if self._packages is not None:
            ret_dict["packages"] = []
            for package in self._packages:
                ret_dict["packages"].append(package.to_export_dict())
        return ret_dict
