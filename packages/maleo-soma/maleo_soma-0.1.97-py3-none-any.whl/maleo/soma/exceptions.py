import traceback as tb
from typing import Dict, Generic, Optional, Tuple, Type, Union
from uuid import UUID
from maleo.soma.enums.logging import LogLevel
from maleo.soma.schemas.authentication import AuthenticationT
from maleo.soma.schemas.error import (
    ErrorSchema,
    BadRequestErrorSchema,
    UnauthorizedErrorSchema,
    ForbiddenErrorSchema,
    NotFoundErrorSchema,
    MethodNotAllowedErrorSchema,
    ConflictErrorSchema,
    UnprocessableEntityErrorSchema,
    TooManyRequestsErrorSchema,
    InternalServerErrorSchema,
    DatabaseErrorSchema,
    NotImplementedErrorSchema,
    BadGatewayErrorSchema,
    ServiceUnavailableErrorSchema,
)
from maleo.soma.schemas.error.spec import (
    ErrorSpecSchema,
    BadRequestErrorSpecSchema,
    UnauthorizedErrorSpecSchema,
    ForbiddenErrorSpecSchema,
    NotFoundErrorSpecSchema,
    MethodNotAllowedErrorSpecSchema,
    ConflictErrorSpecSchema,
    UnprocessableEntityErrorSpecSchema,
    TooManyRequestsErrorSpecSchema,
    InternalServerErrorSpecSchema,
    DatabaseErrorSpecSchema,
    NotImplementedErrorSpecSchema,
    BadGatewayErrorSpecSchema,
    ServiceUnavailableErrorSpecSchema,
)
from maleo.soma.schemas.operation.context import OperationContextSchema
from maleo.soma.schemas.operation.resource import (
    CreateFailedResourceOperationSchema,
    DeleteFailedResourceOperationSchema,
    ReadFailedResourceOperationSchema,
    UpdateFailedResourceOperationSchema,
    generate_failed_resource_operation,
)
from maleo.soma.schemas.operation.resource.action import AllResourceOperationAction
from maleo.soma.schemas.operation.system import FailedSystemOperationSchema
from maleo.soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.resource import Resource
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.types.base import ListOfStrings, OptionalAny, StringToAnyDict
from maleo.soma.utils.logging import BaseLogger


class Error(Exception, Generic[AuthenticationT]):
    """Base class for all exceptions raised by Maleo"""

    spec: ErrorSpecSchema

    def __init__(
        self,
        *args: object,
        service_context: Optional[ServiceContext],
        operation_id: UUID,
        operation_context: OperationContextSchema,
        operation_timestamp: OperationTimestamp,
        operation_summary: str,
        operation_action: Union[
            AllResourceOperationAction,
            SystemOperationActionSchema,
        ],
        request_context: Optional[RequestContext],
        authentication: AuthenticationT,
        resource: Optional[Resource] = None,
        details: OptionalAny = None,
    ) -> None:
        super().__init__(*args)
        self.service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        self.operation_id = operation_id
        self.operation_context = operation_context
        self.operation_timestamp = (
            operation_timestamp
            if operation_timestamp is not None
            else OperationTimestamp.now()
        )
        self.operation_summary = operation_summary
        self.request_context = request_context
        self.authentication = authentication
        self.operation_action = operation_action
        self.resource = resource
        self.details = details

    @property
    def traceback(self) -> ListOfStrings:
        return tb.format_exception(self)

    @property
    def _schema_dict(self) -> StringToAnyDict:
        return {
            **self.spec.model_dump(),
            "details": self.details,
            "traceback": self.traceback,
        }

    @property
    def schema(self) -> ErrorSchema:
        return ErrorSchema.model_validate(self._schema_dict)

    @property
    def operation_schema(self) -> Union[
        CreateFailedResourceOperationSchema[AuthenticationT],
        ReadFailedResourceOperationSchema[AuthenticationT],
        UpdateFailedResourceOperationSchema[AuthenticationT],
        DeleteFailedResourceOperationSchema[AuthenticationT],
        FailedSystemOperationSchema[AuthenticationT],
    ]:
        if isinstance(self.operation_action, SystemOperationActionSchema):
            return FailedSystemOperationSchema[AuthenticationT](
                service_context=self.service_context,
                id=self.operation_id,
                context=self.operation_context,
                timestamp=self.operation_timestamp,
                summary="Failed system operation",
                error=self.schema,
                request_context=self.request_context,
                authentication=self.authentication,
                action=self.operation_action,
            )
        else:
            if self.resource is None:
                raise ValueError(
                    "Resource must be given for resource operation exception"
                )
            return generate_failed_resource_operation(
                action=self.operation_action,
                service_context=self.service_context,
                id=self.operation_id,
                context=self.operation_context,
                timestamp=self.operation_timestamp,
                summary=self.operation_summary,
                error=self.schema,
                request_context=self.request_context,
                authentication=self.authentication,
                resource=self.resource,
            )


class ClientError(Error[AuthenticationT], Generic[AuthenticationT]):
    """Base class for all client error (HTTP 4xx) responses"""


class BadRequest(ClientError[AuthenticationT], Generic[AuthenticationT]):
    spec = BadRequestErrorSpecSchema()

    @property
    def schema(self) -> BadRequestErrorSchema:
        return BadRequestErrorSchema.model_validate(self._schema_dict)


