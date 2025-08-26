import logging
from typing import Any

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from dagtool.tasks import BaseTask, Context
from dagtool.tasks.debug import DebugOperator


def say_hi(name: Any) -> str:
    if not isinstance(name, str):
        logging.info(f"Hello {name.name}")
        return name.name

    logging.info(f"Hello {name}")
    return name


class CustomTask(BaseTask):
    name: str

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> TaskGroup:
        with TaskGroup(
            "custom_task_group", dag=dag, parent_group=task_group
        ) as tg:
            t1 = EmptyOperator(task_id="start", dag=dag)
            t2 = DebugOperator(
                task_id=f"for_{self.name.lower()}",
                debug={"name": self.name},
                dag=dag,
            )
            t1 >> t2
        return tg
