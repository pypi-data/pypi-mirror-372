from typing import Literal

from airflow.models import DAG, Operator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from .__abc import Context, OperatorTask


class EmptyTask(OperatorTask):
    """Empty Task model."""

    op: Literal["empty"]

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Empty Operator object."""
        return EmptyOperator(
            task_group=task_group,
            dag=dag,
            **self.task_kwargs(),
        )