class Unauthorized(ClientError[AuthenticationT], Generic[AuthenticationT]):
    spec = UnauthorizedErrorSpecSchema()

    @property
    def schema(self) -> UnauthorizedErrorSchema:
        return UnauthorizedErrorSchema.model_validate(self._schema_dict)


class Forbidden(ClientError[AuthenticationT], Generic[AuthenticationT]):
    spec = ForbiddenErrorSpecSchema()

    @property
    def schema(self) -> ForbiddenErrorSchema:
        return ForbiddenErrorSchema.model_validate(self._schema_dict)


class NotFound(ClientError[AuthenticationT], Generic[AuthenticationT]):
    spec = NotFoundErrorSpecSchema()

    @property
    def schema(self) -> NotFoundErrorSchema:
        return NotFoundErrorSchema.model_validate(self._schema_dict)


class MethodNotAllowed(ClientError[AuthenticationT], Generic[AuthenticationT]):
    spec = MethodNotAllowedErrorSpecSchema()

    @property
    def schema(self) -> MethodNotAllowedErrorSchema:
        return MethodNotAllowedErrorSchema.model_validate(self._schema_dict)


class Conflict(ClientError[AuthenticationT], Generic[AuthenticationT]):
    spec = ConflictErrorSpecSchema()

    @property
    def schema(self) -> ConflictErrorSchema:
        return ConflictErrorSchema.model_validate(self._schema_dict)


class UnprocessableEntity(ClientError[AuthenticationT], Generic[AuthenticationT]):
    spec = UnprocessableEntityErrorSpecSchema()

    @property
    def schema(self) -> UnprocessableEntityErrorSchema:
        return UnprocessableEntityErrorSchema.model_validate(self._schema_dict)


class TooManyRequests(ClientError[AuthenticationT], Generic[AuthenticationT]):
    spec = TooManyRequestsErrorSpecSchema()

    @property
    def schema(self) -> TooManyRequestsErrorSchema:
        return TooManyRequestsErrorSchema.model_validate(self._schema_dict)


class ServerError(Error[AuthenticationT], Generic[AuthenticationT]):
    """Base class for all server error (HTTP 5xx) responses"""


class InternalServerError(ServerError[AuthenticationT], Generic[AuthenticationT]):
    spec = InternalServerErrorSpecSchema()

    @property
    def schema(self) -> InternalServerErrorSchema:
        return InternalServerErrorSchema.model_validate(self._schema_dict)


class DatabaseError(InternalServerError[AuthenticationT], Generic[AuthenticationT]):
    spec = DatabaseErrorSpecSchema()

    @property
    def schema(self) -> DatabaseErrorSchema:
        return DatabaseErrorSchema.model_validate(self._schema_dict)


class NotImplemented(ServerError[AuthenticationT], Generic[AuthenticationT]):
    spec = NotImplementedErrorSpecSchema()

    @property
    def schema(self) -> NotImplementedErrorSchema:
        return NotImplementedErrorSchema.model_validate(self._schema_dict)


class BadGateway(ServerError[AuthenticationT], Generic[AuthenticationT]):
    spec = BadGatewayErrorSpecSchema()

    @property
    def schema(self) -> BadGatewayErrorSchema:
        return BadGatewayErrorSchema.model_validate(self._schema_dict)


class ServiceUnavailable(ServerError[AuthenticationT], Generic[AuthenticationT]):
    spec = ServiceUnavailableErrorSpecSchema()

    @property
    def schema(self) -> ServiceUnavailableErrorSchema:
        return ServiceUnavailableErrorSchema.model_validate(self._schema_dict)


def from_resource_http_request(
    status_code: int,
    service_context: Optional[ServiceContext],
    operation_id: UUID,
    operation_context: OperationContextSchema,
    operation_timestamp: OperationTimestamp,
    operation_action: AllResourceOperationAction,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    logger: BaseLogger,
) -> Error[AuthenticationT]:
    """Create appropriate error based on HTTP status code"""

    error_mapping: Dict[int, Tuple[Type[Error[AuthenticationT]], str]] = {
        400: (
            BadRequest[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Bad Request response",
        ),
        401: (
            Unauthorized[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Unauthorized response",
        ),
        403: (
            Forbidden[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Forbidden response",
        ),
        404: (
            NotFound[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Not Found response",
        ),
        405: (
            MethodNotAllowed[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Method Not Allowed response",
        ),
        409: (
            Conflict[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Conflict response",
        ),
        422: (
            UnprocessableEntity[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Unprocessable Entity response",
        ),
        429: (
            TooManyRequests[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Too Many Requests response",
        ),
        500: (
            InternalServerError[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Internal Server Error response",
        ),
        501: (
            NotImplemented[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Not Implemented response",
        ),
        502: (
            BadGateway[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Bad Gateway response",
        ),
        503: (
            ServiceUnavailable[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to Service Unavailable response",
        ),
    }

    error_class, summary = error_mapping.get(
        status_code,
        (
            InternalServerError[AuthenticationT],
            f"Failed requesting '{resource.aggregate()}' due to unexpected error",
        ),
    )

    error = error_class(
        service_context=service_context,
        operation_id=operation_id,
        operation_context=operation_context,
        operation_timestamp=operation_timestamp,
        operation_summary=summary,
        operation_action=operation_action,
        request_context=request_context,
        authentication=authentication,
        resource=resource,
    )
    error.operation_schema.log(logger, LogLevel.ERROR)
    return error
