from pydantic import BaseModel
from typing import Any, Dict, Optional
import json
from jsonpatch import JsonPatch


class ErrorBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            JsonPatch: lambda v: json.loads(v.to_string()),
            Exception: lambda v: v.to_dict(),
        }


class _ValidationError(ErrorBaseModel):
    exception: str
    message: str
    parameters: Optional[Dict[str, Any]] = None
    patch: Optional[JsonPatch] = None


class ValidationError(Exception):
    def __init__(
        self,
        message: str,
        parameters: Optional[Dict[str, Any]] = None,
        patch: Optional[JsonPatch] = None,
    ):
        super().__init__(message)
        self._fields = _ValidationError(
            exception=self.__class__.__name__,
            message=message,
            parameters=parameters,
            patch=patch,
        )
        self.parameters = parameters
        self.patch = patch

    def __str__(self):
        return self._fields.model_dump_json()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            (self.args == other.args)
            and (type(self) is type(other))
            and (self.patch.to_string() == other.patch.to_string())
            if self.patch is not None
            else True
        )

    def to_dict(self):
        return self._fields.model_dump()

    def apply_patch_to(self, vfg_json: dict):
        if self.patch is not None:
            return self.patch.apply(vfg_json)

        return vfg_json


class ModelTypeError(ValidationError):
    pass


class JsonSerializationError(ValidationError):
    def __init__(self, message: str):
        super(JsonSerializationError, self).__init__(message)


class _ValidationErrors(ErrorBaseModel):
    errors: list[_ValidationError]


class ValidationErrors(Exception):
    def __init__(
        self,
        errors: list[ValidationError],
    ):
        super(Exception, self).__init__(
            "Errors occurred during model validation. \n Catch this exception and check the .errors field for details. \n VFG.apply_patches(errors) will automatically correct recoverable errors."
        )
        self.errors = errors
        self._error_info = _ValidationErrors(errors=[e._fields for e in errors])

    def __iter__(self):
        return iter(self.errors)

    def __len__(self):
        return len(self.errors)

    def __getitem__(self, i):
        return self.errors[i]

    def __str__(self):
        return self._error_info.model_dump_json()

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return self._error_info.model_dump()

    def to_dicts(self):
        return [e.to_dict() for e in self.errors]

    def __add__(self, other):
        if isinstance(other, ValidationErrors):
            return ValidationErrors(errors=self.errors + other.errors)
        elif isinstance(other, ValidationError):
            return ValidationErrors(errors=self.errors + [other])
        elif other is None:
            return self
        else:
            raise ValueError(f"Cannot add {type(other)} to ValidationErrors")

    def __iadd__(self, other: ValidationError):
        self.errors.append(other)
        self._error_info = _ValidationErrors(errors=[e._fields for e in self.errors])
        return self

    def __eq__(self, other):
        return all([e1 == e2 for (e1, e2) in zip(self.errors, other.errors)])

    def __ne__(self, other):
        return self.errors != other.errors

    def extend(self, error: Optional[ValidationError] = None):
        if error:
            self.errors.append(error)
            self._error_info = _ValidationErrors(errors=[e._fields for e in self.errors])

    @property
    def model_type_errors(self):
        return [e for e in self.errors if isinstance(e, ModelTypeError)]

    @property
    def patches(self):
        return [e.patch for e in self.errors if e.patch is not None]

    @property
    def non_recoverable_errors(self):
        return [e for e in self.errors if e.patch is None]

    @staticmethod
    def new():
        return ValidationErrors(errors=[])


def is_valid_name(var_name: str) -> bool:
    return len(var_name) > 0 and all([c.isalnum() or c == "_" or c == "-" or c == "." for c in var_name])
