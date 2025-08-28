# -*- coding: utf-8 -*-

"""
Handles Genius Project files.
Genius Project files are a standard ZIP file, with multiple NP files inside containing
the tensors, and one JSON file containing the graph structure.
The JSON file is identical to that of a standalone VFG JSON file, but the tensors
have been externalized via "factor-name-quality" mapping
"""

# backwards compatability for handling partial migrations.
# will likely be removed before release, but is useful for scaffolding and testing.
from .serialization_backwards_compat import (
    load_project_050 as load_project_050,
    save_project_050 as save_project_050,
)
