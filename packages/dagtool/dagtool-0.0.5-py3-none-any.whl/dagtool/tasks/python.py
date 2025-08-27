from collections.abc import Sequence
from typing import Any, Literal

from airflow import DAG
from airflow.models import Operator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import Context, OperatorTask


class DataReader:
    template_fields: Sequence[str] = ("name",)

    def __init__(self, data: str):
        self.name = data


class PythonTask(OperatorTask):
    """Python Task model."""

    op: Literal["python"]
    caller: str = Field(description="A Python function name.")
    params: dict[str, Any] = Field(default_factory=dict)

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Python Operator object."""
        ctx: dict[str, Any] = context or {}
        python_callers: dict[str, Any] = ctx["python_callers"]
        if self.caller not in python_callers:
            raise ValueError(
                f"Python task need to pass python callers function, "
                f"{self.caller}, first."
            )
        return PythonOperator(
            task_group=task_group,
            dag=dag,
            python_callable=python_callers[self.caller],
            # op_args=[DataReader(data="{{ run_id }}")],
            op_kwargs={"name": DataReader(data="{{ run_id }}")} | self.params,
            **self.task_kwargs(),
        )
