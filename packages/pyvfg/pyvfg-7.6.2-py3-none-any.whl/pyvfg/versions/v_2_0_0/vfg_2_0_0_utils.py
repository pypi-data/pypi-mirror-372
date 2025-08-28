# -*- coding: utf-8 -*-
import importlib.metadata
import json
import math
from typing import Union, Optional

import numpy as np
import pydantic_core

from pyvfg.errors import JsonSerializationError
from pyvfg.versions.common import is_version_higher_than
from pyvfg.versions.v_0_5_0.vfg_0_5_0 import VariableRole, FactorRole, Distribution
from pyvfg.versions.v_0_5_0.vfg_0_5_0_utils import vfg_upgrade as vfg_upgrade_0_5_0
from pyvfg.versions.v_2_0_0.vfg_2_0_0 import (
    VFG as VFG_2_0_0,
    Variable as Variable_2_0_0,
    Function,
)

VERSION = importlib.metadata.version("pyvfg")


def vfg_from_json(json_data: Union[dict, str]) -> VFG_2_0_0:
    """
    See vfg_upgrade
    :param json_data: The json data to up-convert
    :return: The VFG data
    """
    import pydantic_core

    # this try/except is required to coerce the return type to JsonSerializationError for backwards compatibility
    try:
        return vfg_upgrade(json_data)
    except pydantic_core._pydantic_core.ValidationError as e:
        raise JsonSerializationError(message=str(e)) from e


