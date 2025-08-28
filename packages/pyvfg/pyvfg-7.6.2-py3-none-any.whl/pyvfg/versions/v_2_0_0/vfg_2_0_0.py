# -*- coding: utf-8 -*-

from __future__ import annotations

import re
import warnings
import zipfile
from collections import Counter
from enum import StrEnum
from typing import Annotated, Dict, List, Optional, Tuple, Union, Literal, Any
from zipfile import ZipFile

import numpy as np
from jsonpatch import JsonPatch
from pydantic import BaseModel, Field, RootModel, model_validator
from pydantic_core import core_schema

from ..common import (
    initialize_factors,
    normalize_factors,
    GenerateJsonSchemaIgnoreInvalid,
    apply_patches_to_vfg,
    ModelType,
    FactorInitialization,
)
from ...errors import (
    DuplicateElementsError,
    ValidationError,
    ValidationErrors,
)
from ...project.model import GeniusProjectFile
from ...project.utils import load_single_tensor

warnings.simplefilter("always", ResourceWarning)


DUMMY_CONTROL_STATE_NAME = "dummy_control_state"

VariableReference = Union[str, Tuple[str, int]]


class NpyFilepath(str):
    """
    A string representing a file path to a .npy file.
    This class validates the file path to ensure it ends with '.npy'.
    """

    # Compile the regex pattern once for efficiency
    _pattern = re.compile(r"^.*\.(npy)$")

    def __new__(cls, value):
        """
        Overrides the default object creation method to add validation.
        """
        # Validate the input value against the regex pattern
        if not cls._pattern.fullmatch(value):
            raise ValueError(f"'{value}' is not a valid .npy file path. ")

        return super().__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        """
        Tells Pydantic how to handle this custom type.
        """

        # This defines a validation function that Pydantic will call.
        # It takes the input string and must return an instance of NpyFilepath.
        def validate_from_str(value: str) -> "NpyFilepath":
            if not cls._pattern.fullmatch(value):
                raise ValueError(f"Path must end with .npy, but got '{value}'")
            # noinspection PyTypeChecker
            return NpyFilepath(value)

        # This tells Pydantic:
        # 1. Expect a string (`type='str'`).
        # 2. After validating it's a string, call our `validate_from_str` function.
        # 3. The result will be an instance of our class.
        return core_schema.no_info_after_validator_function(
            validate_from_str,
            core_schema.str_schema(),
        )


class VariableConstraints(BaseModel):
    """
    A class representing constraints for a variable.
    This class is used to define constraints on the variables in the VFG.
    """

    form: Literal["delta"] = "delta"
    """The form of the constraint, currently only 'delta' is supported"""


