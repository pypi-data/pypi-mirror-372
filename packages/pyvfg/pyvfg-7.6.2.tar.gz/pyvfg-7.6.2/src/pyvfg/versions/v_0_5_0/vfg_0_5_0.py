# -*- coding: utf-8 -*-

from __future__ import annotations

from collections import Counter
from enum import Enum
from itertools import permutations, chain
from typing import Annotated, Any, Dict, List, Optional, Tuple, Union

import networkx as nx
import numpy as np
from jsonpatch import JsonPatch
from pydantic import BaseModel, Field, RootModel
from pydantic.json_schema import WithJsonSchema
from scipy.linalg import expm

from ..common import (
    GenerateJsonSchemaIgnoreInvalid,
    random_factor_values,
    softmax,
    initialize_factors,
    normalize_factors,
    model_is_one_of,
    ModelType,
    FactorInitialization,
    Smoothing,
    NumPreviousObservations,
    InitializationStrategy,
    DIRICHLET_COUNTS_EPSILON,
    get_tensor_and_belief_definitions,
    apply_patches_to_vfg,
)
from ...errors import (
    DuplicateElementsError,
    DuplicateVariablesError,
    IncorrectTensorShape,
    InvalidVariableItemCount,
    MissingFactors,
    MissingProbability,
    MissingVariable,
    NegativePotentialError,
    NormalizationError,
    ValidationError,
    ValidationErrors,
    VariableMissingInVariableList,
)


class Metadata(BaseModel):
    model_version: Optional[str] = None
    model_type: Optional[ModelType] = None
    description: Optional[str] = None


class FactorRole(str, Enum):
    Transition = "transition"
    Preference = "preference"
    Likelihood = "likelihood"
    InitialStatePrior = "initial_state_prior"
    Belief = "belief"
    Observation = "observation"


class VariableRole(str, Enum):
    ControlState = "control_state"
    Latent = "latent"


class DiscreteVariableNamedElements(BaseModel):
    elements: List[str]
    role: Optional[VariableRole] = None


class DiscreteVariableAnonymousElements(BaseModel):
    cardinality: int = Field(..., ge=1, description="Cardinality")
    role: Optional[VariableRole] = None


class Variable(
    RootModel[
        Union[
            DiscreteVariableNamedElements,
            DiscreteVariableAnonymousElements,
        ]
    ]
):
    def get_elements(self):
        return self.elements

    @property
    def elements(self):
        if isinstance(self.root, DiscreteVariableNamedElements):
            return self.root.elements
        if isinstance(self.root, DiscreteVariableAnonymousElements):
            return [str(c) for c in range(self.root.cardinality)]

        raise ValueError(f"Cannot parse VFG Variable: {self}")

    @property
    def cardinality(self):
        if isinstance(self.root, DiscreteVariableNamedElements):
            return len(self.root.elements)
        if isinstance(self.root, DiscreteVariableAnonymousElements):
            return self.root.cardinality

        raise ValueError(f"Cannot parse VFG Variable: {self}")

    def validate(self, var_name: str, raise_exceptions: bool = True):
        errors = ValidationErrors(errors=[])
        ele_counter = Counter(self.elements)
        for ele_name, ele_count in ele_counter.items():
            if ele_count > 1:
                new_elements = []
                i = 1
                for e in self.elements:
                    ele = e
                    if e == ele_name:
                        if i > 1:
                            ele = f"{e}_{i}"
                        i += 1
                    new_elements.append(ele)
                patch = JsonPatch(
                    [
                        {
                            "op": "replace",
                            "path": f"/variables/{var_name}/elements",
                            "value": new_elements,
                        }
                    ]
                )
                errors.extend(DuplicateElementsError(var_name, ele_name, ele_count - 1, patch))
        if errors and raise_exceptions:
            raise errors
        return errors


class Distribution(str, Enum):
    Categorical = "categorical"
    CategoricalConditional = "categorical_conditional"
    Potential = "potential"
    Logits = "logits"