def vfg_upgrade(json_data: Union[dict, str], force_use_factor_values: bool = False) -> VFG_2_0_0:
    """
    Upgrades the incoming VFG from JSON data to version 2.0.0.
    If factor counts are available and meaningful, they will be used; otherwise, factor values will be used.

    Args:
        json_data (Union[dict, str]): Incoming json data, in either dictionary or string format
        force_use_factor_values (bool): If True, forces the use of factor values instead of counts even if counts are available and meaningful
    Returns:
        A VFG object, in the 2.0.0 schema.
    """

    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    if not isinstance(json_data, dict):
        raise ValueError("json_data must be dict or str")

    if json_data["version"] == "2.0.0":
        # already in the latest version
        return VFG_2_0_0(**json_data)

    if is_version_higher_than(json_data["version"], "2.0.0"):
        raise ValueError(
            f"Cannot upgrade VFG from version {json_data['version']} to 2.0.0, "
            f"as it is already higher than the target version."
        )

    if json_data["version"] != "0.5.0":
        json_data = vfg_upgrade_0_5_0(json_data).to_dict()
    json_data["version"] = "2.0.0"

    control_state_variable_present = False

    # -- Upgrade variables --
    variables = json_data.get("variables", {})
    new_variables = {}
    new_variables_observation_values = {}
    for var_name, var in variables.items():
        new_variables[var_name] = {
            "domain": "categorical",
        }
        # use elements if available, otherwise use cardinality
        if "elements" in var:
            new_variables[var_name]["elements"] = var["elements"]
            new_variables[var_name]["shape"] = [len(var["elements"])]
        else:
            new_variables[var_name]["shape"] = [var["cardinality"]]

        if "role" in var:
            new_variables[var_name]["control_state"] = var["role"] == VariableRole.ControlState
            control_state_variable_present |= new_variables[var_name]["control_state"]

    # -- Upgrade factors --
    factors = json_data.get("factors", [])
    is_pomdp = control_state_variable_present or any(
        factor.get("role", None) == FactorRole.Preference for factor in factors
    )

    new_factors = {}
    for idx, factor in enumerate(factors):
        factor_vector_symbol = _get_alphabet_letter_for_index(idx)
        factor_vector_symbol_lower = factor_vector_symbol.lower()

        role = factor.get("role", None)
        if role is not None and isinstance(role, str):
            # Convert string role to FactorRole enum
            try:
                role = FactorRole(role)
            except ValueError:
                raise ValueError(f"Invalid factor role: {role}")
        factor_vars = factor.get("variables", [])
        factor_control_target = False
        factor_distribution_type = "probabilities"

        if role is None:
            new_factor_name = f"{factor_vars[0]}_prior" if len(factor_vars) == 1 else "_given_".join(factor_vars)
        else:
            # If the role is set, we use it to create a new factor name
            new_factor_name = f"{factor_vars[0]}_{role.value}"
            if new_factor_name in new_factors:
                # If the factor name already exists, append the index to make it unique
                new_factor_name += f"_{idx}"
            if role == FactorRole.Preference:
                factor_control_target = True
                factor_distribution_type = "logits"

        # factor's priors vector name
        factor_variable_vector_name = None
        if force_use_factor_values:
            factor_variable_vector_name = "values"
        else:
            # counts have priority over values
            if "counts" in factor and factor["counts"] is not None:
                factor_variable_vector_name = "counts"
            # if only values are available just use them
            elif "values" in factor and factor["values"] is not None:
                factor_variable_vector_name = "values"

        _input = None
        factor_vars = factor["variables"]
        if role == FactorRole.Transition or any(factor_vars.count(var) > 1 for var in factor_vars):
            # it's a transition

            if is_pomdp:
                # patch control state variable if needed
                if len(factor_vars) != 2 or (factor_vars[0] != factor_vars[1]):
                    new_variables[factor_vars[-1]]["control_state"] = True

                elif factor_variable_vector_name is not None:
                    # in case this transition factor is a self-transition and only has two (same) variables (i.e. ["X", "X"]),
                    # we need to add a control state variable
                    if np.array(factor[factor_variable_vector_name]).shape == (
                        variables[factor_vars[0]]["cardinality"],
                        variables[factor_vars[1]]["cardinality"],
                    ):
                        # add a new control state variable
                        control_state_variable = {
                            "domain": "categorical",
                            "shape": [1],
                            "control_state": True,
                        }
                        # let's take an unreachable index to get a safe control variable name
                        control_variable_name = _get_alphabet_letter_for_index(len(factors) + idx).lower()
                        new_variables[control_variable_name] = control_state_variable
                        factor_vars.append(control_variable_name)
                        # given that a control state variable has been added,
                        # we need to patch the factor variable vector by adding a new axis
                        factor[factor_variable_vector_name] = np.expand_dims(
                            factor[factor_variable_vector_name], -1
                        ).tolist()

            _input = [[var, -1] for var in set(factor_vars)]

        elif len(factor_vars) > 1:
            _input = factor_vars[1:]

        distribution = factor["distribution"]
        if not isinstance(distribution, str):
            # Validate that distribution is a valid Distribution enum member
            try:
                distribution = Distribution(distribution).value
            except ValueError:
                raise ValueError(f"Invalid factor distribution: {distribution}")

        new_factor = {
            "output": [factor_vars[0]],
            "function": Function.Type.from_value(distribution),
            "parameters": {factor_distribution_type: factor_vector_symbol},
            "control_target": factor_control_target,
        }
        if _input is not None:
            new_factor["parameters"]["input"] = _input

        new_factors[new_factor_name] = new_factor

        # factor's priors vector
        factor_variable_vector = (
            None if factor_variable_vector_name is None else np.array(factor[factor_variable_vector_name])
        )

        if factor_variable_vector is not None:
            factor_shape = list(factor_variable_vector.shape)
        else:
            factor_shape = [x["cardinality"] for x in factor_vars]

        # uppercase variable vector
        new_variables[factor_vector_symbol] = {
            "domain": "simplex",
            "shape": factor_shape,
        }

        # lowercase variable vector
        new_variables[factor_vector_symbol_lower] = {
            "domain": "positive_real",
            "shape": factor_shape,
        }

        if factor_variable_vector is not None:
            # add the observation filepath
            new_variables[factor_vector_symbol_lower]["observation"] = f"{factor_vector_symbol_lower}.npy"
            # save the observation values for the variable to load them directly into the VFG once it is created
            new_variables_observation_values[factor_vector_symbol_lower] = factor_variable_vector

        new_factors[f"{factor_vector_symbol}_prior"] = {
            "function": Function.Type.Dirichlet,
            "output": [factor_vector_symbol],
            "parameters": {"alpha": factor_vector_symbol_lower},
        }

    json_data["variables"] = new_variables
    json_data["factors"] = new_factors

    try:
        vfg = VFG_2_0_0(**json_data)
        for var_name, observation_values in new_variables_observation_values.items():
            vfg.variables[var_name].observation_values = observation_values
        return vfg
    except pydantic_core._pydantic_core.ValidationError as e:
        raise JsonSerializationError(message=str(e)) from e


def _upgrade_prior_factor(factor: dict) -> dict:
    """
    Upgrade a factor to the new prior factor format.
    :param factor: The factor to upgrade.
    :return: The upgraded factor.
    """
    new_factor = {
        "function": "conditional_categorical",
        "output": factor["variables"][0],
        "parameters": {"probabilities": "A"},
    }

    if len(factor["variables"]) > 1:
        new_factor["input"] = factor["variables"][1:]

    return new_factor


