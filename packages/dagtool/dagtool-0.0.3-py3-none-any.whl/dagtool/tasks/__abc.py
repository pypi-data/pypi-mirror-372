from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Literal, TypedDict

from airflow.models import DAG, Operator
from airflow.utils.task_group import TaskGroup
from pydantic import BaseModel, Field, field_validator


class Context(TypedDict):
    tasks: dict[str, type["BaseTask"]]
    operators: dict[str, type[Operator]]
    python_callers: dict[str, Callable]


class TaskMixin(ABC):
    """Task Mixin Abstract class override the build method."""

    @abstractmethod
    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator | TaskGroup:
        """Build Any Airflow Task object. This method can return Operator or
        TaskGroup object.
        """


class BaseTask(BaseModel, TaskMixin, ABC): ...


class BaseAirflowTask(BaseTask, ABC):
    """Base Task model that represent Airflow Task object."""

    desc: str | None = Field(
        default=None, description="A Airflow task description"
    )
    trigger_rule: str = Field(default="all_done")
    upstream: list[str] = Field(
        default_factory=list,
        validate_default=True,
        description=(
            "A list of upstream task name or only task name of this task."
        ),
    )

    @field_validator(
        "upstream",
        mode="before",
        json_schema_input_type=str | list[str] | None,
    )
    def __prepare_upstream(cls, data: Any) -> Any:
        """Prepare upstream value that passing to validate with string value
        instead of list of string. This function will create list of this value.
        """
        if data is None:
            return []
        elif data and isinstance(data, str):
            return [data]
        return data

    @property
    @abstractmethod
    def iden(self) -> str:
        """Task identity Abstract method for making represent task_id or group_id
        for Airflow object.
        """


class OperatorTask(BaseAirflowTask, ABC):
    """Operator Task Model."""

    task: str = Field(description="A task name.")
    type: Literal["task"] = Field(default="task")
    op: str = Field(description="An operator type of this task.")
    inlets: list[dict[str, Any]] = Field(default_factory=list)
    outlets: list[dict[str, Any]] = Field(default_factory=list)

    @abstractmethod
    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build the Airflow Operator object from this model fields."""

    @property
    def iden(self) -> str:
        """Return the task field value for represent task_id in Airflow Task
        Instance.
        """
        return self.task

    def task_kwargs(self) -> dict[str, Any]:
        """Prepare Airflow BaseOperator kwargs from OperatorTask model field."""
        kws: dict[str, Any] = {"task_id": self.iden}
        if self.desc:
            kws.update({"doc": self.desc})
        if self.inlets:
            kws.update({"inlets": self.inlets})
        if self.outlets:
            kws.update({"outlets": self.outlets})
        return kws
