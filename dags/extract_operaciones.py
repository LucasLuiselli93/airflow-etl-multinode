from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook # El hook de Azure
from datetime import datetime, timedelta
import pandas as pd

# CONFIGURACIÓN GLOBAL
NODOS = ['ar', 'br', 'cl']
LOCAL_TMP_PATH = '/opt/airflow/logs/'
CONTAINER_NAME = 'datos-maritimos'

def extraer_y_cargar(pais):
    # 1. Extracción (Lo que ya lograste)
    pg_hook = PostgresHook(postgres_conn_id=f'conn_node_{pais}')
    df = pg_hook.get_pandas_df("SELECT * FROM importaciones_maritimas")
    
    file_name = f"importaciones_{pais}.parquet"
    local_path = f"{LOCAL_TMP_PATH}{file_name}"
    df.to_parquet(local_path, index=False)
    print(f"Archivo {file_name} generado localmente.")

    # 2. Carga a Azure (El gran final)
    azure_hook = WasbHook(wasb_conn_id='azure_blob_connection')
    
    print(f"Subiendo {file_name} a Azure...")
    azure_hook.load_file(
        file_path=local_path,
        container_name=CONTAINER_NAME,
        blob_name=f"raw/{file_name}", # Lo guardamos en una carpeta virtual 'raw'
        overwrite=True
    )

default_args = {
    'owner': 'Lucas',
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id='etl_maritimo_to_azure',
    default_args=default_args,
    start_date=datetime(2026, 5, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    for pais in NODOS:
        PythonOperator(
            task_id=f'proceso_{pais}',
            python_callable=extraer_y_cargar,
            op_kwargs={'pais': pais}
        )