def get_einsum_signature_for_combining_factors(factors: list[Factor]) -> str:
    letters = [chr(97 + i) for i in range(26)] + [chr(65 + i) for i in range(26)]
    num_conditioning_dims = np.sum([f.values.ndim - 1 for f in factors])

    target_var_idx = letters[0]
    index_sets = []
    idx = 1
    for f in factors:
        index_sets.append(letters[idx : idx + f.values.ndim - 1])
        idx += f.values.ndim - 1

    return f"{','.join([target_var_idx + ''.join(index_set) for index_set in index_sets])}->{target_var_idx + ''.join(letters[1 : num_conditioning_dims + 1])}"


def combine_factors(factors: list[Factor]) -> Factor:
    """
    Combine a list of factors into a single factor.
    Assumes that all factors represent conditional distributions over the same variable, conditioned on disjoint sets of variables.

    Example:
        Input: factors = [f1, f2, f3]
        where f1 represents P(A | B, C)
            f2 represents P(A | D)
            f3 represents P(A | E, F)
        and variables A, B, C, D, E, and F have cardinalities 2, 3, 4, 2, 5, and 6, respectively.

        Output: factor f' representing P(A | B, C, D, E, F), with tensor shape (2, 3, 4, 2, 5, 6)
        where the variables are the union of the variables in the input factors.

        The values of f' are computed by taking the outer product of the values of f1, f2, and f3 and re-normalizing, i.e.
        performing the einsum operation described by the subscripts
            abc, ad, aef --> abcdef
        and normalizing the result.
    """
    einsum_signature = get_einsum_signature_for_combining_factors(factors)
    combined_values = np.einsum(einsum_signature, *[f.values for f in factors])
    factor = Factor(
        variables=[factors[0].variables[0]] + list(chain(*[f.variables[1:] for f in factors])),
        distribution=Distribution.CategoricalConditional,
        values=combined_values,
    )
    factor.normalize()
    return factor


