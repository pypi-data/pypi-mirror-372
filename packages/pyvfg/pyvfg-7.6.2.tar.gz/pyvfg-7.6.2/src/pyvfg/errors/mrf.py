from typing import Optional
from .base import ModelTypeError, ValidationError
from jsonpatch import JsonPatch


class NonPotentialInMRF(ModelTypeError):
    def __init__(self, factor_idx: int, patch: Optional[JsonPatch] = None):
        super(NonPotentialInMRF, self).__init__(
            "Factor %d represents an invalid distribution type for Markov random fields (must use a symmetric potential function)."
            % factor_idx,
            {"factor_idx": factor_idx},
            patch,
        )


class NegativePotentialError(ValidationError):
    def __init__(
        self,
        factor_idx: int,
    ):
        super(NegativePotentialError, self).__init__(
            "Tensor values for potential functions must be non-negative. Found negative values for factor %s"
            % str(factor_idx),
            {
                "factor_idx": factor_idx,
            },
        )
