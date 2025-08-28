# -*- coding: utf-8 -*-
from typing import Union
import json

from deprecation import deprecated
import importlib.metadata

from ...errors import JsonSerializationError
from ..v_0_2_0.vfg_0_2_0 import migrate as migrate_from_0_2_0
from .vfg_0_5_0 import VFG

VERSION = importlib.metadata.version("pyvfg")


@deprecated(
    deprecated_in="6.0.1",
    removed_in="7.0.0",
    current_version=VERSION,
    details="Use pydantic json schema creation instead",
)
def vfg_to_json_schema(indent: int = 2) -> tuple[dict, str]:
    vfg_schema_dict: dict = VFG.model_json_schema()
    vfg_schema_json = json.dumps(vfg_schema_dict, indent=indent)
    return vfg_schema_dict, vfg_schema_json


def vfg_from_json(json_data: Union[dict, str]) -> VFG:
    """
    See vfg_upgrade
    :param json_data: The json data to up-convert
    :return: The VFG data
    """
    import pydantic_core

    # this try/except is required to coerce the return type to JsonSerializationError for backwards compatibility
    try:
        return vfg_upgrade(json_data)
    except pydantic_core._pydantic_core.ValidationError as e:
        raise JsonSerializationError(message=str(e)) from e


def vfg_upgrade(json_data: Union[dict, str]) -> VFG:
    """
    Upgrades the incoming VFG from JSON data to the latest version supported.
    This calls migrate methods to update from earlier versions to the latest version.
    :param json_data: Incoming json data, in either dictionary or string format
    :return: A VFG object, in the latest schema.
    """
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    if not isinstance(json_data, dict):
        raise AttributeError("json_data must be dict or str")

    if json_data["version"] == "0.2.0":
        json_data = migrate_from_0_2_0(json_data)
    elif json_data["version"] in ["0.3.0", "0.4.0"]:
        # Currently, only the version will be updated
        json_data["version"] = "0.5.0"
    else:
        if json_data["version"] != "0.5.0":
            raise ValueError(f"Unsupported VFG version: {json_data['version']}")

    import pydantic_core

    try:
        return VFG(**json_data)
    except pydantic_core._pydantic_core.ValidationError as e:
        raise JsonSerializationError(message=str(e)) from e


@deprecated(
    deprecated_in="6.0.1",
    removed_in="7.0.0",
    current_version=VERSION,
    details="Use pydantic JSON conversions instead",
)
def vfg_from_dict(dict_data: dict) -> VFG:
    return VFG(**dict_data)


@deprecated(
    deprecated_in="6.0.1",
    removed_in="7.0.0",
    current_version=VERSION,
    details="Use pydantic JSON conversions instead",
)
def vfg_to_json(vfg: VFG, indent: int = 2) -> str:
    return vfg.model_dump_json(indent=indent)
