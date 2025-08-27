from typing import Generic, Literal
from maleo.soma.mixins.general import SuccessT
from maleo.soma.enums.operation import OperationType
from maleo.soma.schemas.authentication import AuthenticationT
from maleo.soma.schemas.error import (
    NoErrorMixin,
    ErrorMixin,
)
from maleo.soma.schemas.operation.base import BaseOperationSchema
from maleo.soma.schemas.operation.result import (
    AnyOperationResultMixin,
    NoOperationResultMixin,
    OperationResultSchemaT,
    OptionalOperationResultMixin,
)
from .action import SystemOperationActionSchema


class SystemOperationSchema(
    AnyOperationResultMixin,
    BaseOperationSchema[SuccessT, AuthenticationT, SystemOperationActionSchema],
    Generic[SuccessT, AuthenticationT],
):
    type: OperationType = OperationType.SYSTEM


class FailedSystemOperationSchema(
    NoOperationResultMixin,
    ErrorMixin,
    SystemOperationSchema[Literal[False], AuthenticationT],
    Generic[AuthenticationT],
):
    success: Literal[False] = False


class SuccessfulSystemOperationSchema(
    OptionalOperationResultMixin[OperationResultSchemaT],
    NoErrorMixin,
    SystemOperationSchema[Literal[True], AuthenticationT],
    Generic[AuthenticationT, OperationResultSchemaT],
):
    success: Literal[True] = True
