"""Base dataclass / model for SDK."""

from dataclasses import dataclass, fields
from typing import Any, TypeVar
from uuid import UUID

from dateutil import parser

T = TypeVar("T", bound="Model")


def _parse_datetime(date_as_string, _):
    return parser.isoparse(date_as_string) if date_as_string else None


def _parse_uuid(uuid_as_string, _):
    return UUID(uuid_as_string) if uuid_as_string else None


def _read_nested(data, type_var):
    return type_var.from_api(data) if data is not None else None


def _read_nested_list(data, type_var):
    return [_read_nested(item, type_var) for item in data] if data is not None else None


def _parse_enum(data, enum_var):
    return enum_var[data] if data else None


def _identity_function(value, _):
    return value


TYPE_MAP = {
    "datetime": _parse_datetime,
    "uuid": _parse_uuid,
    "type": _read_nested,
    "listtype": _read_nested_list,
    "enum": _parse_enum,
}


def _to_iso_date_string(datetime_data, _):
    return datetime_data.strftime("%Y-%m-%dT%H:%M:%SZ") if datetime_data else None


def _to_uuid_string(uuid_data, _):
    return str(uuid_data) if uuid_data else None


def _write_nested(data, _):
    return data.to_api() if data is not None else None


def _write_nested_list(data, type_var):
    return [_write_nested(item, type_var) for item in data] if data is not None else None


def _to_str(data, _):
    """Convert to string representation.

    The odd case here, writing bool as a string, is only used for HTTP headers.
    """
    if data is None:
        return None
    if data is True:
        return "true"
    if data is False:
        return "false"
    return str(data)


def _to_enum_name(data, _):
    return data.name if data is not None else None


REVERSE_TYPE_MAP = {
    "datetime": _to_iso_date_string,
    "uuid": _to_uuid_string,
    "type": _write_nested,
    "listtype": _write_nested_list,
    "str": _to_str,
    "enum": _to_enum_name,
}


@dataclass
class Model:
    """Base dataclass / model for SDK."""

    @classmethod
    def from_api(cls: type[T], data: dict[str, Any]) -> T:
        """Read values from JSON dict and map to model fields.

        Args:
            data: The data to initialize the instance from.

        Returns:
            An instance of the model.
        """
        field_data = [
            (
                f.name,
                f.metadata.get("api_name"),
                f.metadata.get("transform", ""),
                f.metadata.get("type"),
            )
            for f in fields(cls)
            if f.init
        ]
        mapper = {
            api_name or name: (name, datatype, type_var)
            for (name, api_name, datatype, type_var) in field_data
        }
        field_list = mapper.keys()
        kwargs = {
            name: mapped_value
            for (name, datatype, type_var, value) in (
                (*mapper[k], v) for k, v in data.items() if k in field_list
            )
            if (mapped_value := TYPE_MAP.get(datatype, _identity_function)(value, type_var))
            is not None
        }

        return cls(**kwargs)

    def to_api(self) -> dict[str, Any]:
        """Map model field names and values to JSON Dict.

        Returns:
            Representation of object (and any nested objects) as a dictionary that can be passed as
            the JSON body of an API request.
        """
        field_data = [
            (
                f.name,
                f.metadata.get("api_name"),
                f.metadata.get("transform", ""),
                f.metadata.get("type"),
            )
            for f in fields(self)
            if f.init
        ]
        data = {
            api_name or name: mapped_value
            for (name, api_name, datatype, type_var) in field_data
            if (
                mapped_value := REVERSE_TYPE_MAP.get(datatype, _identity_function)(
                    getattr(self, name), type_var
                )
            )
            is not None
        }
        return data
