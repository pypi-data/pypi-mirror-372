import json
from io import TextIOWrapper
from pathlib import Path
from typing import Union, Dict, Any, get_args

from .project.model import GeniusProjectFile
from .project.serialization_backwards_compat import load_project_050
from .versions.common import is_version_less_than
from .versions.v_0_5_0.vfg_0_5_0 import VFG as VFG_0_5_0
from .versions.v_0_5_0.vfg_0_5_0_utils import vfg_from_json as vfg_from_json_0_5_0
from .versions.v_2_0_0.vfg_2_0_0 import VFG as VFG_2_0_0
from .versions.v_2_1_0.vfg_2_1_0 import VFG as VFG_2_1_0

VFG = Union[VFG_0_5_0, VFG_2_0_0, VFG_2_1_0]


def load_model(data: VFG | GeniusProjectFile | TextIOWrapper | Dict[str, Any]) -> VFG:
    """
    Load a VFG model from various data types.

    Args:
        data (VFG | GeniusProjectFile | TextIOWrapper | Dict[str, Any]): The model data, which can be a VFG instance,
            a GeniusProjectFile, a dict, a JSON string, a file path to a JSON file, or an open file-like object.
    Returns:
        VFG: An instance of VFG (either VFG_0_5_0 or VFG_2_0_0) loaded from the provided data.
    """
    vfg_classes = get_args(VFG)
    if isinstance(data, vfg_classes):
        return data

    vfg_json = None
    if isinstance(data, str):
        try:
            if data.endswith(".json"):
                # Assume it's a JSON file path
                with open(data, "r") as f:
                    vfg_json = json.load(f)
            else:
                # Assume it's a JSON string
                vfg_json = json.loads(data)
        except json.JSONDecodeError:
            # this is not a valid JSON string or file
            pass
    elif isinstance(data, Path) and data.suffix == ".json":
        with open(data, "r") as f:
            vfg_json = json.load(f)
    elif isinstance(data, TextIOWrapper):
        # it may be an open json file, but can also be a gpf file
        try:
            vfg_json = json.load(data)
        except Exception:
            pass
    elif isinstance(data, dict):
        # if it's a dict, we assume it's already a VFG JSON representation
        vfg_json = data

    if vfg_json is not None:
        vfg_version = vfg_json.get("version", "")
        if vfg_version == "":
            raise ValueError("VFG JSON data must contain a 'version' field.")

        if is_version_less_than(vfg_version, "2.0.0"):
            return vfg_from_json_0_5_0(vfg_json)

        match vfg_version:
            case "2.0.0":
                return VFG_2_0_0(**vfg_json)
            case "2.1.0":
                return VFG_2_1_0(**vfg_json)
            case _:
                raise ValueError(f"Unsupported VFG version: {vfg_version}")

    if isinstance(data, TextIOWrapper):
        data = data.name

    if isinstance(data, GeniusProjectFile):
        try:
            try:
                # Assuming we always want the first model in the project file
                return load_project_050(data)[0]
            except Exception:
                return VFG_2_0_0.from_gpf(data)
        except Exception as e:
            raise ValueError(f"Bad data. The provided input is not a valid VFG or GeniusProjectFile: {data}") from e
    else:
        raise ValueError("Unsupported model data type. Must be VFG or GeniusProjectFile.")
