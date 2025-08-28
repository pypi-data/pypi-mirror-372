from typing import Optional
from .base import ValidationError, ModelTypeError
from jsonpatch import JsonPatch


class MissingTransition(ValidationError):
    def __init__(self, which_vars: list[str], patch: Optional[JsonPatch] = None):
        super(MissingTransition, self).__init__(
            "Variable(s) '%s' lack transition factors." % ", ".join(which_vars),
            {"variables": which_vars},
            patch,
        )


class StateVarMissingLikelihood(ValidationError):
    def __init__(self, which_vars: list[str], patch: Optional[JsonPatch] = None):
        super(StateVarMissingLikelihood, self).__init__(
            "State variable(s) '%s' participate in no likelihood factors." % ", ".join(which_vars),
            {"variables": which_vars},
            patch,
        )


class ObsVarMissingLikelihood(ValidationError):
    def __init__(self, which_vars: list[str], patch: Optional[JsonPatch] = None):
        super(ObsVarMissingLikelihood, self).__init__(
            "Observation variable(s) '%s' lack likelihood factors." % ", ".join(which_vars),
            {"variables": which_vars},
            patch,
        )


class VariableRoleIndeterminate(ValidationError):
    def __init__(self, which_vars: list[str], patch: Optional[JsonPatch] = None):
        super(VariableRoleIndeterminate, self).__init__(
            "Role for variable(s) '%s' cannot be inferred from VFG information." % which_vars,
            {"variables": which_vars},
            patch,
        )


class NoTransitionFactors(ModelTypeError):
    def __init__(self, patch: Optional[JsonPatch] = None):
        super(NoTransitionFactors, self).__init__(
            "POMDP contains no transition factors.",
        )


class NoLikelihoodFactors(ModelTypeError):
    def __init__(self, patch: Optional[JsonPatch] = None):
        super(NoLikelihoodFactors, self).__init__(
            "POMDP contains no likelihood factors.",
        )
