from contextlib import asynccontextmanager
from contextvars import ContextVar
from enum import Enum
from typing import Callable, Union

from pydantic import BaseModel

from planar.logging import get_logger
from planar.workflows.models import Workflow, WorkflowStep

logger = get_logger(__name__)


class Notification(str, Enum):
    WORKFLOW_STARTED = "workflow-started"
    WORKFLOW_SUSPENDED = "workflow-suspended"
    WORKFLOW_RESUMED = "workflow-resumed"
    WORKFLOW_SUCCEEDED = "workflow-succeeded"
    WORKFLOW_FAILED = "workflow-failed"
    STEP_RUNNING = "step-running"
    STEP_SUCCEEDED = "step-succeeded"
    STEP_FAILED = "step-failed"


class WorkflowNotification(BaseModel):
    kind: Notification
    data: Union[Workflow, WorkflowStep]


WorkflowNotificationCallback = Callable[[WorkflowNotification], None]

workflow_notification_callback_var: ContextVar[WorkflowNotificationCallback] = (
    ContextVar("workflow_notification_callback")
)


def workflow_notify(workflow: Workflow, kind: Notification):
    callback = workflow_notification_callback_var.get(None)
    if callback is not None:
        logger.debug("notifying workflow event", kind=kind, workflow_id=workflow.id)
        callback(WorkflowNotification(kind=kind, data=workflow))


def workflow_started(workflow: Workflow):
    return workflow_notify(workflow, Notification.WORKFLOW_STARTED)


def workflow_suspended(workflow: Workflow):
    return workflow_notify(workflow, Notification.WORKFLOW_SUSPENDED)


def workflow_resumed(workflow: Workflow):
    return workflow_notify(workflow, Notification.WORKFLOW_RESUMED)


def workflow_succeeded(workflow: Workflow):
    return workflow_notify(workflow, Notification.WORKFLOW_SUCCEEDED)


def workflow_failed(workflow: Workflow):
    return workflow_notify(workflow, Notification.WORKFLOW_FAILED)


def step_notify(step: WorkflowStep, kind: Notification):
    callback = workflow_notification_callback_var.get(None)
    if callback is not None:
        logger.debug(
            "notifying step event",
            kind=kind,
            workflow_id=step.workflow_id,
            step_id=step.step_id,
        )
        callback(WorkflowNotification(kind=kind, data=step))


def step_running(step: WorkflowStep):
    return step_notify(step, Notification.STEP_RUNNING)


def step_succeeded(step: WorkflowStep):
    return step_notify(step, Notification.STEP_SUCCEEDED)


def step_failed(step: WorkflowStep):
    return step_notify(step, Notification.STEP_FAILED)


@asynccontextmanager
async def workflow_notification_context(callback: WorkflowNotificationCallback):
    """Context manager for setting up and tearing down Workflow notification context"""

    tok = workflow_notification_callback_var.set(callback)
    try:
        yield
    finally:
        workflow_notification_callback_var.reset(tok)
