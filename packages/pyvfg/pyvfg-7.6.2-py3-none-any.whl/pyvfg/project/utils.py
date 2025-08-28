import io
import json
import zipfile
from typing import List, Dict, Any

import numpy as np

from pyvfg.project.model import GeniusProjectFile, MANIFEST_FILE_NAME


def load_single_tensor(zf: zipfile.ZipFile, prefix: str, name: str) -> np.ndarray:
    """
    Loads a single tensor from the zip file, in the given prefix directory.
    Args:
        zf: The zip file containing the GeniusProjectFile.
        prefix: The prefix directory where the tensor is located. In the context of a GeniusProjectFile, this is the model name.
        name: The name of the tensor file (without the .np extension).
    Returns:
        The numpy array loaded from the tensor file.
    """
    if not name.endswith(".npy"):
        name += ".npy"
    with zf.open(f"{prefix}/tensors/{name}", mode="r") as f:
        return np.load(f, allow_pickle=False, encoding="bytes")


def get_models_list(zf: zipfile.ZipFile) -> List[str]:
    """
    Reads the manifest.txt file from the zip file and returns a list of model names.

    Args:
        zf: The zip file containing the GeniusProjectFile.
    Returns:
        A list of the models contained in the zipped GeniusProjectFile.
    """
    with zf.open(MANIFEST_FILE_NAME, mode="r") as mf:
        return [line.decode("utf-8").strip() for line in mf.readlines()]


def write_vfg_pieces_to_gpf(
    file: GeniusProjectFile,
    model_name: str,
    vfg_json: Dict[str, Any],
    tensors: Dict[str, np.ndarray],
    viz_metadata: Dict[str, Any],
) -> None:
    # save the JSON and NP files
    with zipfile.ZipFile(file, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # write the manifest
        with zf.open(MANIFEST_FILE_NAME, mode="w") as mf:
            mf.write(f"{model_name}\n".encode("utf-8"))

        # write the model json, into the appropriate folder
        with zf.open(f"{model_name}/vfg.json", mode="w") as f:
            text_stream = io.TextIOWrapper(f, encoding="utf-8", write_through=True)
            json.dump(vfg_json, text_stream)

        # write all tensors to the zip file, indexed by name
        for tensor_name, tensor in tensors.items():
            if not tensor_name.endswith(".npy"):
                tensor_name += ".npy"
            with zf.open(f"{model_name}/tensors/{tensor_name}", mode="w") as f:
                np.save(f, tensor)

        # write visualization metadata
        with zf.open(f"{model_name}/visualization_metadata.json", "w") as f:
            text_stream = io.TextIOWrapper(f, encoding="utf-8", write_through=True)
            json.dump(viz_metadata, text_stream)
