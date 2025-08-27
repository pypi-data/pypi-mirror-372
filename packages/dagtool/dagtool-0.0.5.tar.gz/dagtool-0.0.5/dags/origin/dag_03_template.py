from pathlib import Path

from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

from dagtool.models import get_variable_stage
from dagtool.tasks.debug import DebugOperator

dag = DAG(
    dag_id="origin_template",
    start_date=days_ago(2),
    catchup=False,
    tags=["origin"],
    doc_md="doc.md",
    user_defined_macros={
        "custom_macros": "foo",
        "vars": get_variable_stage(Path(__file__).parent, name="template").get,
    },
)
task = EmptyOperator(task_id="test", dag=dag)
task_debug = DebugOperator(
    task_id="debug",
    dag=dag,
    debug={
        "test": "Hello World",
        "custom": "{{ custom_macros }}",
        "variable_1": "{{ vars('schedule_interval') }}",
        "variable_2": "{{ vars('project_id') }}",
    },
)
task_debug.set_upstream(task)
