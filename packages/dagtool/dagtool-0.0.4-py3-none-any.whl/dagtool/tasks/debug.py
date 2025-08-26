import json
from collections.abc import Sequence
from typing import Any, Literal, cast

from airflow.exceptions import AirflowException, AirflowSkipException
from airflow.models import DAG, Operator
from airflow.models.baseoperator import BaseOperator
from airflow.utils.context import Context as AirflowContext
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import Context, OperatorTask


class RaiseOperator(BaseOperator):
    ui_color: str = "#ef3a25"
    inherits_from_empty_operator: bool = False
    template_fields: Sequence[str] = ("message",)

    def __init__(
        self, message: str | None, skipped: bool = False, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.skipped: bool = skipped
        self.message: str = (
            message or "Default message raise from Raise Operator."
        )

    def execute(self, context: Context) -> Any:
        if self.skipped:
            raise AirflowSkipException(self.message)
        raise AirflowException(self.message)


class RaiseTask(OperatorTask):
    op: Literal["raise"]
    message: str | None = Field(default=None)
    skipped: bool = False

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        return RaiseOperator(
            message=self.message,
            skipped=self.skipped,
            dag=dag,
            task_group=task_group,
            **self.task_kwargs(),
        )


class DebugOperator(BaseOperator):
    """Operator that does literally nothing.

    It can be used to group tasks in a DAG.
    The task is evaluated by the scheduler but never processed by the executor.
    """

    ui_color: str = "#fcf5a2"
    inherits_from_empty_operator: bool = False
    template_fields: Sequence[str] = ("debug",)

    def __init__(self, debug: dict[str, Any], **kwargs) -> None:
        super().__init__(**kwargs)
        self.debug: dict[str, Any] = debug

    def execute(self, context: AirflowContext) -> None:
        """Debug Operator execute method that only show parameters that passing
        from the template config.

        Args:
            context (AirflowContext): An Airflow Context object.
        """
        self.log.info("Start DEBUG Parameters:")
        for k, v in self.debug.items():
            self.log.info(f"> {k}: {v}")

        self.log.info("Start DEBUG Context:")
        ctx: AirflowContext = cast(AirflowContext, dict(context))
        self.log.info(json.dumps(ctx, indent=2, default=str))


class DebugTask(OperatorTask):
    """Debug Task model that inherit from Operator task."""

    op: Literal["debug"]
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="A parameters that want to logging.",
    )

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Debug Operator object."""
        return DebugOperator(
            task_group=task_group,
            dag=dag,
            debug=self.params,
            **self.task_kwargs(),
        )
