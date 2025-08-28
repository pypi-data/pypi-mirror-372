# -*- coding: utf-8 -*-

from __future__ import annotations

import warnings
from typing import Annotated, Dict, List, Optional, Literal
from zipfile import ZipFile

from pydantic import BaseModel, Field

from ..v_2_0_0.vfg_2_0_0 import VFG as VFG_2_0_0, Variable, Factor, NpyFilepath

__all__ = ["VFG", "Plate", "NpyFilepath", "Variable", "Factor"]

from ... import ValidationError, ValidationErrors

from ...project.model import GeniusProjectFile

warnings.simplefilter("always", ResourceWarning)


class Plate(BaseModel):
    factors: Annotated[List[str], Field(min_length=1)]
    """The factors that are part of this plate"""
    variables: Annotated[List[str], Field(min_length=1)]
    """The variables that are part of this plate"""
    size: int
    """The size of the plate (number of repetitions)"""


class VFG(VFG_2_0_0):
    version: Literal["2.1.0"] = "2.1.0"
    plates: Dict[str, Plate] = Field(default_factory=dict)

    def __init__(
        self,
        name: Optional[str] = None,
        variables: Optional[Dict[str, Variable]] = None,
        factors: Optional[Dict[str, Factor]] = None,
        plates: Optional[Dict[str, Plate]] = None,
        gpf: Optional[GeniusProjectFile] = None,
        gpf_zip_file: Optional[ZipFile] = None,
        **data,
    ):
        if plates is None:
            plates = {}

        super().__init__(
            name=name, variables=variables, factors=factors, gpf=gpf, gpf_zip_file=gpf_zip_file, plates=plates, **data
        )

    def vfg_validate(
        self,
        raise_exceptions: bool = True,
    ) -> ValidationErrors:
        """
        Determines if the given VFG is valid and tries to infer its type.
        This method extends the standard VFG 2.0.0 validation to also implement plate validation.

        Args:
            raise_exceptions (bool): If True, raise an exception on any validation warning
        Returns:
            ValidationErrors if the VFG is invalid, otherwise an empty list of errors, and the inferred VFG type
        """
        errors: List[ValidationError] = []

        # just carry out plate validation
        defined_factor_keys = set(self.factors.keys())

        for plate_name, plate in self.plates.items():
            for factor_name in plate.factors:
                if factor_name not in defined_factor_keys:
                    errors.append(
                        ValidationError(
                            message=f"Factor '{factor_name}' in plate '{plate_name}' is not defined in the graph's main factors.",
                            parameters={"plate": plate_name, "factor": factor_name},
                        )
                    )

        # handle return
        errors_obj = super().vfg_validate(raise_exceptions=raise_exceptions)
        errors_obj.errors.extend(errors)
        if raise_exceptions and len(errors) > 0:
            raise errors_obj
        else:
            return errors_obj
