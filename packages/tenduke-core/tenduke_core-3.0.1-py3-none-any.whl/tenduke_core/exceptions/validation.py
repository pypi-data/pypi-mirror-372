"""Validation Errors."""


class InvalidArgumentError(ValueError):
    """The argument is missing or contains an invalid value."""

    def __init__(self, name: str):
        """Construct an InvalidArgumentError instance.

        Args:
             name: name of the missing argument.
        """
        super().__init__(f"Parameter '{name}' is invalid or missing")


class MissingConfigurationItemError(ValueError):
    """A required configuration item is missing."""

    def __init__(self, name: str, key: str):
        """Construct an MissingConfigurationItemError instance.

        Args:
             name: name of the missing configuration argument.
             key: key of the missing configuration argument.
        """
        super().__init__(f"Configuration missing {name} ({key})")


class DeviceCodeAuthorizationUrlMissingError(MissingConfigurationItemError):
    """The OIDC Device Core Authorization URL is missing."""

    def __init__(self):
        """Construct an DeviceCodeAuthorizationUrlMissingError instance."""
        super().__init__("device code authorization url", "idp_oauth_device_code_url")


class TokenUrlMissingError(MissingConfigurationItemError):
    """The OIDC Token URL is missing."""

    def __init__(self):
        """Construct an TokenUrlMissingError instance."""
        super().__init__("token url", "idp_oauth_token_url")


class UserInfoUrlMissingError(MissingConfigurationItemError):
    """The OIDC User Info URL is missing."""

    def __init__(self):
        """Construct an UserInfoUrlMissingError instance."""
        super().__init__("userinfo url", "idp_userinfo_url")


class IdTokenMissingError(ValueError):
    """No id_token is present."""

    def __init__(self):
        """Construct an IdTokenMissingError instance."""
        super().__init__("Cannot provide authorization when no id_token is present.")
