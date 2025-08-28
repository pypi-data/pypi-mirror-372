from typing import Union, Self

import numpy as np
from jsonpatch import JsonPatch

from pyvfg import (
    ValidationErrors,
    ValidationError,
    MultivariateDistributionNotConditional,
    StateVarMissingLikelihood,
    MissingTransition,
    VariableRoleIndeterminate,
    NoTransitionFactors,
    NoLikelihoodFactors,
    ObsVarMissingLikelihood,
)
from pyvfg.versions.v_0_5_0.vfg_0_5_0 import VFG, VariableRole, FactorRole, Distribution


class POMDP(VFG):
    def apply_patches(
        self,
        patches: Union[ValidationErrors, list[ValidationError], JsonPatch, list[JsonPatch]],
    ) -> Self:
        return POMDP.model_validate(super().apply_patches(patches).to_dict())

    @classmethod
    def from_vfg(cls, vfg: VFG) -> Self:
        return POMDP.model_validate(vfg.to_dict())

    @property
    def control_vars(self):
        return [v for v in self.vars_set if self.variables[v].root.role == VariableRole.ControlState]

    def validate(self, raise_exceptions: bool = True):
        errors = ValidationErrors(errors=[])

        has_likelihood_obs = set()
        has_likelihood_state = set()
        has_transition = set()
        has_preference_dist = set()
        control_vars = set()
        unlabeled_factors = set()

        # Gather info on existing factors
        for factor_idx, factor in enumerate(self.factors):
            if factor.role == FactorRole.Transition:
                has_transition.add(factor.variables[0])

                if factor.distribution != Distribution.CategoricalConditional:
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

                # Identify control variables
                if len(factor.variables) > 2 or (factor.variables[0] != factor.variables[1]):
                    control_vars.add(factor.variables[-1])

            elif factor.role == FactorRole.Likelihood:
                has_likelihood_obs.add(factor.variables[0])
                has_likelihood_state.update(factor.variables[1:])

                if factor.distribution != Distribution.CategoricalConditional:
                    # We can just set the distribution to conditional

                    # factor.distribution = Distribution.CategoricalConditional

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

            elif factor.role == FactorRole.Preference:
                has_preference_dist.add(factor.variables[0])

            elif factor.role is None:
                unlabeled_factors.add(factor_idx)

        # Group variables into sets
        no_likelihood_obs = has_preference_dist - has_likelihood_obs
        obs_vars = has_preference_dist | has_likelihood_obs
        state_vars = has_likelihood_state | has_transition
        unknown = self.vars_set - obs_vars - state_vars - control_vars

        # Deal with missing likelihoods for observation variables

        if no_likelihood_obs:
            diffs = []

            for var in no_likelihood_obs:
                likelihood_factor_found = False

                # We can check whether any unlabeled factors look like suitable likelihoods
                for factor_idx in unlabeled_factors:
                    factor = self.factors[factor_idx]
                    if len(factor.variables) > 1 and factor.variables[0] == var:
                        diffs.append(
                            {
                                "op": "replace",
                                "path": f"/factors/{factor_idx}/role",
                                "value": "likelihood",
                            }
                        )
                        # factor.role = FactorRole.Likelihood
                        has_likelihood_obs.add(var)
                        has_likelihood_state.update(factor.variables[1:])
                        unlabeled_factors.remove(factor_idx)
                        likelihood_factor_found = True
                        break

                if not likelihood_factor_found:
                    # We can add a new factor, connecting the observation to all state variables
                    diffs.append(
                        {
                            "op": "add",
                            "path": "/factors/-",
                            "value": {
                                "variables": [var] + list(state_vars),
                                "distribution": Distribution.CategoricalConditional,
                                "values": (
                                    np.ones(
                                        tuple(
                                            [
                                                self.variables[var].cardinality,
                                            ]
                                            + [self.variables[k].cardinality for k in state_vars]
                                        )
                                    )
                                    / self.variables[var].cardinality
                                ).tolist(),
                                "role": FactorRole.Likelihood,
                            },
                        }
                    )
                    has_likelihood_obs.add(var)
                    has_likelihood_state.update(state_vars)

            errors.extend(ObsVarMissingLikelihood(list(no_likelihood_obs), JsonPatch(diffs)))

        # Deal with missing likelihoods for state variables
        # NOTE: There's no obvious way to auto-add missing likelihoods in this case,
        # but we can check for missing labels

        no_likelihood_state = state_vars - has_likelihood_state
        if no_likelihood_state:
            diffs = []
            for var in no_likelihood_state:
                unlabeled_likelihood_idx = None
                # We can check whether any unlabeled factors look like suitable likelihoods
                for factor_idx in unlabeled_factors:
                    factor = self.factors[factor_idx]
                    maybe_obs = factor.variables[0]
                    if len(factor.variables) > 1 and var in factor.variables[1:] and maybe_obs in obs_vars | unknown:
                        diffs.append(
                            {
                                "op": "replace",
                                "path": f"/factors/{factor_idx}/role",
                                "value": "likelihood",
                            }
                        )
                        has_likelihood_state.add(var)
                        unknown.remove(maybe_obs)
                        obs_vars.add(maybe_obs)
                        has_likelihood_obs.add(maybe_obs)
                        unlabeled_likelihood_idx = factor_idx

                if unlabeled_likelihood_idx is not None:
                    unlabeled_factors.remove(unlabeled_likelihood_idx)

            errors.extend(
                StateVarMissingLikelihood(
                    list(no_likelihood_state),
                    JsonPatch(diffs),
                )
            )

        # Deal with missing transition factors
        no_transition = state_vars - has_transition
        if no_transition:
            diffs = []
            for var in no_transition:
                # We can add a new factor, connecting the state to itself
                diffs.append(
                    {
                        "op": "add",
                        "path": "/factors/-",
                        "value": {
                            "variables": [var, var],
                            "distribution": Distribution.CategoricalConditional,
                            "values": np.eye(self.variables[var].cardinality).tolist(),
                            "role": FactorRole.Transition,
                        },
                    }
                )
                has_transition.add(var)

            errors.extend(MissingTransition(list(no_transition), JsonPatch(diffs)))

        if unknown:
            # Non-auto-recoverable error
            errors.extend(VariableRoleIndeterminate(unknown))

        # For now, POMDPs must have at least one transition and at least one likelihood factor
        # TODO: Do we want to allow "trivial" simple POMDPs for which this doesn't hold?
        if not has_transition:
            errors.extend(NoTransitionFactors())
        if not has_likelihood_obs:
            errors.extend(NoLikelihoodFactors())

        # As above, fix the subclass then validate against superclass
        fixed = self.apply_patches(errors)
        all_errors = errors + super(POMDP, fixed).validate(raise_exceptions=False)

        if raise_exceptions and all_errors:
            raise all_errors

        return all_errors
