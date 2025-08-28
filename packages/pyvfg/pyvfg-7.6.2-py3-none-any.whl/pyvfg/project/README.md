## GPF
GPF, or Genius Project Format, is a container format for VFGs. It is a zip file that contains the VFG and its associated files. It is used to store and share VFGs in a standardized format.

As decided in [ADR-0002](../../../decisions/ADR-0002-container.md), a given `model1` model, will produce a gpf file having the following structure
```
model1.gpf
    ├── manifest.txt
    └── model1/
        ├── tensors/
        │   ├── a.np
        │   └── b.np
        ├── vfg.json
        └── visualization_metadata.json
```
The manifest is a text file that lists the folders expected to be models, and the directory structure contains the VFG and its associated tensors files. Also, a `visualization_metadata.json` file is included, which contains metadata about the visualization of the model in the editor.