class Variable(BaseModel):
    class Domain(StrEnum):
        Real = "real"
        NonNegativeReal = "nonnegative_real"
        PositiveReal = "positive_real"
        PositiveDefinite = "positive_definite"
        PositiveSemidefinite = "positive_semidefinite"
        Simplex = "simplex"
        Categorical = "categorical"

    domain: Domain
    """The domain of the variable"""
    constraints: Optional[VariableConstraints]
    """The constraints of the variable"""
    shape: List[int]
    """The shape of the variable"""
    elements: Optional[List[str]]
    """The elements of the variable"""
    messages: Optional[NpyFilepath]
    """The messages file path for the stored vector"""
    observation: Optional[NpyFilepath]
    """The observation file path for the stored vector"""
    control_state: Optional[bool]
    """Whether the variable is a control state variable (default: False)"""

    # Private fields
    _messages_values: np.ndarray = None
    _observation_values: np.ndarray = None

    def __init__(
        self,
        domain: Domain,
        shape: List[int],
        constraints: Optional[VariableConstraints] = None,
        vfg: Optional[VFG] = None,
        elements: Optional[List[str]] = None,
        messages: Optional[NpyFilepath] = None,
        observation: Optional[NpyFilepath] = None,
        control_state: Optional[bool] = False,
    ):
        super().__init__(
            domain=domain,
            shape=shape,
            constraints=constraints,
            elements=elements,
            messages=messages,
            observation=observation,
            control_state=control_state,
        )

        self._vfg = vfg

        # disable hash given that this is a mutable object
        self.__hash__ = None

    _vfg: VFG = None

    def __eq__(self, other, exclude_tensor_values: bool = False):
        """
        Checks if two Variable instances are equal, excluding observation values if specified.
        Args:
            other (Variable): The other Variable instance to compare with.
            exclude_tensor_values (bool): If True, excludes any tensor value from the comparison.
        Returns:
            bool: True if the Variable instances are equal, False otherwise.
        """
        if not isinstance(other, Variable):
            return False

        return (
            self.domain == other.domain
            and self.constraints == other.constraints
            and self.shape == other.shape
            and self.elements == other.elements
            and self.control_state == other.control_state
            and self.control_state == other.control_state
            and self._eq_tensor_variables(other, exclude_tensor_values)
        )

    def _eq_tensor_variables(self, other: Variable, exclude_tensor_values: bool = False) -> bool:
        """
        Checks the equality of all the tensor variables of the Variable instance.
        Args:
            exclude_tensor_values (bool): If True, excludes any tensor value from the comparison, only checks the file paths.
        Returns:
            bool: True if the tensor variables are equal, False otherwise.
        """
        if exclude_tensor_values:
            return self.messages == other.messages and self.observation == other.observation

        messages_are_none = self.messages_values is None and other.messages_values is None
        observations_are_none = self.observation_values is None and other.observation_values is None

        return (messages_are_none or np.allclose(self.messages_values, other._messages_values)) and (
            observations_are_none or np.allclose(self.observation_values, other._observation_values)
        )

    def equals_besides_tensor_values(self, other):
        """
        Checks if two Variable instances are equal, ignoring observation values.
        """
        return self.__eq__(other, exclude_tensor_values=True)

    # region Properties

    @property
    def messages_values(self):
        """
        Messages values for the variable.

        Returns:
            List of messages values for the Variable.
        Raises:
            ValueError: If '_messages_values' is None, but 'messages' is not None and the Variable is not associated with a VFG.
        """
        if self._messages_values is None:
            if not self.messages:
                return None

            if self._vfg is None:
                raise ValueError("Variable is not associated with a VFG.")

            self._messages_values = self._vfg.load_tensor(self.messages)

        return self._messages_values

    @messages_values.setter
    def messages_values(self, value):
        """
        Sets the messages values for the Variable.
        """
        self._messages_values = value

    @property
    def observation_values(self):
        """
        Observation values for the variable.

        Returns:
            List of observation values for the variable.
        Raises:
            ValueError: If '_observation_values' is None, but 'observation' is not None and the Variable is not associated with a VFG.
        """
        if self._observation_values is None:
            if not self.observation:
                return None

            if self._vfg is None:
                raise ValueError("Variable is not associated with a VFG.")

            self._observation_values = self._vfg.load_tensor(self.observation)

        return self._observation_values

    @observation_values.setter
    def observation_values(self, value):
        """
        Sets the observation values for the variable.
        """
        self._observation_values = value

    # endregion

    # todo vfg2.0: check this. remember to validate tensors shape
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


