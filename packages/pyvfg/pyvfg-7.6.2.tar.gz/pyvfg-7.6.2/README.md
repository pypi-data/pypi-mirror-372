# pyvfg

This package declares and defines a class `VFG` that represents a Verses Factor Graph. It supports python versions 3.11,
3.12, and 3.13. The wide version support is necessary so that downstream clients, such as the SDK, can continue to
support the python versions required by popular ML packages.

## Working with this Repository
This repository and its tests may use files using Git LFS (Large File Storage). Please
[install Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage)
using the previous link and run `git lfs install` before cloning.\
After cloning, you can run `git lfs pull` to download the LFS files.

## What is a VFG?
VFGs, or Verses Factor Graphs, are a data structure that represents a probabilistic model. They are used to represent the relationships between variables in a model, and can be used to perform inference and learning. This is a generic structure that can be used to represent a variety of models, including Bayesian networks, Markov random fields, and partially-observable Markov decision processes (POMDPs).

VFG 2.0.0 implements a variant of the [Constrained Forney-style Factor Graph (CFFG)](https://arxiv.org/abs/2306.08014), which allows specification of constraints on the inference procedure for the model, as well as model structure.

### Versioning
>Latest version is **2.0.0**, released on 10 July 2025.

VFG versions are, in general, backwards-compatible -- calling `pyvfg.vfg_upgrade()` on
a 0.2.0 VFG will produce a valid VFG on the latest version. However, one exception is <= 0.4.0 POMDPs to 0.5.0 POMDPs. Please see below
for how to upgrade the POMDPs.

#### Upgrading POMDPs from 0.4.0 to 0.5.0 and above
VFG 0.5.0 introduces numeric validation for factor values. This means that POMDPs that use "categorical" for their
reward factor will fail validation. As such, the model will need to be updated.

To upgrade a POMDP from 0.4.0 to 0.5.0, you will need to change the reward factor from `"categorical"` to `"logits"`.

#### VFG 2.0.0 paradigm shift
VFG 2.0.0 introduces a paradigm shift in how VFGs are represented. The new format, based on [CFFG](https://arxiv.org/abs/2306.08014), is more flexible and allows for richer representations of models.

### Model Description
Model types explicitly supported by VFG up to 0.5.0 are Bayesian Networks (BNs), Markov Random Fields (MRFs), and Partially-Observable Markov Decision Processes (POMDPs).
VFG 2.0.0 can represent any model composed of exponential family distributions, including the preceding model types but also Gaussian and linear Gaussian models, mixture models, hidden Markov models, and models including custom functions.

## Version
Determines how the model will be parsed, for backwards compatability when using durable storage. New or updated models will be output as 2.0.0.

## Variables
Variables represent unknown entities or quantities in a model. These may include objects, properties, actions, or events that the model represents, and also parameters that influence relationships among other variables.
The main use of a model is to infer distributions over variables. Variables may also be _observed_ in which case they represent known datapoints.
The `domain` of a variable is the range of possible values it can take. For example, a variable representing a magnitude may take any positive real value. Variables may also represent groups of related numbers
(vectors or matrices), or one of a set of alternatives (discrete variables).

### Variable Roles

In VFG 0.5.0, the following roles specify special types of variables:

| Role            | Model Type     | Description                                                             |
|-----------------|----------------|-------------------------------------------------------------------------|
| null            | BN, MRF, POMDP | a "default" variable without a role.                                    |
| `latent`        | BN, MRF        | A variable known to be present in the system, but cannot be observed.   | 
| `control_state` | POMDP          | A special kind of latent variable used for control or action selection. |

VFG 2.0.0 retains only `control_state` as a Boolean indicator.

## Factors
Factors represent functions of zero or more variables, which compose into a factor graph. Intuitively, these represent the relationships among variables in the model.
They have at least one "output" variable and zero or more input variables (parameters).

### Possible Function Types

Factors typically represent probabilistic relationships (e.g. probability density functions), so their names often correspond to probability distributions such as `gaussian` or `categorical`, but more generally can represent any function.

(Note: the `function` field was called `distribution` in VFG <=0.5.0)

| Function              | Description                                                                                                                                                   
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `categorical`             | Categorical joint distribution over a set of variables. Joint probability of a single variable is simply the probability of that variable. |
| `conditional_categorical` | Categorical distribution conditioned on a set of variables. In 0.5.0, this was called `categorical_conditional` and the first variable in the factor list was the "target", e.g. `["A", "B", "C"]` means , e.g.`P(A\|B,C)`.  |
| `dirichlet`               | Distribution over probabilities (specifically, over the parameters of categorical distributions). |
| `gaussian`                | Normal distribution (bell-shaped curve). |
| `linear_gaussian`         | Gaussian that is a linear function of an input variable. |
| `mixture`                 | Generic mixture model (weighted average of several distributions of the same type). |
| `gmm`                     | Gaussian mixture model - allows compact specification of a very commonly used type of mixture model. |
| `wishart`                 | Distribution over covariance matrices (for multivariate Gaussian distributions). |
| `matrix_normal_wishart`   | A single distribution over both the mean and covariance of a multivariate Gaussian. |
| `softmax`                 | A function that normalizes an arbitrary set of real values (logits), yielding a categorical distribution. In VFG 0.5.0, this is marked using the `logits` disrtribution type.           |
| `mnlr`                    | Multinomial logistic regression node (converts continuous values to a categorical distribution). |
| `potential`               | Non-normalized probability distribution (similar to the logits of a softmax but constrained to be non-negative.) |
| `custom`                  | Placeholder for arbitrary user-specified functions. |

### Additional factor properties

`constraints` - specifies constraints on the inference procedure associated with a given factor.
`output` - lists the variable(s) in the VFG associated with the factor's output.
`parameters` - dictionary of named parameters for the function, whose values are variables specified in the VFG.
`control_target` - marks a special type of factor used as a target for control (action, planning, or policy selection) tasks, i.e. a goal, preference, or reward.

### Legacy fields (VFG 0.5.0 and below)

#### Factor Roles

In VFG <= 0.5.0, many model-type-specific factor roles are available:

| Role                  | Model Type     | Description                                                                                            |
|-----------------------|----------------|--------------------------------------------------------------------------------------------------------|
| null                  | BN, MRF, POMDP | A "default" factor without a role.                                                                     |
| `transition`          | MRF, POMDP     | Represents the transition probabilities between states, optionally conditioned on an action.          |
| `preference`          | POMDP          | Represents the preferences of an agent, functions analogously to a reward.                             |
| `likelihood`          | POMDP, BN      | A likelihood, e.g. a conditional probability distribution P(observation|state)                      |
| `initial_state_prior` | POMDP          | The initial state prior factor. This is a factor that represents the initial state probabilities.    |
| `belief`              | POMDP          | Represents a variational posterior (Q(x)); stored for use in future inferences.                  |
| `observation`         | POMDP          | Represents an observed variable.                                                        |

In VFG 2.0.0, these have been paired down to the minimum information necessary to execute certain types of inference (i.e. the `control_target` Boolean), with the rest considered as metadata.

#### Values
N-D tensor (matrix) representing the probabilities associated with a categorical distribution. (In 2.0.0, these are treated as random variables, which may or may not be observed.) The `values` for a factor should be set as its normalized `counts`, if the latter are present.

#### Counts
Dirichlet counts associated with a factor (these may be raw counts derived from data, or "pseudocounts" specified as priors). Used for continuous learning. When normalized, these yield the probabilities associated with a categorical factor, and their raw values indicate degree of confidence in the resulting distribution. In 2.0.0, these are absorbed into the parameters of `dirichlet` priors.

#### Metadata
Stores information about the model, as distinct from the graph. These are user-defined and will be parroted, without affecting output.
In 2.0.0, any metadata is stored in a separate `metadata.json`.

##### Model Version
The version of the *model*, not the VFG. User-defined. No versioning scheme is imposed.

##### Model type
Informational only. One of `"bayesian_network"`, `"markov_random_field"`, `"pomdp"`, or the generic `"factor_graph"`.
This is not used in any parsers; model type is used implicitly.

##### Description
Free-form text field describing information and the purpose of the model.

##### Visualization Metadata
Visualization metadata is used to store information about how the model should be visualized in the editor.

## GPF
GPF, or Genius Project Format, is a container format for VFGs. It is a zip file that contains the VFG and its associated files. It is used to store and share VFGs in a standardized format.

As decided in [ADR-0002](decisions/ADR-0002-container.md), a given `model1` model, will produce a gpf file having the following structure
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
