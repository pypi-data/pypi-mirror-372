from abc import abstractmethod
from typing import Dict, List
from abc import ABC, abstractmethod

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject


class YamlObject(SemanticObject):
    """A class representing semantic objects that are exactly characterized by a single YAML
    file."""

    @abstractmethod
    def __init__(
        self,
    ):
        """Constructor for the class."""
        raise NotImplementedError

    @property
    def label(self) -> str:
        """Getter for the label instance variable

        Returns:
            str: The label of this object
        """
        return self._label

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable.
        Args:
            value: The value to which label will be set
        """
        self._label = value
        self._object_dict["label"] = value

    @property
    def file_path(
        self,
    ) -> str:
        """The file path at which the YAMLObject's corresponding .yml/.yaml file is located.
        Returns:
            str: The file path.
        """
        return self._file_path

    @file_path.setter
    def file_path(
        self,
        value,
    ):
        """Setter for the file_path instance variable. This variable is final, please construct a new YAMLObject.
        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of file_path is final; it cannot be altered."
        )
