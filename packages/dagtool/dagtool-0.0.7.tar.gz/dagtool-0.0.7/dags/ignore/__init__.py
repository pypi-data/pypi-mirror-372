"""# Ignore DAGs

The ignored DAGs that generate from template config file.
"""

from airflow.utils.dates import days_ago

from dagtool import Factory

factory = Factory(name="ignore", path=__file__, docs=__doc__)
factory.build_airflow_dags_to_globals(
    gb=globals(),
    default_args={"start_date": days_ago(2)},
)
