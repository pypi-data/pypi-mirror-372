from typing import Union, Counter, Self

import numpy as np
from jsonpatch import JsonPatch

from .vfg_0_5_0 import VFG, FactorRole, Distribution, combine_factors

from pyvfg.errors import (
    ValidationErrors,
    ValidationError,
    InvalidFactorRole,
    MultivariateDistributionNotConditional,
    MultipleDistributions,
    MissingDistribution,
    CyclicGraph,
)


class BayesianNetwork(VFG):
    def get_factor(self, factor_var):
        return next((f for f in self.factors if f.variables[0] == factor_var), None)

    @classmethod
    def from_vfg(cls, vfg: VFG) -> Self:
        return BayesianNetwork.model_validate(vfg.to_dict())

    def apply_patches(
        self,
        patches: Union[ValidationErrors, list[ValidationError], JsonPatch, list[JsonPatch]],
    ) -> Self:
        return BayesianNetwork.model_validate(super().apply_patches(patches).to_dict())

    def validate(self, raise_exceptions: bool = True):
        errors = ValidationErrors(errors=[])

        has_distribution = Counter()
        exclude_factors_idxs = []
        for factor_idx, factor in enumerate(self.factors):
            if factor.role in [FactorRole.Transition, FactorRole.Preference]:
                patch = JsonPatch(
                    [
                        {
                            "op": "replace",
                            "path": f"/factors/{factor_idx}/role",
                            "value": None,
                        }
                    ]
                )
                if factor.role == FactorRole.Transition:
                    # If it looks like this was meant to be a transition based on variables, don't auto-patch
                    if factor.variables[0] == factor.variables[1]:
                        patch = None
                    # Don't consider this factor for the acyclicity check, the transition role suggests
                    # maybe there's a deeper problem
                    exclude_factors_idxs.append(factor_idx)

                errors.extend(InvalidFactorRole(factor.variables, factor.role, patch))

            has_distribution.update([factor.variables[0]])

            if len(factor.variables) > 1 and factor.distribution != Distribution.CategoricalConditional:
                # We can just set the distribution to conditional
                patch = JsonPatch(
                    [
                        {
                            "op": "replace",
                            "path": f"/factors/{factor_idx}/distribution",
                            "value": "categorical_conditional",
                        }
                    ]
                )
                errors.extend(MultivariateDistributionNotConditional(factor.variables, patch))
                # For simplicity of error messages, we can exclude this factor from the acyclicity check
                # since fixing this suffices to make the graph acyclic, ceteris paribus
                exclude_factors_idxs.append(factor_idx)

        for var in has_distribution:
            if has_distribution[var] > 1:
                var_factor_idxs = [(idx, f) for idx, f in enumerate(self.factors) if f.variables[0] == var]
                var_factors = [f for _, f in sorted(var_factor_idxs, key=lambda x: x[0])]
                common_vars = set(var_factors[0].variables[1:])
                for vf in var_factors[1:]:
                    common_vars = common_vars.intersection(set(vf.variables[1:]))
                patch = None
                if (
                    all([vf.values.shape[0] == var_factors[0].values.shape[0] for vf in var_factors])
                    and not common_vars
                ):
                    patch = JsonPatch(
                        [
                            {
                                "op": "remove",
                                "path": f"/factors/{factor_idx}",
                            }
                            for factor_idx, _ in sorted(var_factor_idxs, key=lambda x: x[0], reverse=True)
                        ]
                        + [
                            {
                                "op": "add",
                                "path": "/factors/-",
                                "value": combine_factors(var_factors).to_dict(),
                            }
                        ]
                    )
                errors.extend(
                    MultipleDistributions(
                        var,
                        [i for i, f in enumerate(self.factors) if f.variables[0] == var],
                        patch,
                    )
                )

        no_dist = self.vars_set - set(has_distribution)

        if no_dist:
            diffs = []
            for var in no_dist:
                patch = {
                    "op": "add",
                    "path": "/factors/-",
                    "value": {
                        "variables": [var],
                        "distribution": Distribution.Categorical,
                        "values": (np.ones(self.variables[var].cardinality) / self.variables[var].cardinality).tolist(),
                    },
                }
                diffs.append(patch)

            # todo vfg2.0-clean: wrong type
            errors.extend(MissingDistribution(list(no_dist), JsonPatch(diffs)))

        if not self.is_acyclic(exclude_factors_idxs):
            # Non-auto-recoverable error
            errors.extend(CyclicGraph())

        # Fixing the subclass can't introduce new errors at the superclass level,
        # but subclasses can impose stronger constraints that make more general ones
        # redundant, so we fix the subclass before validating against the superclass
        fixed = self.apply_patches(errors)
        all_errors = errors + super(BayesianNetwork, fixed).validate(raise_exceptions=False)

        if raise_exceptions and all_errors:
            raise all_errors

        return all_errors
