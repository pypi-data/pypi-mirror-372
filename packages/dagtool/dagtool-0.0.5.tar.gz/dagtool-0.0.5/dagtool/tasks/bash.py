from typing import Literal

from airflow.models import DAG, Operator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import Context, OperatorTask


class BashTask(OperatorTask):
    """Bash Task model that will represent to Airflow BashOperator object."""

    op: Literal["bash"] = Field(description="An operator type for bash model.")
    command: str = Field(description="A bash command or bash file")
    env: dict[str, str] | None = Field(
        default=None,
        description="A mapping of environment variable.",
    )
    append_env: bool = False
    output_encoding: str = Field(
        default="utf-8",
        description="Output encoding of bash command.",
    )
    skip_on_exit_code: int | list[int] | None = Field(default=99)
    cwd: str | None = None

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Bash Operator object."""
        return BashOperator(
            bash_command=self.command,
            env=self.env,
            append_env=self.append_env,
            output_encoding=self.output_encoding,
            skip_on_exit_code=self.skip_on_exit_code,
            cwd=self.cwd,
            dag=dag,
            task_group=task_group,
            **self.task_kwargs(),
        )
