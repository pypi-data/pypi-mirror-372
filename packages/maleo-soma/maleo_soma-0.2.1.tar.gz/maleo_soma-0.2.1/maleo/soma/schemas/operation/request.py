from typing import Generic, Literal
from maleo.soma.enums.operation import (
    OperationType,
)
from maleo.soma.mixins.general import SuccessT
from maleo.soma.schemas.authentication import AuthenticationT
from maleo.soma.schemas.error import (
    NoErrorMixin,
    OptionalErrorMixin,
)
from maleo.soma.schemas.operation.base import BaseOperationSchema
from maleo.soma.schemas.response import ResponseContextMixin
from maleo.soma.schemas.operation.resource.action import (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    ResourceOperationActionSchemaT,
)


class RequestOperationSchema(
    ResponseContextMixin,
    BaseOperationSchema[SuccessT, AuthenticationT, ResourceOperationActionSchemaT],
    Generic[SuccessT, AuthenticationT, ResourceOperationActionSchemaT],
):
    type: OperationType = OperationType.REQUEST


class FailedRequestOperationSchema(
    OptionalErrorMixin,
    RequestOperationSchema[
        Literal[False], AuthenticationT, ResourceOperationActionSchemaT
    ],
    Generic[AuthenticationT, ResourceOperationActionSchemaT],
):
    success: Literal[False] = False
    summary: str = "Failed processing request"


class CreateFailedRequestOperationSchema(
    FailedRequestOperationSchema[AuthenticationT, CreateResourceOperationAction]
):
    pass


class ReadFailedRequestOperationSchema(
    FailedRequestOperationSchema[AuthenticationT, ReadResourceOperationAction]
):
    pass


class UpdateFailedRequestOperationSchema(
    FailedRequestOperationSchema[AuthenticationT, UpdateResourceOperationAction]
):
    pass


class DeleteFailedRequestOperationSchema(
    FailedRequestOperationSchema[AuthenticationT, DeleteResourceOperationAction]
):
    pass


class SuccessfulRequestOperationSchema(
    NoErrorMixin,
    RequestOperationSchema[
        Literal[True], AuthenticationT, ResourceOperationActionSchemaT
    ],
    Generic[AuthenticationT, ResourceOperationActionSchemaT],
):
    success: Literal[True] = True
    summary: str = "Successfully processed request"


class CreateSuccessfulRequestOperationSchema(
    SuccessfulRequestOperationSchema[AuthenticationT, CreateResourceOperationAction]
):
    pass


class ReadSuccessfulRequestOperationSchema(
    SuccessfulRequestOperationSchema[AuthenticationT, ReadResourceOperationAction]
):
    pass


class UpdateSuccessfulRequestOperationSchema(
    SuccessfulRequestOperationSchema[AuthenticationT, UpdateResourceOperationAction]
):
    pass


class DeleteSuccessfulRequestOperationSchema(
    SuccessfulRequestOperationSchema[AuthenticationT, DeleteResourceOperationAction]
):
    pass