class Factor(BaseModel):
    variables: List[str]
    distribution: Distribution
    # This annotation is required when OpenAPI generates the schema for /docs page
    counts: Optional[Annotated[np.ndarray, WithJsonSchema({"type": "array", "items": {"type": "number"}})]] = None
    values: Annotated[np.ndarray, WithJsonSchema({"type": "array", "items": {"type": "number"}})]
    role: Optional[FactorRole] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {np.ndarray: lambda v: v.tolist() if v.ndim > 0 else v.item()}

    def __init__(
        self,
        variables: List[str],
        distribution: Distribution,
        values: Union[np.ndarray, list, float, int],
        role: Optional[FactorRole] = None,
        counts: Optional[Union[np.ndarray, list, float, int]] = None,
    ):
        if isinstance(values, (float, int, list)):
            values = np.array(values, dtype=float)
        if isinstance(counts, (float, int, list)):
            counts = np.array(counts, dtype=float)
        super().__init__(
            variables=variables,
            distribution=distribution,
            values=values,
            role=role,
            counts=counts,
        )

    def __eq__(self, other):
        return (
            self.variables == other.variables
            and self.distribution == other.distribution
            and np.allclose(self.values, other.values)
            and self.role == other.role
        )

    def deepcopy(self):
        return self.model_copy(deep=True)

    @classmethod
    def model_json_schema(cls, **kwargs):
        kwargs["schema_generator"] = GenerateJsonSchemaIgnoreInvalid
        # Get the default schema which skips over the np.ndarray field
        schema_ = super().model_json_schema(**kwargs)

        tensor_definition, belief_definition = get_tensor_and_belief_definitions()

        # "Manually" add the tensor definition
        schema_["$defs"]["Tensor"] = tensor_definition

        # Update the Factor schema to use the tensor definition
        schema_["properties"]["values"] = {"$ref": "#/$defs/Tensor"}

        # Same for parameter_belief (counts)
        schema_["properties"]["counts"] = belief_definition

        # Fix schema version
        schema_["$schema"] = "http://json-schema.org/draft-07/schema#"

        return schema_

    def initialize(self, init_strategy: Optional[FactorInitialization] = None):
        if init_strategy is None:
            self.counts = self.values.copy()
            self.normalize()
            return

        if isinstance(init_strategy, Smoothing):
            smoothing = init_strategy.smoothing
            if isinstance(smoothing, (int, float)):
                self.counts = np.full_like(self.values, float(smoothing))
            elif isinstance(smoothing, list):
                self.counts = np.array(smoothing, dtype=float)

            self.values = self.counts.copy()
            self.normalize()

        elif isinstance(init_strategy, NumPreviousObservations):
            self.counts = self.values * init_strategy.num_previous_observations

        elif isinstance(init_strategy, InitializationStrategy):
            match init_strategy:
                case InitializationStrategy.EPSILON:
                    self.counts = np.zeros_like(self.values) + DIRICHLET_COUNTS_EPSILON

                case InitializationStrategy.UNIFORM:
                    self.values = np.ones_like(self.values)
                    self.normalize()
                    self.counts = self.values.copy()
                    return

                case InitializationStrategy.RANDOM:
                    self.counts = random_factor_values(
                        self.values.shape,
                        self.distribution == Distribution.CategoricalConditional,
                    )
                case _:
                    raise ValueError(f"Unknown initialization strategy: {init_strategy}")
            self.normalize(from_counts=True)

        else:
            raise ValueError(f"Unknown initialization strategy: {init_strategy}")

    def normalize(self, from_counts: bool = False):
        base = self.counts if from_counts else self.values

        if self.distribution == Distribution.Categorical:
            normalizer = base.sum(keepdims=True)
            zero_fill = 1 / np.prod(base.shape)

        elif self.distribution == Distribution.CategoricalConditional:
            normalizer = base.sum(axis=0, keepdims=True)
            zero_fill = 1 / base.shape[0]

        elif self.distribution == Distribution.Potential:
            # TODO: Local normalization can't be performed in this case.
            return self

        elif self.distribution == Distribution.Logits:
            # TODO: Should the distribution type change once normalized?
            self.values = softmax(base)
            return self

        # If normalizer is zero, fill with uniform distribution
        self.values = np.nan_to_num(base / normalizer, nan=zero_fill)

        return self

    def __iadd__(self, other: float | int | list | np.ndarray):
        if isinstance(other, list):
            other = np.array(other, dtype=float)

        if self.counts is None:
            self.counts = self.values.copy()

        self.counts += other
        return self

    def to_dict(self, exclude_none: bool = True) -> dict:
        return self.model_dump(by_alias=True, exclude_none=exclude_none, mode="json")

    def validate(self, factor_idx: Optional[int] = None, raise_exceptions: bool = True) -> ValidationErrors:
        errors = ValidationErrors(errors=[])
        match self.distribution:
            case Distribution.Categorical:
                z = self.values.sum()
                if not np.isclose(z, 1.0):
                    patch = JsonPatch(
                        [
                            {
                                "op": "replace",
                                "path": f"/factors/{factor_idx}/values",
                                "value": self.deepcopy().normalize().values.tolist(),
                            }
                        ]
                    )
                    errors.extend(NormalizationError(self.distribution.value, z, factor_idx, patch))

            case Distribution.CategoricalConditional:
                z = self.values.sum(keepdims=True, axis=0)
                if not np.allclose(z, 1.0):
                    patch = JsonPatch(
                        [
                            {
                                "op": "replace",
                                "path": f"/factors/{factor_idx}/values",
                                "value": self.deepcopy().normalize().values.tolist(),
                            }
                        ]
                    )
                    errors.extend(NormalizationError(self.distribution.value, z, factor_idx, patch))

            case Distribution.Potential:
                if np.any(self.values < 0):
                    errors.extend(NegativePotentialError(factor_idx))

            case Distribution.Logits:
                # Nothing to validate beyond Pydantic validation
                return errors

            case _:
                raise ValueError(f"Unknown distribution: {self.distribution}")

        var_counter = Counter(self.variables)
        for var_name, var_count in var_counter.items():
            if (
                self.role == FactorRole.Transition
                and (
                    (var_name != self.variables[0] and var_count > 1)
                    or (var_name == self.variables[0] and var_count > 2)
                )
            ) or (self.role != FactorRole.Transition and var_count > 1):
                errors.extend(DuplicateVariablesError(var_name, factor_idx))

        if errors and raise_exceptions:
            raise errors

        return errors


