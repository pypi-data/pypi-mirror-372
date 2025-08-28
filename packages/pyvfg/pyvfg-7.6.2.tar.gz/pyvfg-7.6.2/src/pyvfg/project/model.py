from pathlib import Path
from typing import Union, BinaryIO

MANIFEST_FILE_NAME = "manifest.txt"

GeniusProjectFile = Union[str, BinaryIO, Path]
"""
A GeniusProjectFile can be a path to a file, a file-like object, or a string representing the file path.
In essence, it is a zip file containing the following structure:
- manifest.txt: A manifest for the project file, listing the folders expected to be models. One per line, UTF-8, UNIX line endings.
    This allows folders to exist that are not models. 
    Assuming that manifest.txt has one line, "model1", the following files are expected:
    - model1/vfg.json: The JSON version of the VFG
    - model1/tensors/${key}.np: The numpy tensors for the VFG.
        An npz is just a zip of np files! We don't want to compress twice, so we do this instead.
        These are stored separately to be easier to load individually (and in javascript)
        The name of the tensor is the key to access it with
    - model1/visualization_metadata.json: Previously "visualization_metadata" in the top-level VFG
    Any other streams are allowed, but will not be produced or parsed by GPIL tools
"""
