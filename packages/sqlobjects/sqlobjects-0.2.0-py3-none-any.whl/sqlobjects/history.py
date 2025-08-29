"""SQLObjects History Tracking Module - Field change history tracking"""

from datetime import datetime
from typing import Any


__all__ = [
    "HistoryTrackingMixin",
    "FieldHistory",
    "get_field_history",
]


class FieldHistory:
    """Field change history record"""

    def __init__(self, old_value: Any, new_value: Any, timestamp: datetime | None = None):
        self.old_value = old_value
        self.new_value = new_value
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        return f"FieldHistory(old={self.old_value!r}, new={self.new_value!r}, time={self.timestamp})"


class HistoryTrackingMixin:
    """History tracking mixin class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._field_history: dict[str, list[FieldHistory]] = {}
        self._history_initialized = False
        self._initialize_field_tracking()
        self._history_initialized = True

    def _initialize_field_tracking(self) -> None:
        """Initialize tracking for fields with active history"""
        # Get field names from model class
        if hasattr(self, "_get_field_names"):
            for name in self._get_field_names():  # type: ignore[reportAttributeAccessIssue]
                # Skip private fields
                if name.startswith("_"):
                    continue

                field_attr = getattr(self.__class__, name, None)
                if hasattr(field_attr, "has_active_history") and field_attr.has_active_history:  # type: ignore[reportAttributeAccessIssue]
                    self._field_history[name] = []

    def __setattr__(self, name: str, value: Any) -> None:
        # Track field changes only after initialization
        if (
            not name.startswith("_")
            and hasattr(self, "_field_history")
            and hasattr(self, "_history_initialized")
            and self._history_initialized
            and name in self._field_history
        ):
            old_value = getattr(self, name, None)
            if old_value != value:
                history_record = FieldHistory(old_value, value)
                self._field_history[name].append(history_record)

        super().__setattr__(name, value)

    def get_field_history(self, field_name: str) -> list[FieldHistory]:
        """Get field change history"""
        return self._field_history.get(field_name, [])

    def get_field_history_dict(self, field_name: str) -> list[dict[str, Any]]:
        """Get field change history in dictionary format"""
        history = self.get_field_history(field_name)
        return [record.to_dict() for record in history]

    def clear_field_history(self, field_name: str) -> None:
        """Clear history for specific field"""
        if field_name in self._field_history:
            self._field_history[field_name].clear()

    def clear_all_history(self) -> None:
        """Clear history for all fields"""
        for field_name in self._field_history:
            self._field_history[field_name].clear()

    def get_all_field_history(self) -> dict[str, list[dict[str, Any]]]:
        """Get history for all tracked fields"""
        return {field_name: self.get_field_history_dict(field_name) for field_name in self._field_history}


def get_field_history(instance: Any, field_name: str) -> list[FieldHistory]:
    """Get field history from instance"""
    if hasattr(instance, "get_field_history"):
        return instance.get_field_history(field_name)
    return []