class VFG(BaseModel):
    version: str = Field("0.5.0", Literal=True)
    metadata: Optional[Metadata] = Field(default=None)
    variables: Dict[str, Variable] = Field(default_factory=dict)
    factors: List[Factor] = Field(default_factory=list)
    visualization_metadata: Optional[Any] = None

    def __init__(
        self,
        variables: Optional[Dict[str, Variable]] = None,
        factors: Optional[List[Factor]] = None,
        **data,
    ):
        if variables is None:
            variables = {}
        if factors is None:
            factors = []
        super().__init__(variables=variables, factors=factors, **data)

    @classmethod
    def model_json_schema(cls, **kwargs):
        kwargs["schema_generator"] = GenerateJsonSchemaIgnoreInvalid
        # Get the default schema which skips over the np.ndarray field
        schema_ = super().model_json_schema(**kwargs)

        tensor_definition, belief_definition = get_tensor_and_belief_definitions()
        # "Manually" add the tensor definition
        schema_["$defs"]["Tensor"] = tensor_definition
        schema_["$defs"]["Factor"]["properties"]["values"] = {"$ref": "#/$defs/Tensor"}

        # Update the Factor schema to use the tensor definition
        schema_["$defs"]["Factor"]["properties"]["counts"] = belief_definition

        # Fix schema version
        schema_["$schema"] = "http://json-schema.org/draft-07/schema#"

        return schema_

    def as_vfg(self) -> VFG:
        """
        Returns the VFG object (for use by subclasses)
        """
        return VFG.model_validate(self.json_copy())

    def to_dict(self, exclude_none: bool = True) -> dict:
        return self.model_dump(by_alias=True, exclude_none=exclude_none, mode="json")

    def to_digraph(self, exclude_factors_idxs=None) -> nx.DiGraph:
        if exclude_factors_idxs is None:
            exclude_factors_idxs = []

        G = nx.DiGraph()
        for idx, factor in enumerate(self.factors):
            if idx not in exclude_factors_idxs:
                for i in range(1, len(factor.variables)):
                    if factor.distribution == Distribution.CategoricalConditional:
                        G.add_edge(factor.variables[i], factor.variables[0])
                    elif factor.distribution == Distribution.Categorical:
                        G.add_edges_from(permutations(factor.variables, 2))
        return G

    def copy_without_tensors(self) -> VFG:
        """
        Returns a copy of the VFG without the tensors (values and counts) in the factors.
        This is useful for serialization or when you want to work with the structure without the data.
        """
        vfg_copy = {
            "version": self.version,
            "metadata": self.metadata,
            "variables": {k: v.model_copy(deep=True) for k, v in self.variables.items()},
            "factors": [],
            "visualization_metadata": self.visualization_metadata,
        }
        for factor in self.factors:
            vfg_copy["factors"].append(
                {
                    "variables": factor.variables,
                    "distribution": factor.distribution,
                    "counts": np.empty((0,)) if factor.counts is not None else None,
                    "values": np.empty((0,)) if factor.values is not None else None,
                    "role": factor.role,
                }
            )

        return VFG(**vfg_copy)

    def deepcopy(self):
        return self.model_copy(deep=True)

    def json_copy(self):
        return self.deepcopy().model_dump()

    @property
    def vars_set(self):
        return set(self.variables.keys())

    @property
    def latents(self):
        return [
            v
            for v in self.variables.keys()
            if hasattr(self.variables[v].root, "role") and self.variables[v].root.role == VariableRole.Latent
        ]

    @property
    def cardinalities(self):
        return {v: self.variables[v].cardinality for v in self.variables}

    @property
    def latent_cards(self):
        return {v: self.variables[v].cardinality for v in self.latents}

    def is_acyclic(self, exclude_factors_idxs=list[int]) -> bool:
        # Using acyclicity test from https://arxiv.org/pdf/1803.01422
        dag = self.to_digraph(exclude_factors_idxs=exclude_factors_idxs)
        if len(dag.edges) == 0:
            return True
        return np.trace(expm(nx.adjacency_matrix(dag).toarray())) == len(dag.nodes)

    @property
    def is_directed(self) -> bool:
        # Undirected graphs have symmetric adjacency matrices
        mat = nx.adjacency_matrix(self.to_digraph()).toarray()
        return not np.allclose(mat, mat.T)

    def get_flat_params(self, use_counts: bool = False) -> np.ndarray:
        def _get_arr(f):
            return f.counts if use_counts else f.values

        return np.concatenate([_get_arr(f).flatten() for f in self.factors])

    @staticmethod
    def from_dict(vfg_dict: dict) -> VFG:
        return VFG.model_validate(vfg_dict)

    @staticmethod
    def from_file(file_path: str) -> VFG:
        with open(file_path, "r") as f:
            return VFG.model_validate_json(f.read())

    def apply_patches(
        self,
        patches: Union[ValidationErrors, list[ValidationError], JsonPatch, list[JsonPatch]],
    ) -> VFG:
        return apply_patches_to_vfg(self, patches)

    def initialize_factors(self, init_strategy: FactorInitialization | dict[str, FactorInitialization]):
        initialize_factors(self, init_strategy)

    def normalize_factors(self):
        normalize_factors(self)

    def validate(
        self,
        raise_exceptions: bool = True,
    ) -> ValidationErrors:
        """
        Determines if the given VFG, which was valid according to the JSON schema, actually represents
        a processable VFG according to its type.
        # :param as_model_type: The input VFG type
        :param raise_exceptions: If True, raise an exception on any validation warning
        :return:
            ValidationErrors if the VFG is invalid; otherwise an empty list of errors
        Collect all errors into a single exception and raise on completion if `raise_exceptions` is True.
        """
        errors = ValidationErrors(errors=[])

        # Check for variables that are not in any factor
        in_factor = set()
        for factor in self.factors:
            in_factor.update(factor.variables)

        vars_not_in_factor = self.vars_set - in_factor

        if vars_not_in_factor:
            # if there are variables with no factors, we can add a flat distribution factor
            diffs = []
            for var in vars_not_in_factor:
                diffs.append(
                    {
                        "op": "add",
                        "path": "/factors/-",
                        "value": {
                            "variables": [var],
                            "distribution": Distribution.Categorical,
                            "values": (
                                np.ones(self.variables[var].cardinality) / self.variables[var].cardinality
                            ).tolist(),
                        },
                    }
                )

            errors.extend(MissingFactors(vars_not_in_factor, JsonPatch(diffs)))

        # check that all variables have a valid name, and that every variable has at least one element
        for var_name, values in self.variables.items():
            # TODO: Restore this if desired; it creates problems with CSV to model and
            # it's not clear it's necessary for inference
            # if not validation.is_valid_name(var_name):
            #     # Non-auto-recoverable error
            #     validation.conditional_raise(InvalidVariableName(var_name))

            if len(values.get_elements()) == 0:
                # Non-auto-recoverable error
                errors.extend(InvalidVariableItemCount(var_name))

            # Perform variable-specific validation
            errors = errors + values.validate(var_name, raise_exceptions=raise_exceptions)

        # check that all factors have valid variables
        # TODO refactor this to be a method on the Factor class
        for factor_idx, factor in enumerate(self.factors):
            # basic checks
            if len(factor.variables) == 0:
                # Non-auto-recoverable error
                errors.extend(MissingVariable(factor_idx))

            for idx, variable_id in enumerate(factor.variables):
                if variable_id not in self.variables:
                    # if the variable is not in the list, we can maybe add it based on the tensor shape
                    patch = (
                        JsonPatch(
                            [
                                {
                                    "op": "add",
                                    "path": f"/variables/{variable_id}",
                                    "value": {"cardinality": factor.values.shape[idx]},
                                }
                            ]
                        )
                        if factor.values.ndim == len(factor.variables)
                        else None
                    )
                    errors.extend(VariableMissingInVariableList(variable_id, patch))

            if len(factor.values) == 0:
                # if the factor has no values, we can fill in a flat distribution based on variable shapes
                if all(k in self.variables for k in factor.variables):
                    cardinalities = tuple([self.variables[k].cardinality for k in factor.variables])
                    patch = (
                        JsonPatch(
                            [
                                {
                                    "op": "replace",
                                    "path": f"/factors/{factor_idx}/values",
                                    "value": (np.ones(cardinalities) / cardinalities[0]).tolist(),
                                }
                            ]
                        )
                        if len(cardinalities) > 0
                        else None
                    )
                else:
                    patch = None
                errors.extend(MissingProbability(factor_idx, patch))

            else:
                if all(k in self.variables for k in factor.variables):
                    expected_var_shape = [self.variables[k].cardinality for k in factor.variables]
                    actual_var_shape = list(factor.values.shape)
                    if expected_var_shape != actual_var_shape:
                        # Non-auto-recoverable error (TODO: is it?)
                        errors.extend(IncorrectTensorShape(factor_idx, expected_var_shape, actual_var_shape))
                    else:
                        errors = errors + factor.validate(factor_idx, raise_exceptions=raise_exceptions)

        if raise_exceptions and errors:
            raise errors

        return errors

    def validate_as(
        self,
        model_type: ModelType,
        raise_exceptions: bool = True,
    ) -> ValidationErrors:
        from .bayesian_network import BayesianNetwork
        from .markov_random_field import MarkovRandomField
        from .pomdp import POMDP

        match model_type:
            case ModelType.BayesianNetwork:
                return BayesianNetwork.model_validate(self.json_copy()).validate(
                    raise_exceptions,
                )
            case ModelType.Pomdp:
                return POMDP.model_validate(self.json_copy()).validate(raise_exceptions)
            case ModelType.MarkovRandomField:
                return MarkovRandomField.model_validate(self.json_copy()).validate(
                    raise_exceptions,
                )
            case ModelType.FactorGraph:
                return self.validate(raise_exceptions)
            case _:
                raise NotImplementedError(f"'VFG.validate_as' not implemented for model type {model_type}")

    def model_is_one_of(
        self,
        allowed_model_types: Union[ModelType, list[ModelType]],
    ) -> bool:
        return model_is_one_of(self, allowed_model_types)

    def _correct(
        self,
        raise_exceptions: bool = True,
    ) -> Tuple[VFG, list[ValidationError]]:
        """
        Implementation of the 'correct' method (shared by subclasses).
        """
        errors = self.validate(raise_exceptions=False)
        vfg = self.apply_patches(errors) if errors else self

        nre = errors.non_recoverable_errors
        if nre and raise_exceptions:
            raise nre

        return vfg, nre

    def correct(
        self,
        as_model_type: Optional[ModelType] = None,
        raise_exceptions: bool = True,
    ) -> Tuple[VFG, list[ValidationError]]:
        """
        Corrects the VFG by automatically applying patches where possible.
        :param as_model_type: Option to apply more stringent standards associated with a subclass
        :param raise_exceptions: If True, raise an exception on any validation warning that can't be recovered from
        :return:
            A corrected VFG and a list of non-recoverable errors
        Collect all errors into a single exception and raise on completion if `raise_exceptions` is True.
        """
        as_model_type = as_model_type or ModelType.FactorGraph

        from .bayesian_network import BayesianNetwork
        from .markov_random_field import MarkovRandomField
        from .pomdp import POMDP

        match as_model_type:
            case ModelType.BayesianNetwork:
                fixed_model, errors = BayesianNetwork.model_validate(self.json_copy())._correct(raise_exceptions)
                return fixed_model.as_vfg(), errors

            case ModelType.Pomdp:
                fixed_model, errors = POMDP.model_validate(self.json_copy())._correct(raise_exceptions)
                return fixed_model.as_vfg(), errors

            case ModelType.MarkovRandomField:
                fixed_model, errors = MarkovRandomField.model_validate(self.json_copy())._correct(raise_exceptions)
                return fixed_model.as_vfg(), errors

            case ModelType.FactorGraph:
                pass

        errors = self.validate_as(model_type=as_model_type, raise_exceptions=raise_exceptions)
        vfg = self.apply_patches(errors) if errors else self

        return vfg, errors.non_recoverable_errors
