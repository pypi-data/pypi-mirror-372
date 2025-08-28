# -*- coding: utf-8 -*-
from .errors import (
    ValidationError as ValidationError,
    ModelTypeError as ModelTypeError,
    JsonSerializationError as JsonSerializationError,
    ValidationErrors as ValidationErrors,
    MissingDistribution as MissingDistribution,
    MultipleDistributions as MultipleDistributions,
    CyclicGraph as CyclicGraph,
    MultivariateDistributionNotConditional as MultivariateDistributionNotConditional,
    InvalidFactorRole as InvalidFactorRole,
    MissingFactors as MissingFactors,
    InvalidVariableName as InvalidVariableName,
    InvalidVariableItemCount as InvalidVariableItemCount,
    MissingVariable as MissingVariable,
    MissingProbability as MissingProbability,
    VariableMissingInVariableList as VariableMissingInVariableList,
    IncorrectTensorShape as IncorrectTensorShape,
    DuplicateVariablesError as DuplicateVariablesError,
    DuplicateElementsError as DuplicateElementsError,
    NormalizationError as NormalizationError,
    MissingTransition as MissingTransition,
    StateVarMissingLikelihood as StateVarMissingLikelihood,
    ObsVarMissingLikelihood as ObsVarMissingLikelihood,
    VariableRoleIndeterminate as VariableRoleIndeterminate,
    NoTransitionFactors as NoTransitionFactors,
    NoLikelihoodFactors as NoLikelihoodFactors,
    NonPotentialInMRF as NonPotentialInMRF,
    NegativePotentialError as NegativePotentialError,
)

from .versions.v_2_0_0.vfg_2_0_0 import (
    VFG as VFG,
    DUMMY_CONTROL_STATE_NAME as DUMMY_CONTROL_STATE_NAME,
    # todo vfg2.0: uncomment when ready
    # BayesianNetwork as BayesianNetwork,
    # MarkovRandomField as MarkovRandomField,
    # POMDP as POMDP,
    Factor as Factor,
    Variable as Variable,
    ModelType as ModelType,
    # Smoothing as Smoothing,
    # NumPreviousObservations as NumPreviousObservations,
    FactorInitialization as FactorInitialization,
    # Metadata as Metadata,
    # InitializationStrategy as InitializationStrategy,
    GenerateJsonSchemaIgnoreInvalid as GenerateJsonSchemaIgnoreInvalid,
)
from .versions.v_2_0_0.vfg_2_0_0_utils import (
    vfg_from_json as vfg_from_json,
    vfg_upgrade as vfg_upgrade,
    infer_variable_domain as infer_variable_domain,
)

from .versions.v_0_5_0.vfg_0_5_0_utils import (
    vfg_to_json_schema as vfg_to_json_schema,
)

from .project.utils import (
    load_single_tensor as load_single_tensor,
    get_models_list as get_models_list,
)

from .project.serialization_backwards_compat import (
    load_project_050 as load_project_050,
    save_project_050 as save_project_050,
)

from .project.model import GeniusProjectFile as GeniusProjectFile

from .api import load_model as load_model


# by request
@property
def __version__() -> str:
    import importlib.metadata

    return importlib.metadata.version("pyvfg")


# for compatibility
VFGPydanticType = VFG
validate_graph = VFG.validate