def _get_alphabet_letter_for_index(index: int) -> str:
    """
    Get the alphabet letter for a given index.
    Args:
        The index of the letter (0 for 'A', 1 for 'B', ..., 25 for 'Z', 26 for 'AA', 27 for 'AB', etc.).

    Returns:
            A string representing the Excel-style column name.

    Examples:
        0   -> A
        1   -> B
        ...
        25  -> Z
        26  -> AA
        27  -> AB
        ...
        625 -> ZZ
        626 -> AAA
        627 -> AAB

    """
    if not isinstance(index, int) or index < 0:
        raise ValueError("Input index must be a non-negative integer.")

    ALPHABET_MODULE = 26

    result = []
    while index >= 0:
        # Calculate the remainder when divided by ALPHABET_MODULE.
        remainder = index % ALPHABET_MODULE
        result.append(chr(65 + remainder))  # chr(65) is 'A', chr(66) is 'B', etc.
        # We need to subtract 1 from the index to get a 0-25 range for A-Z.
        index = (index // ALPHABET_MODULE) - 1

    # The characters are appended in reverse order, so reverse the list and join.
    return "".join(reversed(result))


def infer_variable_domain(value) -> Optional[Variable_2_0_0.Domain]:
    """
    Infers the most specific domain from the Variable_2_0_0.Domain enum that a given value fits.

    Args:
        value: The number of data structure to check.

    Returns:
        A Variable_2_0_0.Domain enum member if a suitable domain is found, otherwise None.
    """
    # 1. Categorical
    # This is a bit tricky as "categorical" can apply to almost anything if it's
    # part of a finite set. Without a predefined set of categories,
    # it's hard to infer purely from the value itself.
    # For a single number, it's usually not the primary inference.
    # If it's a string or a specific identifier, it might be categorical.
    if isinstance(value, (str, bool)):  # Simple check for common categorical types
        return Variable_2_0_0.Domain.Categorical

    # 2. Numeric Types
    if isinstance(value, (int, float)):
        if value > 0:
            return Variable_2_0_0.Domain.PositiveReal
        elif value >= 0:
            return Variable_2_0_0.Domain.NonNegativeReal
        else:
            return Variable_2_0_0.Domain.Real

    # 3. Simplex (typically a 1D array/list of non-negative reals that sum to 1)
    if isinstance(value, (list, np.ndarray)):
        if len(value) == 0:
            return None  # An empty list/array isn't a simplex

        if isinstance(value, list):
            value = np.array(value)

        is_simplex = True
        current_sum = 0.0
        # sum over the first axis
        array = value
        if array.ndim == 1:
            current_sum = array.sum(0)
        else:
            array_dim = tuple([-2] * (array.ndim - 2))  # To get the innermost 2D matrix
            array = array[array_dim]
            current_sum = array.sum(axis=0)

        # Allow for floating-point inaccuracies
        if not isinstance(current_sum, np.ndarray):
            current_sum = [current_sum]
        if is_simplex and all([math.isclose(x, 1.0, rel_tol=1e-9) for x in current_sum]):
            return Variable_2_0_0.Domain.Simplex

    # 4. PositiveDefinite / PositiveSemidefinite (typically 2D NumPy arrays/matrices)
    if isinstance(value, np.ndarray):

        def check_positive_real_or_non_negative_real():
            if np.all(value > 0):
                return Variable_2_0_0.Domain.PositiveReal
            elif np.all(value >= 0):
                return Variable_2_0_0.Domain.NonNegativeReal
            else:
                return Variable_2_0_0.Domain.Real

        if value.ndim == 2:
            if value.shape[0] != value.shape[1]:
                # Not a square matrix, so cannot be positive definite/semidefinite,
                # but we can check for positive real or non-negative real
                return check_positive_real_or_non_negative_real()

            # Check for Positive Definite/Semidefinite
            try:
                # Cholesky decomposition is a common way to check for positive definiteness.
                # If A is positive definite, then it can be decomposed as L @ L.T
                # where L is lower triangular. If A is positive semidefinite, it means
                # all eigenvalues are non-negative.
                # Using `np.linalg.cholesky` is typically for positive definite.
                # For positive semi-definite, you'd usually check eigenvalues.

                # Attempt Cholesky for PositiveDefinite
                np.linalg.cholesky(value)
                return Variable_2_0_0.Domain.PositiveDefinite
            except np.linalg.LinAlgError:
                # If Cholesky fails, it's not strictly positive definite.
                # Now check for Positive Semidefinite (all eigenvalues >= 0), eigvalsh for symmetric matrices
                eigenvalues = np.linalg.eigvalsh(value)
                # Allow small negative for float errors
                if np.all(eigenvalues >= -1e-9):
                    return Variable_2_0_0.Domain.PositiveSemidefinite
        else:
            return check_positive_real_or_non_negative_real()

    return None
