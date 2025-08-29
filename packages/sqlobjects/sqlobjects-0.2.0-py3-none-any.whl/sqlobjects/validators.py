"""SQLObjects Validators Module - Field validation system"""

from abc import ABC, abstractmethod
from typing import Any

from .exceptions import ValidationError


__all__ = [
    "FieldValidator",
    "LengthValidator",
    "RangeValidator",
    "EmailValidator",
    "validate_field_value",
]


class FieldValidator(ABC):
    """Base class for field validators.

    This abstract base class defines the interface for all field validators
    in the SQLObjects system. Validators are used to ensure data integrity
    and enforce business rules on model fields.

    Examples:
        >>> class CustomValidator(FieldValidator):
        ...     def validate(self, value: Any, field_name: str) -> Any:
        ...         if value and len(str(value)) < 3:
        ...             raise ValidationError(self.get_error_message(field_name, value))
        ...         return value
        ...
        ...     def get_error_message(self, field_name: str, value: Any) -> str:
        ...         return f"Field '{field_name}' must be at least 3 characters long"
    """

    @abstractmethod
    def validate(self, value: Any, field_name: str) -> Any:
        """Validate and return the processed value.

        Args:
            value: The value to validate
            field_name: Name of the field being validated

        Returns:
            The validated (and potentially transformed) value

        Raises:
            ValidationError: If validation fails
        """
        pass

    @abstractmethod
    def get_error_message(self, field_name: str, value: Any) -> str:
        """Get the error message for validation failure.

        Args:
            field_name: Name of the field that failed validation
            value: The value that failed validation

        Returns:
            Human-readable error message
        """
        pass


class LengthValidator(FieldValidator):
    """Validator for string/value length constraints.

    This validator ensures that the string representation of a value
    meets minimum and/or maximum length requirements.

    Args:
        min_length: Minimum required length (default: 0)
        max_length: Maximum allowed length (optional)

    Examples:
        >>> # Username must be 3-20 characters
        >>> username_validator = LengthValidator(min_length=3, max_length=20)
        >>> username_validator.validate("john", "username")  # Valid
        >>> username_validator.validate("jo", "username")  # Raises ValidationError

        >>> # Description must be at least 10 characters
        >>> desc_validator = LengthValidator(min_length=10)
        >>> desc_validator.validate("Short desc", "description")  # Valid
    """

    def __init__(self, min_length: int = 0, max_length: int | None = None):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any, field_name: str) -> Any:
        """Validate the length of the value.

        Args:
            value: The value to validate
            field_name: Name of the field being validated

        Returns:
            The original value if validation passes

        Raises:
            ValidationError: If the value length is outside the allowed range
        """
        if value is None:
            return value

        length = len(str(value))
        if length < self.min_length:
            raise ValidationError(self.get_error_message(field_name, value))
        if self.max_length and length > self.max_length:
            raise ValidationError(self.get_error_message(field_name, value))

        return value

    def get_error_message(self, field_name: str, value: Any) -> str:
        """Get the error message for length validation failure.

        Args:
            field_name: Name of the field that failed validation
            value: The value that failed validation

        Returns:
            Human-readable error message describing the length requirement
        """
        if self.max_length:
            return f"Field '{field_name}' length must be between {self.min_length} and {self.max_length}"
        return f"Field '{field_name}' length must be at least {self.min_length}"


class RangeValidator(FieldValidator):
    """Validator for numeric range constraints.

    This validator ensures that numeric values fall within specified
    minimum and/or maximum bounds. The value is converted to float
    for comparison.

    Args:
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)

    Examples:
        >>> # Age must be between 0 and 150
        >>> age_validator = RangeValidator(min_value=0, max_value=150)
        >>> age_validator.validate(25, "age")  # Valid
        >>> age_validator.validate(-5, "age")  # Raises ValidationError

        >>> # Price must be at least 0
        >>> price_validator = RangeValidator(min_value=0)
        >>> price_validator.validate(19.99, "price")  # Valid
    """

    def __init__(self, min_value: float | None = None, max_value: float | None = None):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any, field_name: str) -> Any:
        """Validate the numeric range of the value.

        Args:
            value: The value to validate
            field_name: Name of the field being validated

        Returns:
            The original value if validation passes

        Raises:
            ValidationError: If the value is not numeric or outside the allowed range
        """
        if value is None:
            return value

        try:
            num_value = float(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Field '{field_name}' must be a number") from e

        if self.min_value is not None and num_value < self.min_value:
            raise ValidationError(self.get_error_message(field_name, value))
        if self.max_value is not None and num_value > self.max_value:
            raise ValidationError(self.get_error_message(field_name, value))

        return value

    def get_error_message(self, field_name: str, value: Any) -> str:
        """Get the error message for range validation failure.

        Args:
            field_name: Name of the field that failed validation
            value: The value that failed validation

        Returns:
            Human-readable error message describing the range requirement
        """
        if self.min_value is not None and self.max_value is not None:
            return f"Field '{field_name}' must be between {self.min_value} and {self.max_value}"
        elif self.min_value is not None:
            return f"Field '{field_name}' must be at least {self.min_value}"
        else:
            return f"Field '{field_name}' must be at most {self.max_value}"


class EmailValidator(FieldValidator):
    """Validator for email address format.

    This validator performs basic email format validation by checking
    for the presence of '@' symbol and a dot in the domain part.
    For production use, consider using more comprehensive email
    validation libraries.

    Examples:
        >>> email_validator = EmailValidator()
        >>> email_validator.validate("user@example.com", "email")  # Valid
        >>> email_validator.validate("invalid-email", "email")  # Raises ValidationError
        >>> email_validator.validate("user@domain", "email")  # Raises ValidationError
    """

    def validate(self, value: Any, field_name: str) -> Any:
        """Validate the email address format.

        Args:
            value: The value to validate
            field_name: Name of the field being validated

        Returns:
            The original value if validation passes

        Raises:
            ValidationError: If the value is not a valid email format
        """
        if value is None:
            return value

        email_str = str(value)
        if "@" not in email_str or "." not in email_str.split("@")[-1]:
            raise ValidationError(self.get_error_message(field_name, value))

        return value

    def get_error_message(self, field_name: str, value: Any) -> str:
        """Get the error message for email validation failure.

        Args:
            field_name: Name of the field that failed validation
            value: The value that failed validation

        Returns:
            Human-readable error message for invalid email format
        """
        return f"Field '{field_name}' must be a valid email address"


def validate_field_value(validators: list[Any], value: Any, field_name: str) -> Any:
    """Validate a field value using a list of validators.

    This function applies multiple validators to a field value in sequence.
    It supports both FieldValidator instances and simple callable functions.

    Args:
        validators: List of validators to apply
        value: The value to validate
        field_name: Name of the field being validated

    Returns:
        The validated (and potentially transformed) value

    Raises:
        ValidationError: If any validator fails

    Examples:
        >>> validators = [LengthValidator(min_length=3, max_length=50), EmailValidator()]
        >>> validate_field_value(validators, "user@example.com", "email")
        'user@example.com'

        >>> # Using simple function validator
        >>> def no_spaces(value):
        ...     if " " in str(value):
        ...         raise ValueError("No spaces allowed")
        ...     return value
        >>> validate_field_value([no_spaces], "username", "username")
        'username'
    """
    for validator in validators:
        if isinstance(validator, FieldValidator):
            value = validator.validate(value, field_name)
        elif callable(validator):
            # Support for simple function validators
            try:
                result = validator(value)
                if result is not None:
                    value = result
            except Exception as e:
                raise ValidationError(f"Validation failed for {field_name}: {e}") from e

    return value
