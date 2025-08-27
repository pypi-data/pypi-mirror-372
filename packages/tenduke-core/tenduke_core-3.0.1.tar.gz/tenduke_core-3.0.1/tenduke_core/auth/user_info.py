"""User info response data model."""

from dataclasses import dataclass, field
from typing import Optional

from ..base_model import Model


@dataclass
class UserInfo(Model):
    """User info response data model.

    Attributes:
        sub:
            Subject identitfier. A locally unique and never reassigned identifier within the issuer
            for the End-User.
        name:
            End-User's full name in displayable form including all name parts, possibly including
            titles and suffixes, ordered according to the End-User's locale and preferences.
        given_name:
            Given name(s) or first name(s) of the End-User. Note that in some cultures, people can
            have multiple given names; all can be present, with the names being separated by space
            characters.
        family_name:
            Surname(s) or last name(s) of the End-User. Note that in some cultures, people can have
            multiple family names or no family name; all can be present, with the names being
            separated by space characters.
        email: End-User's preferred e-mail address.
        formatted_name:
            Combination of names for display purposes. Shall contain a value if any identifier is
            populated.
    """

    sub: str
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    email: Optional[str] = None
    formatted_name: Optional[str] = field(init=False)

    def __post_init__(self):
        """Initialize formatted name based on other values."""
        if self.given_name and self.family_name:
            self.formatted_name = f"{self.given_name} {self.family_name}"
        else:
            self.formatted_name = self.name or self.email or self.sub
