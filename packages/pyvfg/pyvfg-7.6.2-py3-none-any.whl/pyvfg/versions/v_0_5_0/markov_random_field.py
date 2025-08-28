from typing import Union, Self

from jsonpatch import JsonPatch

from pyvfg import (
    InvalidFactorRole,
    ValidationError,
    ValidationErrors,
    NonPotentialInMRF,
)
from pyvfg.versions.v_0_5_0.vfg_0_5_0 import Distribution, VFG


class MarkovRandomField(VFG):
    def apply_patches(
        self,
        patches: Union[ValidationErrors, list[ValidationError], JsonPatch, list[JsonPatch]],
    ) -> Self:
        return MarkovRandomField.model_validate(super().apply_patches(patches).to_dict())

    @classmethod
    def from_vfg(cls, vfg: VFG) -> Self:
        return MarkovRandomField.model_validate(vfg.to_dict())

    def validate(self, raise_exceptions: bool = True):
        errors = ValidationErrors(errors=[])

        for factor_idx, factor in enumerate(self.factors):
            if factor.role is not None:
                patch = JsonPatch(
                    [
                        {
                            "op": "replace",
                            "path": f"/factors/{factor_idx}/role",
                            "value": None,
                        }
                    ]
                )
                errors.extend(InvalidFactorRole(factor.variables, factor.role, patch))

            if factor.distribution != Distribution.Potential:
                # We can just set the distribution to categorical
                patch = JsonPatch(
                    [
                        {
                            "op": "replace",
                            "path": f"/factors/{factor_idx}/distribution",
                            "value": "potential",
                        }
                    ]
                )
                errors.extend(NonPotentialInMRF(factor_idx, patch))

        # As above, fix the subclass then validate against superclass
        fixed = self.apply_patches(errors)
        all_errors = errors + super(MarkovRandomField, fixed).validate(raise_exceptions=False)

        if raise_exceptions and all_errors:
            raise all_errors

        return all_errors
