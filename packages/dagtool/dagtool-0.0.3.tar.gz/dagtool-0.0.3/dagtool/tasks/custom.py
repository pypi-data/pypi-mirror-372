from typing import Any, Literal

from airflow import DAG
from airflow.models import Operator
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import BaseTask, Context, OperatorTask


class CustomTask(OperatorTask):
    """Custom Task model."""

    op: Literal["custom_task"]
    uses: str = Field(description="A custom building function name.")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "A mapping of parameters that want to pass to Custom Task model "
            "before build."
        ),
    )

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator | TaskGroup:
        """Build with Custom builder function."""
        ctx: Context = context or {}
        custom_tasks: dict[str, type[BaseTask]] = ctx["tasks"]
        if self.uses not in custom_tasks:
            raise ValueError(
                f"Custom task need to pass to `tasks` argument, {self.uses}, first."
            )
        op: type[BaseTask] = custom_tasks[self.uses]
        model: BaseTask = op.model_validate(self.params)
        return model.build(
            dag=dag,
            task_group=task_group,
            context=context | self.params,
        )


class CustomOperatorTask(OperatorTask):
    op: Literal["operator"]
    operator_name: str = Field(
        alias="from",
        description="An Airflow operator that import from external provider.",
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "A mapping of parameters that want to pass to Airflow Operator"
        ),
    )

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        ctx: Context = context or {}
        custom_opts: dict[str, type[Operator]] = ctx["operators"]
        if self.operator_name not in custom_opts:
            raise ValueError(
                f"Operator need to pass to `operator` argument, {self.operator_name}, first."
            )
        op: type[Operator] = custom_opts[self.operator_name]
        return op(
            dag=dag,
            task_group=task_group,
            **self.params,
            **self.task_kwargs(),
        )
