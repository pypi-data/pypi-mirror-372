from enum import Enum
from typing import List, Union

import numpy as np
from jsonpatch import JsonPatch
from pydantic import BaseModel, Field
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from pydantic_core import core_schema, PydanticOmit
from ..errors import ValidationErrors, ValidationError

# Small value to use for ~zero Dirichlet counts
DIRICHLET_COUNTS_EPSILON = 1e-16


class InitializationStrategy(str, Enum):
    EPSILON = "epsilon"
    UNIFORM = "uniform"
    RANDOM = "random"


class ModelType(str, Enum):
    BayesianNetwork = "bayesian_network"
    MarkovRandomField = "markov_random_field"
    Pomdp = "pomdp"
    FactorGraph = "factor_graph"


class Smoothing(BaseModel):
    smoothing: float | int | List = Field(...)


class NumPreviousObservations(BaseModel):
    num_previous_observations: float | int = Field(..., ge=0)


FactorInitialization = InitializationStrategy | Smoothing | NumPreviousObservations


class GenerateJsonSchemaIgnoreInvalid(GenerateJsonSchema):
    """
    Custom JSON schema generator that ignores invalid schemas by raising PydanticOmit.
    """

    def handle_invalid_for_json_schema(self, schema: core_schema.CoreSchema, error_info: str) -> JsonSchemaValue:
        raise PydanticOmit


def softmax(x):
    """
    Compute the softmax of a numpy array along the first axis.
    """
    ex = np.exp(x - np.max(x, axis=0))
    return ex / ex.sum(axis=0)


def random_factor_values(
    source_shape: tuple,
    conditional: bool = False,
    dirichlet_range: int = 10,
):
    """
    Generate random factor values for a given source shape using a Dirichlet distribution.
    """
    if conditional:
        new_shape = tuple([source_shape[0]]) + tuple([int(np.prod(source_shape[1:]))])
    else:
        new_shape = tuple([int(np.prod(source_shape)), 1])

    new_values = np.empty(new_shape)
    # Randomly sample from a Dirichlet distribution
    for col in range(new_values.shape[-1]):
        new_values[:, col] = np.random.dirichlet(np.random.choice(range(1, dirichlet_range), new_shape[0]))
    return new_values.reshape(source_shape)


def initialize_factors(vfg, init_strategy: FactorInitialization | dict[str, FactorInitialization]):
    """
    Initialize factors in a Variable Factor Graph (VFG) based on the provided initialization strategy.
    If the strategy is a dictionary, it should map variable names to initialization strategies.
    Args:
        vfg (VFG_0_5_0|VFG_2_0_0): The variable factor graph to initialize.
        init_strategy (FactorInitialization | dict[str, FactorInitialization]): The initialization strategy.
            Can be a single strategy or a dictionary mapping variable names to strategies.
    Raises:
        ValueError: If a variable in the initialization strategy is not found in the VFG.
    """
    if isinstance(init_strategy, dict):
        for k in init_strategy.keys():
            if k not in vfg.vars_set:
                raise ValueError(f"Factor variable {k} not found in VFG")

        for factor in vfg.factors:
            if factor.variables[0] in init_strategy:
                factor.initialize(init_strategy[factor.variables[0]])
            else:
                factor.initialize()
    else:
        for factor in vfg.factors:
            factor.initialize(init_strategy)


def normalize_factors(vfg):
    """
    Normalize all factors in the Variable Factor Graph (VFG) to ensure their values sum to 1.
    Args:
        vfg (VFG_0_5_0|VFG_2_0_0): The variable factor graph whose factors need to be normalized.
    """
    for factor in vfg.factors:
        factor.normalize()


def model_is_one_of(
    vfg,
    allowed_model_types: Union[ModelType, list[ModelType]],
) -> bool:
    """
    Check if the Variable Factor Graph (VFG) is of one of the allowed model types.
    Args:
        vfg (VFG_0_5_0|VFG_2_0_0): The variable factor graph to check.
        allowed_model_types (Union[ModelType, list[ModelType]]): A single model type or a list of model types to check against.
    Returns:
        bool: True if the VFG is of one of the allowed model types, False otherwise.
    """
    if isinstance(allowed_model_types, ModelType):
        allowed_model_types = [allowed_model_types]

    for mt in allowed_model_types:
        errors = vfg.validate_as(mt, raise_exceptions=False).model_type_errors
        if not errors:
            return True

    return False


def get_tensor_and_belief_definitions():
    # return tensor, belief definitions for JSON schema
    return {
        "oneOf": [
            {"type": "number"},
            {"type": "array", "items": {"$ref": "#/$defs/Tensor"}},
        ],
    }, {
        "anyOf": [
            {"$ref": "#/$defs/Tensor"},
            {"type": "null"},
        ],
        "default": None,
    }


def apply_patches_to_vfg(
    vfg,
    patches: Union[ValidationErrors, list[ValidationError], JsonPatch, list[JsonPatch]],
):
    """
    Apply a list of patches to a Variable Factor Graph (VFG) and return a new VFG instance.
    Args:
        vfg (VFG_0_5_0|VFG_2_0_0): The variable factor graph to which the patches will be applied.
        patches (Union[ValidationErrors, list[ValidationError], JsonPatch, list[JsonPatch]]):
            A single patch or a list of patches to apply to the VFG.
    Returns:
        (VFG_0_5_0|VFG_2_0_0): A new instance of the VFG with the patches applied.
    """
    vfg_json = vfg.json_copy()
    if isinstance(patches, (ValidationError, JsonPatch)):
        patches = [patches]

    for patch in patches:
        if isinstance(patch, ValidationError):
            vfg_json = patch.apply_patch_to(vfg_json)
        elif isinstance(patch, JsonPatch):
            vfg_json = patch.apply(vfg_json)

    return type(vfg).from_dict(vfg_json)


def is_version_less_than(version: str, target_version: str) -> bool:
    """
    Check if the given version is less than the target version.
    It compares the version numbers by splitting them into components and comparing each component.

    Args:
        version (str): The version to compare.
        target_version (str): The target version to compare against.
    Returns:
        bool: True if the given version is less than the target version, False otherwise.
    """
    return tuple(map(int, version.split("."))) < tuple(map(int, target_version.split(".")))


def is_version_higher_than(version: str, target_version: str) -> bool:
    """
    Check if the given version is less than the target version.
    It compares the version numbers by splitting them into components and comparing each component.

    Args:
        version (str): The version to compare.
        target_version (str): The target version to compare against.
    Returns:
        bool: True if the given version is higher than the target version, False otherwise.
    """
    return tuple(map(int, version.split("."))) > tuple(map(int, target_version.split(".")))
