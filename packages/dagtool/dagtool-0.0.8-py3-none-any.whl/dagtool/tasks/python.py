from typing import Any, Literal

try:
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:
    from airflow.operators.python import PythonOperator

from pydantic import Field

from dagtool.tasks.__abc import DAG, BaseTask, Context, Operator, TaskGroup


class PythonTask(BaseTask):
    """Python Task model."""

    uses: Literal["python"]
    caller: str = Field(
        description=(
            "A Python function name that already set on the `python_callers` "
            "parameter."
        )
    )
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
            op_kwargs=self.params,
            **self.task_kwargs(),
        )
