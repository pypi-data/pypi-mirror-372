from typing import Optional
from .base import ValidationError, ModelTypeError
from jsonpatch import JsonPatch


class MissingDistribution(ValidationError):
    def __init__(self, which_var: str, patch: Optional[JsonPatch] = None):
        super(MissingDistribution, self).__init__(
            "There must be a distribution over variable '%s'." % which_var,
            {"variable": which_var},
            patch,
        )


class MultipleDistributions(ValidationError):
    def __init__(self, which_var: str, factor_idxs: list[int], patch: Optional[JsonPatch] = None):
        super(MultipleDistributions, self).__init__(
            "There must be only one distribution over variable '%s'. Factors targeting this variable: %s"
            % (which_var, ", ".join([str(i) for i in factor_idxs])),
            {"variable": which_var, "factor_idxs": factor_idxs},
            patch,
        )


class CyclicGraph(ValidationError):
    def __init__(self):
        super(CyclicGraph, self).__init__("The graph representing a Bayesian Network must be acyclic.")


class MultivariateDistributionNotConditional(ModelTypeError):
    def __init__(self, which_var: str, patch: Optional[JsonPatch] = None):
        super(MultivariateDistributionNotConditional, self).__init__(
            "Variables '%s' are connected by a factor whose distribution must be conditional." % which_var,
            {"variable": which_var},
            patch,
        )


class InvalidFactorRole(ModelTypeError):
    def __init__(self, which_vars: list[str], role: str, patch: Optional[JsonPatch] = None):
        super(InvalidFactorRole, self).__init__(
            "Factors involving variable(s) '%s' have role '%s' which is undefined for this model type."
            % (", ".join(which_vars), role),
            {"variables": which_vars, "role": role},
            patch,
        )
