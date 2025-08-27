import asyncio
import os
import psutil
from collections import deque
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from maleo.soma.dtos.configurations.system.resource import ResourceUsageConfigurationDTO
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import (
    OperationOrigin,
    OperationLayer,
    OperationTarget,
    SystemOperationType,
)
from maleo.soma.schemas.operation.context import (
    OperationContextSchema,
    OperationOriginSchema,
    OperationLayerSchema,
    OperationTargetSchema,
)
from maleo.soma.schemas.operation.system import SuccessfulSystemOperationSchema
from maleo.soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.schemas.system.resource import CPUUsage, ResourceUsage
from maleo.soma.utils.logging import ApplicationLogger


async def monitor_resource_usage(
    service_context: Optional[ServiceContext],
    configurations: ResourceUsageConfigurationDTO,
    logger: ApplicationLogger,
):
    """
    Periodically updates both raw and smoothed CPU & memory usage.
    - raw_cpu_percent: instantaneous value (may be 0.0 if idle)
    - smooth_cpu_percent: moving average across last N samples
    """
    service_context = (
        service_context if service_context is not None else ServiceContext.from_env()
    )

    operation_context = OperationContextSchema(
        origin=OperationOriginSchema(type=OperationOrigin.SERVICE, details=None),
        layer=OperationLayerSchema(type=OperationLayer.INFRASTRUCTURE, details=None),
        target=OperationTargetSchema(type=OperationTarget.MONITORING, details=None),
    )

    operation_action = SystemOperationActionSchema(
        type=SystemOperationType.METRIC_REPORT, details={"type": "resource_usage"}
    )

    process = psutil.Process(os.getpid())
    cpu_window = deque(maxlen=configurations.window)

    while True:
        operation_id = uuid4()
        executed_at = datetime.now(tz=timezone.utc)

        # Raw CPU usage since last call
        raw_cpu = process.cpu_percent(interval=None)

        # Update moving window for smoothing
        cpu_window.append(raw_cpu)
        smooth_cpu = sum(cpu_window) / len(cpu_window)

        # Memory usage in MB
        memory_usage = process.memory_info().rss / (1024 * 1024)

        completed_at = datetime.now(tz=timezone.utc)

        cpu_usage = CPUUsage(raw=raw_cpu, smooth=smooth_cpu)

        resource_usage = ResourceUsage(cpu=cpu_usage, memory=memory_usage)

        SuccessfulSystemOperationSchema[None, ResourceUsage](
            service_context=service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp(
                executed_at=executed_at,
                completed_at=completed_at,
                duration=(completed_at - executed_at).total_seconds(),
            ),
            summary=f"Successfully calculated resource usage - CPU | Raw: {raw_cpu:.2f}% | Smooth: {smooth_cpu:.2f}% - Memory: {memory_usage:.2f}MB",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=resource_usage,
        ).log(logger, LogLevel.INFO)

        await asyncio.sleep(configurations.interval)
