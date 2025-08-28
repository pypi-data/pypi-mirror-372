# -*- coding: utf-8 -*-
import json
import typing
import zipfile
from typing import Dict, List, Any

from .model import GeniusProjectFile, MANIFEST_FILE_NAME
from .utils import load_single_tensor, get_models_list, write_vfg_pieces_to_gpf
from ..versions.v_0_5_0.vfg_0_5_0 import VFG as VFG_0_5_0


def load_project_050(file: GeniusProjectFile) -> List[VFG_0_5_0]:
    """
    Backwards-compatible (0.5.0) handling of a VFG project file.
    Will load a Genius Project File into a VFG 0.5.0, with merged
    tensors.
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
            # Get the factor files
            if "factors" in vfg_json:
                for factor in vfg_json["factors"]:
                    if "counts" in factor and factor["counts"] is not None:
                        factor["counts"] = load_single_tensor(zf, prefix, factor["counts"])
                    if "values" in factor and factor["values"] is not None:
                        factor["values"] = load_single_tensor(zf, prefix, factor["values"])
            with zf.open(f"{prefix}/visualization_metadata.json") as f:
                # Load the visualization metadata
                viz_metadata = json.load(f)
                # Add the visualization metadata to the VFG
                vfg_json["visualization_metadata"] = viz_metadata
            # and finally, load the dict into a single model
            models.append(VFG_0_5_0.from_dict(vfg_json))
    # create the VFG from the JSON
    return models


def save_project_050(vfg: VFG_0_5_0, file: GeniusProjectFile, model_name: typing.Optional[str] = None) -> None:
    """
    Backwards-compatible (0.5.0) saving of a VFG project file.
    Will save a VFG 0.5.0 into a Genius Project File, with externalized tensors.
    """
    if model_name is None:
        model_name = "model1"
    # create the NPZ file
    tensors = {}
    for factor in vfg.factors:
        factor_name = "-".join(factor.variables)
        if factor.counts is not None:
            # save the counts tensor to the NPY file
            tensors[factor_name + "-counts"] = factor.counts
        if factor.values is not None:
            # save the values tensor to the NPY file
            tensors[factor_name + "-values"] = factor.values
    # create the JSON file
    vfg_json = vfg.copy_without_tensors().model_dump()
    # fix up the vfg json with the factor values
    for factor in vfg_json["factors"]:
        if factor["variables"] is None:
            continue
        factor_name = "-".join(factor["variables"])
        if "counts" in factor and factor["counts"] is not None:
            factor["counts"] = factor_name + "-counts"
        if "values" in factor and factor["values"] is not None:
            factor["values"] = factor_name + "-values"
    # remove the visualization metadata
    if "visualization_metadata" in vfg_json:
        viz_metadata = vfg_json["visualization_metadata"]
        del vfg_json["visualization_metadata"]
    else:
        viz_metadata = {}

    write_vfg_pieces_to_gpf(file, model_name, vfg_json, tensors, viz_metadata)


def _add_if_not_in(list1: List[Any], list2: List[Any]) -> None:
    """
    Adds elements from list2 to list1 if they are not already present in list1.
    """
    for item in list2:
        if item not in list1:
            list1.append(item)


def merge_project_files(input_projects: List[GeniusProjectFile], output_project: GeniusProjectFile) -> None:
    """
    Merges two or more project files into a single project file.
    The output file cannot be an input file.
    Later models in input will overwrite earlier models in input.
    """
    if output_project in input_projects:
        raise ValueError("Output file cannot be an input file")
    all_models = []
    with zipfile.ZipFile(output_project, "w") as outf:
        for input_fn in input_projects:
            with zipfile.ZipFile(input_fn, "r") as inf:
                # read manifest at root level to see the list of models we have available
                with inf.open(MANIFEST_FILE_NAME, mode="r") as mf:
                    _add_if_not_in(
                        all_models,
                        [line.decode("utf-8").strip() for line in mf.readlines()],
                    )
                for name in inf.namelist():
                    if name == MANIFEST_FILE_NAME:
                        continue
                    # copy the file to the output file
                    outf.writestr(name, inf.read(name))
        outf.writestr(MANIFEST_FILE_NAME, "\n".join(all_models).encode("utf-8"))
