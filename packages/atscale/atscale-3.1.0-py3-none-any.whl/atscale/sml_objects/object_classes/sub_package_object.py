from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class SubPackageObject(SemanticObject):

    _required_keys = [
        "name",
        "url",
        "branch",
        "version",
    ]

    _optional_keys = []

    def __init__(
        self,
        name: str,
        url: str,
        branch: str,
        version: str,
    ):
        """A class representing the calculated members to incorporate in a given calculated group.

        Args:
            name (str): The name of the repository
            url (str): The URL for the repository
            branch (str): The specific branch from the repository to use
            version (str): The ID for a specific commit to use
        """

        self._object_type = SemanticObjectTypes.SUB_PACKAGE
        self._name = name

        self._url = url
        self._branch = branch
        self._version = version

        object_dict = {
            "name": self._name,
            "url": self._url,
            "branch": self._branch,
            "version": self._version,
        }

        self._object_dict = object_dict

    @property
    def name(self) -> str:
        """Getter for the name instance variable

        Returns:
            str: name of this package
        """
        return self._name

    @name.setter
    def name(
        self,
        value,
    ):
        """Setter for the name instance variable. This variable is final, you must construct a new SubPackageObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name is final; it cannot be altered."
        )

    @property
    def url(self) -> str:
        """Getter for the url instance variable

        Returns:
            str: The url of this package
        """
        return self._url

    @url.setter
    def url(
        self,
        value,
    ):
        """Setter for the url instance variable. This variable is final, you must construct a new SubPackageObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of url is final; it cannot be altered."
        )

    @property
    def branch(self) -> str:
        """Getter for the branch instance variable

        Returns:
            str: The branch this package refers to
        """
        return self._branch

    @branch.setter
    def branch(
        self,
        value,
    ):
        """Setter for the branch instance variable. This variable is final, you must construct a new SubPackageObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of branch is final; it cannot be altered."
        )

    @property
    def version(self) -> str:
        """Getter for the version instance variable

        Returns:
            str: The version of the branch this package refers to
        """
        return self._version

    @version.setter
    def version(
        self,
        value,
    ):
        """Setter for the version instance variable. This variable is final, you must construct a new SubPackageObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of version is final; it cannot be altered."
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
