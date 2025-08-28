from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class MapObject(SemanticObject):
    _required_keys = [
        "field_terminator",
        "key_terminator",
        "key_type",
        "value_type",
    ]
    _optional_keys = [
        "is_prefixed",
    ]

    def __init__(
        self,
        field_terminator: str,
        key_terminator: str,
        key_type: str,
        value_type: str,
        is_prefixed: bool = None,
    ):
        """Represents a column map

        Args:
            field_terminator (str): The field termination character.
            key_terminator (str): The key termination character.
            key_type (str): The type of the key field.
            value_type (str): The type of the value field.
            is_prefixed (bool, optional): Whether the first character is delimited. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.MAP

        self._field_terminator = field_terminator
        self._key_terminator = key_terminator
        self._key_type = key_type
        self._value_type = value_type
        self._is_prefixed = is_prefixed

        self._object_dict = {
            "field_terminator": self._field_terminator,
            "key_terminator": self._key_terminator,
            "key_type": self._key_type,
            "value_type": self._value_type,
        }
        if self._is_prefixed is not None:
            self._object_dict["is_prefixed"] = self._is_prefixed

    @property
    def value_type(self) -> str:
        """Getter for the value_type instance variable

        Returns:
            str: The value_type of this map
        """
        return self._value_type

    @value_type.setter
    def value_type(
        self,
        value,
    ):
        """Setter for the value_type instance variable. This variable is final, you must construct a new MapObject.

        Args:
            value: value_type setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of value_type is final; it cannot be altered."
        )

    @property
    def is_prefixed(self) -> bool:
        """Getter for the is_prefixed instance variable

        Returns:
            str: The is_prefixed of this map
        """
        return self._is_prefixed

    @is_prefixed.setter
    def is_prefixed(
        self,
        value,
    ):
        """Setter for the is_prefixed instance variable. This variable is final, you must construct a new MapObject.

        Args:
            value: is_prefixed setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of is_prefixed is final; it cannot be altered."
        )

    @property
    def key_terminator(self) -> str:
        """Getter for the key_terminator instance variable

        Returns:
            str: The key_terminator of this map
        """
        return self._key_terminator

    @key_terminator.setter
    def key_terminator(
        self,
        value,
    ):
        """Setter for the key_terminator instance variable. This variable is final, you must construct a new MapObject.

        Args:
            value: key_terminator setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of key_terminator is final; it cannot be altered."
        )

    @property
    def field_terminator(self) -> str:
        """Getter for the field_terminator instance variable

        Returns:
            str: The field_terminator of this map
        """
        return self._field_terminator

    @field_terminator.setter
    def field_terminator(
        self,
        value,
    ):
        """Setter for the field_terminator instance variable. This variable is final, you must construct a new MapObject.

        Args:
            value: field_terminator setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of field_terminator is final; it cannot be altered."
        )

    @property
    def key_type(self) -> str:
        """Getter for the key_type instance variable

        Returns:
            str: The key_type of this map
        """
        return self._key_type

    @key_type.setter
    def key_type(
        self,
        value,
    ):
        """Setter for the key_type instance variable. This variable is final, you must construct a new MapObject.

        Args:
            value: key_type setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of key_type is final; it cannot be altered."
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
