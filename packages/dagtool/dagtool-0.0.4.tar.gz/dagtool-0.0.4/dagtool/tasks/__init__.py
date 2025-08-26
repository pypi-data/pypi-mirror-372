from typing import Annotated, Any, Literal, Union

from airflow.models import DAG, Operator
from airflow.utils.task_group import TaskGroup
from pydantic import Discriminator, Field, Tag

from dagtool.utils import TaskMapped, set_upstream

from .__abc import BaseAirflowTask, BaseTask, Context, OperatorTask
from .bash import BashTask
from .custom import CustomOperatorTask, CustomTask
from .debug import DebugTask, RaiseTask
from .empty import EmptyTask
from .python import PythonTask

Task = Annotated[
    Union[
        EmptyTask,
        DebugTask,
        BashTask,
        PythonTask,
        CustomTask,
        CustomOperatorTask,
        RaiseTask,
    ],
    Field(
        discriminator="op",
        description="All supported Operator Tasks.",
    ),
]


class GroupTask(BaseAirflowTask):
    """Group of Task model that will represent Airflow Task Group object."""

    group: str = Field(description="A task group name.")
    type: Literal["group"] = Field(default="group")
    tasks: list["AnyTask"] = Field(
        default_factory=list,
        description="A list of Any Task model.",
    )

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> TaskGroup:
        """Build Airflow Task Group object."""
        task_group = TaskGroup(
            group_id=self.group,
            parent_group=task_group,
            dag=dag,
        )
        tasks: dict[str, TaskMapped] = {}
        for task in self.tasks:
            task_airflow: Operator | TaskGroup = task.build(
                dag=dag,
                task_group=task_group,
                context=context,
            )
            tasks[task.iden] = {"upstream": task.upstream, "task": task_airflow}

        # NOTE: Set Stream for subtask that set in this group.
        set_upstream(tasks)

        return task_group

    @property
    def iden(self) -> str:
        """Return Task Group Identity with it group name."""
        return self.group


def any_task_discriminator(v: Any) -> str | None:
    if isinstance(v, dict):
        if "group" in v:
            return "Group"
        elif "task" in v:
            return "Task"
        return None
    if hasattr(v, "group"):
        return "Group"
    elif hasattr(v, "task"):
        return "Task"
    # NOTE: Return None if the discriminator value isn't found
    return None


AnyTask = Annotated[
    Union[
        Annotated[Task, Tag("Task")],
        Annotated[GroupTask, Tag("Group")],
    ],
    Field(
        discriminator=Discriminator(discriminator=any_task_discriminator),
        description="An any task type that able operator task or group task.",
    ),
    # Archive: Keep for optional discriminator.
    # Discriminator(discriminator=any_task_discriminator)
    #
    # Archive: Keep for optional discriminator.
    # Field(
    #     union_mode="left_to_right",
    #     description="An any task type that able operator task or group task.",
    # ),
]
