from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
from datetime import datetime, timedelta
import polars as pl
import os

# CONFIGURACIÓN GLOBAL
NODOS = ['ar', 'br', 'cl']
LOCAL_TMP_PATH = '/tmp/'
CONTAINER_NAME = 'datos-maritimos'

def extraer_y_cargar(pais):
    """Extrae datos limpiando metadatos de Airflow para compatibilidad con ADBC."""
    pg_hook = PostgresHook(postgres_conn_id=f'conn_node_{pais}')
    
    # 1. Obtener y limpiar el URI de parámetros internos (__extra__)
    uri_raw = pg_hook.get_uri()
    uri = uri_raw.split("?")[0] # Elimina cualquier query string que ADBC rechace
    
    # Normalización del esquema
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    # 2. Ingesta de alto rendimiento
    df = pl.read_database_uri(
        query="SELECT * FROM importaciones_maritimas",
        uri=uri,
        engine="adbc"
    )
    
    file_name = f"importaciones_{pais}.parquet"
    local_path = os.path.join(LOCAL_TMP_PATH, file_name)
    
    # 3. Persistencia local
    df.write_parquet(local_path, compression="snappy")
    
    # 4. Ingesta a Azure Raw
    azure_hook = WasbHook(wasb_conn_id='azure_blob_connection')
    azure_hook.load_file(
        file_path=local_path,
        container_name=CONTAINER_NAME,
        blob_name=f"raw/{file_name}",
        overwrite=True
    )

def consolidar_datasets():
    """Unión masiva de 1.5M de registros mediante Lazy Evaluation."""
    archivos_locales = [os.path.join(LOCAL_TMP_PATH, f"importaciones_{p}.parquet") for p in NODOS]
    
    archivos_validos = [f for f in archivos_locales if os.path.exists(f)]
    if len(archivos_validos) < len(NODOS):
        raise FileNotFoundError(f"Dataset incompleto. Encontrados {len(archivos_validos)}/3 archivos.")

    # Lazy Frame para optimizar el plan de ejecución de 1.5M de filas
    df_final = pl.scan_parquet(archivos_validos).collect()
    
    output_path = os.path.join(LOCAL_TMP_PATH, "consolidado_global.parquet")
    df_final.write_parquet(output_path, compression="snappy")
    
    # Subida a Azure Processed (Capa Gold)
    azure_hook = WasbHook(wasb_conn_id='azure_blob_connection')
    azure_hook.load_file(
        file_path=output_path,
        container_name=CONTAINER_NAME,
        blob_name='processed/consolidado_global.parquet',
        overwrite=True
    )

default_args = {
    'owner': 'Lucas',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='etl_maritimo_to_azure',
    default_args=default_args,
    description='Pipeline Multinodo Optimizado (Fix ADBC URI)',
    schedule_interval='@daily',
    catchup=False
) as dag:

    task_ar = PythonOperator(task_id='proceso_ar', python_callable=extraer_y_cargar, op_kwargs={'pais': 'ar'})
    task_br = PythonOperator(task_id='proceso_br', python_callable=extraer_y_cargar, op_kwargs={'pais': 'br'})
    task_cl = PythonOperator(task_id='proceso_cl', python_callable=extraer_y_cargar, op_kwargs={'pais': 'cl'})

    task_union = PythonOperator(task_id='consolidar_y_subir_global', python_callable=consolidar_datasets)

    [task_ar, task_br, task_cl] >> task_union