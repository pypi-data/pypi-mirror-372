# VFG 0.5.0

### Versioning
VFG is versioned from 0.2.0 to 0.5.0. These are, in general, backwards-compatible -- calling `pyvfg.vfg_upgrade()` on
a 0.2.0 VFG will produce a 0.5.0 VFG. However, one exception os <= 0.4.0 POMDPs to 0.5.0 POMDPs. Please see below
for how to upgrade the POMDPs.

#### Upgrading POMDPs from 0.4.0 to 0.5.0
VFG 0.5.0 introduces numeric validation for factor values. This means that POMDPs that use "categorical" for their
reward factor will fail validation. As such, the model will need to be updated.

To upgrade a POMDP from 0.4.0 to 0.5.0, you will need to change the reward factor from `"categorical"` to `"logits"`.

### Model Description
Currently supported model types are Bayesian Networks (BNs), Markov Random Fields (MRFs), and
Partially-Observable Markov Decision Processes (POMDPs).

## Variables
Variables are the nodes in the VFG. They represent the states, actions, and observations in the model.

### Variable Role
| Role            | Model Type     | Description                                                             |
|-----------------|----------------|-------------------------------------------------------------------------|
| null            | BN, MRF, POMDP | a "default" variable without a role.                                    |
| `control_state` | POMDP          | The state of the system. This is the variable that is being controlled. |
| `latent`        | BN, MRF        | A variable known to be present in the system, but cannot be observed.   | 

## Factors
Factors represent the relations between nodes.

### Possible Distribution Types
| Distribution              | Model type     | Description                                                                                                                                                   | Example Field                              |
|---------------------------|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| `categorical`             | BN, MRF, POMDP | A categorical distribution over a set of variables, for joint probability. Joint probability of a single variable is simply the probability of that variable. | `position` with role `initial_state_prior` |
| `categorical_conditional` | BN, MRF, POMDP | A categorical distribution conditioned on a set of variables. `["A", "B", "C"]` means `P(A\|B,C)`.                                                            | `observation\|position`                    |
| `logits`                  | POMDP          | A distribution as the input to a softmax, usually for intermediate or reward states.                                                                          | `position` with role `preference`          |
| `potential`               | MRF            | A non-normalized probability distribution.                                                                                                                    | `position` with role `potential`           |

### Counts
The counts are raw, observed counts for input variables, and are used to scale for continuous learning. This must be kept
in sync with values (which can be done by setting the `values` field to the normalized counts).

### Values
The values are scaled, probabilistic values, and are used for inference. This must be kept in sync with counts, if counts
are present for the same factor.

### Factor Role
| Role                  | Model Type     | Description                                                                                            |
|-----------------------|----------------|--------------------------------------------------------------------------------------------------------|
| null                  | BN, MRF, POMDP | A "default" factor without a role.                                                                     |
| `transition`          | MRF, POMDP     | The transition factor. This is a factor that represents the transition probabilities between states. |
| `reward`              | POMDP          | The reward factor. This is a factor that represents the reward probabilities.                        |
| `initial_state_prior` | POMDP          | The initial state prior factor. This is a factor that represents the initial state probabilities.    |
| `preference`          | POMDP          | The preference factor. This is a factor that represents the preference probabilities.                |
| `belief`              | MRF            | The potential factor. This is a factor that represents the potential probabilities.                  |
| `observation`         | POMDP          | The observation factor. This is a factor that represents the observation probabilities.              |

## Metadata
Stores information about the model, as distinct from the graph. These are user-defined and will be parroted, without
affecting output.

### Model Version
The version of the *model*, not the VFG. User-defined. No versioning scheme is imposed.

### Model type
Informational only. One of `"bayesian_network"`, `"markov_random_field"`, `"pomdp"`, or the generic `"factor_graph"`.
This is not used in any parsers; model type is used implicitly.

### Description
Free-form text field describing information and the purpose of the model.

## Visualization Metadata
Will be parroted, and never parsed. May be removed in the future.