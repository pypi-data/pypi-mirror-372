# -*- coding: utf-8 -*-
import json
import zipfile
from typing import List, Any, Dict, Optional

from .model import GeniusProjectFile
from .utils import write_vfg_pieces_to_gpf, get_models_list, load_single_tensor
from ..versions.v_2_0_0.vfg_2_0_0 import VFG as VFG_2_0_0


def load_project_200(file: GeniusProjectFile) -> List[VFG_2_0_0]:
    """
    Will load a Genius Project File into a VFG 2.0.0, with loaded tensors.
    """

    models = []
    with zipfile.ZipFile(file, "r") as zf:
        # read manifest at root level to see the list of models we have available
        model_prefixes: List[str] = get_models_list(zf)

        # for each model name ("prefix") in the manifest
        for prefix in model_prefixes:
            # Get the JSON file
            with zf.open(f"{prefix}/vfg.json") as f:
                vfg_json: Dict[str, Any] = json.load(f)

            # load the variable's tensors
            var_values = {"observation": {}, "messages": {}}
            if "variables" in vfg_json:
                for var_name, var in vfg_json["variables"].items():
                    if "observation" in var and var["observation"] is not None:
                        var_values["observation"][var_name] = load_single_tensor(zf, prefix, var["observation"])
                    if "messages" in var and var["messages"] is not None:
                        var_values["messages"][var_name] = load_single_tensor(zf, prefix, var["messages"])

            # and finally, load the dict into a single model
            vfg = VFG_2_0_0.from_dict(vfg_json)
            vfg._name = prefix
            for var_name, observation_values in var_values["observation"].items():
                vfg.variables[var_name].observation_values = observation_values
            for var_name, messages_values in var_values["messages"].items():
                vfg.variables[var_name].messages_values = messages_values
            models.append(vfg)

    return models


def save_project_200(vfg: VFG_2_0_0, file: GeniusProjectFile, model_name: Optional[str] = None) -> None:
    """
    Will save a VFG 2.0.0 into a Genius Project File, with externalized tensors.
    """

    if model_name is None:
        model_name = "model1"

    # collect all tensors from the VFG
    tensors = {}
    for var_name, variable in vfg.variables.items():
        # save the tensors to the .npy files
        if variable.observation_values is not None:
            tensor_name = f"{var_name}_observation.npy"
            tensors[tensor_name] = variable.observation_values
            vfg.variables[var_name].observation = tensor_name

        if variable.messages_values is not None:
            tensor_name = f"{var_name}_messages.npy"
            tensors[tensor_name] = variable.messages_values
            vfg.variables[var_name].messages = tensor_name

    # create the JSON file
    vfg_json = vfg.model_dump()
    viz_metadata = {}

    write_vfg_pieces_to_gpf(file, model_name, vfg_json, tensors, viz_metadata)
