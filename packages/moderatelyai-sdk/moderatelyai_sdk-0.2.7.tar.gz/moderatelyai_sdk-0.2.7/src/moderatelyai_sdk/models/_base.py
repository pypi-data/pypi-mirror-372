"""Base model class for all SDK models."""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .._base_client import BaseClient


class BaseModel:
    """Base class for all SDK model objects.

    Provides common functionality for models that wrap API data and provide
    rich methods for interacting with the API.
    """

    def __init__(self, data: Dict[str, Any], client: "BaseClient") -> None:
        """Initialize the model with API data and client reference.

        Args:
            data: Raw API response data
            client: Client instance for making API calls
        """
        self._data = data
        self._client = client

    def _refresh(self) -> None:
        """Refresh the model data by fetching from the API.

        This method should be overridden by subclasses to implement
        the specific refresh logic for each model type.
        """
        raise NotImplementedError("Subclasses must implement _refresh")

    def to_dict(self) -> Dict[str, Any]:
        """Return the raw API data as a dictionary.

        Returns:
            The underlying API data dictionary
        """
        return dict(self._data)

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        class_name = self.__class__.__name__
        if hasattr(self, "id") or hasattr(self, "dataset_id"):
            id_field = getattr(self, "id", None) or getattr(self, "dataset_id", None)
            return f"{class_name}(id='{id_field}')"
        return f"{class_name}()"
