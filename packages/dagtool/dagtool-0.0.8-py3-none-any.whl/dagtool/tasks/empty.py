from typing import Literal

try:
    from airflow.providers.standard.operators.empty import EmptyOperator
except ImportError:
    from airflow.operators.empty import EmptyOperator

from dagtool.tasks.__abc import DAG, BaseTask, Context, Operator, TaskGroup


class EmptyTask(BaseTask):
    """Empty Task model."""

    uses: Literal["empty"]

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