class Function(BaseModel):
    class Type(StrEnum):
        Categorical = "categorical"
        ConditionalCategorical = "conditional_categorical"
        Dirichlet = "dirichlet"
        Gaussian = "gaussian"
        LinearGaussian = "linear_gaussian"
        Mixture = "mixture"
        GMM = "gmm"
        Wishart = "wishart"
        MatrixNormalWishart = "matrix_normal_wishart"
        NormalInverseWishart = "normal_inverse_wishart"
        Softmax = "softmax"
        MNLRegression = "mnlr"
        Potential = "potential"
        Plus = "+"
        Minus = "-"
        Multiply = "*"
        Custom = "custom"

        @classmethod
        def from_value(cls, value: str):
            """
            Returns the Function.Type enum member corresponding to the given value.
            Args:
                value (str): The value to convert.
            Returns:
                Function.Type: The corresponding enum member.
            Raises:
                ValueError: If the value does not match any enum member.
            """
            if value == "categorical_conditional":
                return Function.Type.ConditionalCategorical
            if value == "logits":
                return Function.Type.Softmax
            return cls(value)

    function: Type = Field(default=Type.Categorical)
    """The type of the function (distribution)"""
    output: Annotated[List[VariableReference], Field(min_length=1)]
    """The output variables of the function"""
    parameters: Optional[Dict[str, Union[VariableReference, List[VariableReference]]]] = Field(default_factory=dict)
    """The parameters of the function"""
    constraints: Optional[Dict[str, NodeConstraint]] = Field(default=None)
    """The constraints of the function, if any"""
    control_target: Optional[bool] = False
    """Whether the function is a control target (default: False)"""


class Factor(RootModel[Union[Function, List[str]]]):
    def __init__(
        self,
        output: Annotated[List[VariableReference], Field(min_length=1)],
        function: Function.Type = Field(default=Function.Type.Categorical),
        parameters: Optional[Dict[str, Union[VariableReference, List[VariableReference]]]] = None,
        constraints: Optional[Dict[str, NodeConstraint]] = None,
        control_target: Optional[bool] = False,
    ):
        super().__init__(
            output=output,
            function=function,
            parameters=parameters,
            constraints=constraints,
            control_target=control_target,
        )
        # disable hash given that this is a mutable object
        self.__hash__ = None

    def __eq__(self, other):
        if not isinstance(other, Factor):
            return False

        parameters_are_equal = True
        for key, value in self.root.parameters.items():
            if isinstance(value, list):
                parameters_are_equal &= all(x in other.root.parameters[key] for x in value)
            else:
                parameters_are_equal &= value == other.root.parameters[key]

        return (
            self.root.function == other.root.function
            and self.root.output == other.root.output
            and parameters_are_equal
            and self.root.constraints == other.root.constraints
            and self.root.control_target == other.root.control_target
        )

    def deepcopy(self):
        return self.model_copy(deep=True)

    @classmethod
    def model_json_schema(cls, **kwargs):
        kwargs["schema_generator"] = GenerateJsonSchemaIgnoreInvalid
        # Get the default schema which skips over the np.ndarray field
        schema_ = super().model_json_schema(**kwargs)
        # Fix schema version
        schema_["$schema"] = "http://json-schema.org/draft-07/schema#"

        return schema_

    def to_dict(self, exclude_none: bool = True) -> dict:
        return self.model_dump(by_alias=True, exclude_none=exclude_none, mode="json")

    def factor_validate(self, factor_idx: Optional[int] = None, raise_exceptions: bool = True) -> ValidationErrors:
        # here we want to check if all input and output factors are the correct shape
        # we have determined that any combination is valid. If this is untrue, this can be changed later.
        return ValidationErrors(errors=[])


class NodeConstraint(BaseModel):
    variables: Annotated[List[VariableReference], Field(min_length=1)]
    """The variables involved in the constraint"""
    form: Literal["delta"] = "delta"
    """The form of the constraint, currently only 'delta' is supported"""
    p_substitutions: Optional[List[VariableReference]] = None
    """The p-substitution for the constraint"""


