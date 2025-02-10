from datetime import datetime
from airflow import Dataset
from airflow.models import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pandas import DataFrame
import pandas as pd
import json

# Import decorators and classes from the SDK
from astro import sql as aql
from astro.files import File
from astro.sql.table import Table

# Import SQLAlchemy to set constraints on some temporary tables
import sqlalchemy

# Define constants/variables for interacting with external systems
SNOWFLAKE_CONN_ID = "snowflake_default"

# Define a function for transforming tables to dataframes and dataframe transformations
@aql.dataframe
def transform_dataframe(df: DataFrame):
    # Renaming columns as per needed column naming conventions
    df = df.rename(columns={"event_id": "event_id","event_time": "event_time","user_id" : "user_id","event.payload": "event_payload"})
    # Assigning row_number column
    df = df.assign(row_number=range(1,len(df)+1))
    df["event_payload"] = df["event_payload"].map(lambda x: json.loads(x))
    # Creating second dataframe only holding exploded JSON columns
    df_flat =pd.json_normalize(df['event_payload'])
    # Assigning rown_number column to second dataframe
    df_flat = df_flat.assign(row_number=range(1,len(df_flat)+1))
    # Merging raw dataframe and exploded json column holding dataframe into one dataframe
    result = pd.merge(df, df_flat, how="inner", on=["row_number"])
    # Sorting dataframe by latest event_time
    result = result.sort_values(by=['event_time'], ascending=False)
    # Drop unnecessary columns
    result = result.drop(['event_payload','row_number'],axis = 1)
    # Second column renaming for JSON exploded columns
    result = result.rename(columns={"platform": "event_platform","parameter": "event_parameter_name","user_id" : "event_user_id",
                                    "parameter_name": "event_parameter_name", "parameter_value": "event_parameter_value"})
    # Index column implementation
    result = result.assign(guid_event=range(1,len(result)+1))
    return result


@aql.run_raw_sql
def create_table(table: Table):
    """Create the user table data which will be the target of the merge method"""
    return """
      CREATE OR REPLACE TABLE {{table}} 
      (
      event_id VARCHAR(100),
      event_time DATETIME,
      event_user_id VARCHAR(100),
      event_name VARCHAR(100),
      event_platform VARCHAR(100),
      event_parameter_name VARCHAR(100),
      event_parameter_value VARCHAR(100),
      guid_event VARCHAR(100)
    );
    """

# Basic DAG definition
dag = DAG(
    dag_id="f_events_table_create",
    start_date=datetime(2024, 1, 12),
    schedule="@daily",
    catchup=False,
)

with dag:
    # Load data from raw layer tables into a variable (temp table) for further transformations
    event_data = Table(name="event_raw", temp=True, conn_id=SNOWFLAKE_CONN_ID)

    # Create the user table data which will be the target of the merge method
    f_events = Table(name="f_events", temp=True, conn_id=SNOWFLAKE_CONN_ID)
    create_f_events_table = create_table(table=f_events, conn_id=SNOWFLAKE_CONN_ID)


    # f_events table created and merged into snowflake table as delta loads arrive
    events_data = transform_dataframe((event_data),output_table = Table(
        conn_id=SNOWFLAKE_CONN_ID,
    ))

    # Merge statement for incremental refresh (update based on key column)
    events_data_merge = aql.merge(target_table=Table(
        name="f_events",
        conn_id=SNOWFLAKE_CONN_ID,),
        source_table = events_data,
        target_conflict_columns=["event_id","event_parameter_name","event_parameter_value"],
        columns=["event_id","event_time","event_user_id","event_name","event_platform"
                 ,"event_parameter_name","event_parameter_value","guid_event"],
        if_conflicts="update",
    )


    # Triggering next dag
    trigger_dependent_dag = TriggerDagRunOperator(
    task_id="trigger_dependent_dag",
    trigger_dag_id="aggregated_views",
    wait_for_completion=False,
    deferrable=False,  
    )

    # Dependencies
    create_f_events_table >>  events_data >> events_data_merge >> trigger_dependent_dag

# Delete temporary and unnamed tables created by `load_file` and `transform`, in this example
    aql.cleanup()