class VFG(BaseModel):
    version: Literal["2.0.0"] = "2.0.0"
    variables: Dict[str, Variable] = Field(default_factory=dict)
    factors: Dict[str, Factor] = Field(default_factory=dict)

    # Private fields
    _name: str
    _gpf_zip_file: Optional[ZipFile] = None
    _model_type: Optional[ModelType] = None
    _is_cleaned_up: bool = False

    def __init__(
        self,
        name: Optional[str] = None,
        variables: Optional[Dict[str, Variable]] = None,
        factors: Optional[Dict[str, Factor]] = None,
        gpf: Optional[GeniusProjectFile] = None,
        gpf_zip_file: Optional[ZipFile] = None,
        **data,
    ):
        """
        Initializes a VFG object.
        Args:
            name (Optional[str]): The name of the VFG.
            variables (Optional[Dict[str, Variable]]): A dictionary of variables in the VFG.
            factors (Optional[Dict[str, Factor]]): A dictionary of factors in the VFG.
            gpf (Optional[GeniusProjectFile]): A GeniusProjectFile object to load/save the VFG from/to.
            gpf_zip_file (Optional[ZipFile]): A ZipFile representing the loaded GPF. If this is not None, the gpf argument is ignored.
            **data: Additional data to initialize the VFG.
        """
        if name is None:
            name = "model1"
        if variables is None:
            variables = {}
        if factors is None:
            factors = {}

        super().__init__(variables=variables, factors=factors, **data)

        self._name = name
        self._gpf_zip_file = gpf_zip_file
        if gpf_zip_file is None and gpf is not None:
            self._gpf_zip_file = zipfile.ZipFile(gpf, "r")

    def cleanup(self):
        """
        Cleans up the VFG by closing the GPF zip file if it exists.
        Note: do not move this inside the __del__() method, as it is not guaranteed
        to be called before the Pydantic __pydantic_private__ attribute is set to None.
        """
        if hasattr(self, "_gpf_zip_file") and self._gpf_zip_file is not None:
            self._gpf_zip_file.close()
            self._gpf_zip_file = None

        self._is_cleaned_up = True

    def __enter__(self):
        """Used for `with` statements to ensure cleanup is called."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Used for `with` statements. Calls cleanup() directly."""
        self.cleanup()

    def __del__(self) -> None:
        try:
            # If the cleanup method was not called, we warn the user
            if not self._is_cleaned_up:
                warnings.warn(
                    f"VFG 2.0.0 instance was destroyed without calling cleanup()! Instance: {self!r}",
                    ResourceWarning,
                )
        except AttributeError:
            pass  # Safe during teardown

    # region Properties

    @property
    def zip_file(self):
        return self._gpf_zip_file

    @property
    def vars_set(self):
        return set(self.variables.keys())

    @property
    def var_shapes(self):
        return {v: self.variables[v].shape for v in self.variables}

    @property
    def model_type(self):
        """
        Returns the model type of the VFG.
        """
        if not self._model_type:
            self._model_type = self.vfg_validate()[1]
        return self._model_type

    # endregion

    def model_post_init(self, __context: Any) -> None:
        for var_instance in self.variables.values():
            var_instance._vfg = self

    @classmethod
    def model_json_schema(cls, **kwargs):
        kwargs["schema_generator"] = GenerateJsonSchemaIgnoreInvalid
        # Get the default schema which skips over the np.ndarray field
        schema_ = super().model_json_schema(**kwargs)
        # Fix schema version
        schema_["$schema"] = "http://json-schema.org/draft-07/schema#"

        return schema_

    def __eq__(self, other, exclude_variable_observation_values=True):
        """
        Checks if two VFG instances are equal, excluding observation values of variables if specified.
        Args:
            other (VFG): The other VFG instance to compare with.
            exclude_variable_observation_values (bool): If True, excludes observation values from the comparison.
        Returns:
            bool: True if the VFG instances are equal, False otherwise.
        """
        if not isinstance(other, VFG):
            return False

        return (
            self.version == other.version
            and self.factors == other.factors
            and (
                all(self.variables[x].equals_besides_tensor_values(other.variables[x]) for x in self.variables.keys())
                if exclude_variable_observation_values
                else self.variables == other.variables
            )
        )

    def equals_besides_variable_observation_values(self, other):
        """
        Checks if two Variable instances are equal, ignoring observation values.
        """
        return self.__eq__(other, exclude_variable_observation_values=True)

    def load_tensor(self, tensor_name: str) -> np.ndarray:
        """
        Loads a tensor from the GPF zip file.
        Args:
            tensor_name (str): The name of the tensor to load.
        Returns:
            The loaded tensor as a numpy array.
        Raises:
            ValueError: If no GPF zip file is provided or the tensor does not exist.
        """
        if self._gpf_zip_file is None:
            try:
                return np.load(tensor_name, allow_pickle=False, encoding="bytes")
            except FileNotFoundError:
                raise ValueError(f"No GPF zip file provided and tensor file '{tensor_name}' has not been found.")
            except Exception as e:
                raise ValueError(f"No GPF zip file provided. Error loading tensor '{tensor_name}': {e}")

        try:
            return load_single_tensor(self._gpf_zip_file, self._name, tensor_name)
        except FileNotFoundError:
            # let's try to load it from the local filesystem
            return np.load(tensor_name, allow_pickle=False, encoding="bytes")

    # region From/To methods

    def to_vfg(self) -> VFG:
        """
        Returns the VFG object (for use by subclasses)
        """
        return VFG.model_validate(self.json_copy())

    def to_dict(self, exclude_none: bool = True) -> dict:
        return self.model_dump(by_alias=True, exclude_none=exclude_none, mode="json")

    def to_gpf(self, file: GeniusProjectFile):
        """
        Saves the VFG to a Genius Project File (GPF).
        Args:
            file (GeniusProjectFile): The Genius Project File to save the VFG to.
        """
        # import here to avoid circular imports
        from ...project.serialization import save_project_200

        save_project_200(self, file, model_name=self._name)

    @staticmethod
    def from_dict(vfg_dict: dict) -> VFG:
        return VFG.model_validate(vfg_dict)

    @staticmethod
    def from_file(file_path: str) -> VFG:
        with open(file_path, "r") as f:
            return VFG.model_validate_json(f.read())

    @staticmethod
    def from_gpf(file: GeniusProjectFile, model_name: Optional[str] = None) -> VFG | None | List[VFG]:
        """
        Loads a VFG from a Genius Project File.
        Args:
            file (GeniusProjectFile): The Genius Project File to load the VFG from.
            model_name (Optional[str]): The name of the model to load. If None, all the models in the GPF will be loaded.
        Returns:
            VFG: If there is only 1 model in the GPF file or if `model_name` is specified and present in the GPF file.
            None: If the GPF file contains no models or if `model_name` is specified but not present in the GPF file.
            List[VFG]: If the GPF contains multiple models and `model_name` is None.
        """
        # import here to avoid circular imports
        from ...project.serialization import load_project_200

        models = load_project_200(file)

        if len(models) == 0:
            return None

        if model_name is None:
            if len(models) == 1:
                return models[0]
            return models

        for model in models:
            if model._name == model_name:
                return model

        # If we reach here, the model_name was specified but not found
        return None

    # endregion

    def deepcopy(self):
        return self.model_copy(deep=True)

    def json_copy(self):
        return self.deepcopy().model_dump()

    def get_flat_params(self, use_counts: bool = False) -> np.ndarray:
        def _get_arr(f):
            return f.counts if use_counts else f.values

        return np.concatenate([_get_arr(f).flatten() for f in self.factors])

    def get_observation_values_for_variables(self, variables: List[str]) -> Dict[str, np.ndarray]:
        """
        Returns the observation values for the given variables.
        """
        obs_values = {}

        if self.zip_file is not None:
            for var in variables:
                if var in self.variables:
                    obs_values[var] = self.variables[var].observation_values
                else:
                    # todo vfg2.0: do we want to raise an Error or return empty?
                    obs_values[var] = np.array([])

        return obs_values

    def apply_patches(
        self,
        patches: Union[ValidationErrors, list[ValidationError], JsonPatch, list[JsonPatch]],
    ) -> VFG:
        return apply_patches_to_vfg(self, patches)

    def initialize_factors(self, init_strategy: FactorInitialization | dict[str, FactorInitialization]):
        initialize_factors(self, init_strategy)

    def normalize_factors(self):
        normalize_factors(self)

    @model_validator(mode="after")
    def _pydantic_validate(self) -> "VFG":
        # re-use internal validation function for pydantic validation
        errors = self.vfg_validate(raise_exceptions=True)
        if len(errors) != 0:
            raise errors
        # if pass, return self
        return self

    def validate(self, raise_exceptions: bool) -> ValidationErrors:
        """
        This method conflicts with the pydantic BaseClass validate() method, which
        is now deprecated. To avoid spurious warnings, please call `vfg_validate` instead.
        Args:
            raise_exceptions: Whether to raise exceptions.

        Returns: The errors from validation;
        See: `vfg_validate`
        """
        return self.vfg_validate(raise_exceptions=raise_exceptions)

    def vfg_validate(
        self,
        raise_exceptions: bool = True,
    ) -> ValidationErrors:
        """
        Determines if the given VFG, is valid and tries to infer its type.

        Args:
            raise_exceptions (bool): If True, raise an exception on any validation warning
        Returns:
            ValidationErrors if the VFG is invalid, otherwise an empty list of errors, and the inferred VFG type
        """
        errors: List[ValidationError] = []

        for factor in self.factors.values():
            # self-validate factors
            factor.factor_validate(factor_idx=None, raise_exceptions=raise_exceptions)
            # validate factor inputs and outputs exist
            for var_name in factor.root.output:
                if isinstance(var_name, tuple):
                    var_name = var_name[0]
                if var_name not in self.variables:
                    errors.append(ValidationError(f"Variable '{var_name}' is not defined in the VFG variables."))
            if factor.root.parameters is not None:
                for parameter_type, var_value in factor.root.parameters.items():
                    # iterate over probability and input variables
                    if parameter_type == "probabilities" or parameter_type == "input":
                        # unify between list and singular from json
                        var_value = var_value if isinstance(var_value, list) else [var_value]
                        # for each of those...
                        for var_name in var_value:
                            # if it's subscripted, take the name without the subscript
                            if isinstance(var_name, tuple):
                                var_name = var_name[0]
                            # verify the name exists as a variable
                            if var_name not in self.variables:
                                errors.append(
                                    ValidationError(
                                        f"Variable '{var_name}' is not defined in the VFG variables.",
                                        parameters={"factor": factor.root.output},
                                    )
                                )

        errors_obj = ValidationErrors(errors=errors)
        if raise_exceptions and len(errors) > 0:
            raise errors_obj
        else:
            return errors_obj

    # todo vfg2.0: this was leveraging validate_as (now removed), how are we going to handle it?
    def model_is_one_of(
        self,
        allowed_model_types: Union[ModelType, list[ModelType]],
    ) -> bool:
        raise NotImplementedError()

        if isinstance(allowed_model_types, ModelType):
            allowed_model_types = [allowed_model_types]

        for mt in allowed_model_types:
            errors = self.validate_as(mt, raise_exceptions=False).model_type_errors
            if not errors:
                return True

        return False

    def _correct(
        self,
        raise_exceptions: bool = True,
    ) -> Tuple[VFG, list[ValidationError]]:
        """
        Implementation of the 'correct' method (shared by subclasses).
        """
        errors = self.vfg_validate(raise_exceptions=False)
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
        Currently implemented to call _correct().

        Args:
            as_model_type (Optional[ModelType]): Currently ignored.
            raise_exceptions (bool): If True, raises an exception on any validation warning that can't be recovered from.
        Returns:
            A corrected VFG and a list of non-recoverable errors
        """
        return self._correct(raise_exceptions=raise_exceptions)
