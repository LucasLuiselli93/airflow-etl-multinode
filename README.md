Multi-Node Sales ETL Pipeline: Postgres to Azure Data Lake

1. Resumen del Proyecto
Implementación de un pipeline de datos robusto diseñado para consolidar registros de operaciones en este caso marítimas provenientes de múltiples nodos transaccionales. El sistema automatiza la extracción concurrente, la optimización de archivos mediante transformación columnar y la ingesta final en una arquitectura de nube (Azure).

2. Diagrama de Arquitectura (Mermaid)
Fragmento de código
graph LR
    subgraph "Fuentes Locales (Docker)"
        A1[(Postgres AR)] 
        A2[(Postgres BR)] 
        A3[(Postgres CL)]
    end

    subgraph "Orquestación (Airflow)"
        B1{DAG Parallel Execution}
        B2[Extracción SQL]
        B3[Conversión Parquet]
    end

    subgraph "Cloud (Landing Zone)"
        C1[Azure Blob Storage]
        C2[Container: datos-maritimos]
    end

    A1 & A2 & A3 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> C1
    C1 --> C2
3. Especificaciones de Infraestructura
Contenerización: Despliegue integral mediante Docker Compose, incluyendo el orquestador Airflow y tres instancias independientes de PostgreSQL 13.

Persistencia de Datos: Configuración de volúmenes físicos en el host (./data/{pais}) mapeados a los contenedores para asegurar la durabilidad de los datos transaccionales frente a reinicios del stack.

Gestión de Secretos: Uso de variables de entorno y el motor de conexiones de Airflow para el manejo cifrado de credenciales de bases de datos y llaves de acceso de Azure.

4. Lógica del Pipeline (ETL)
Extracción Paralela: Uso de PostgresHook para ejecutar consultas SELECT simultáneas en los nodos de Argentina, Brasil y Chile, optimizando el tiempo total de procesamiento.

Transformación Columnar: Implementación de pandas y pyarrow para convertir los datasets relacionales a formato Parquet. Esta decisión reduce significativamente el peso de los objetos en la nube y acelera los tiempos de lectura para análisis posteriores.

Ingesta Cloud: Automatización de la carga mediante WasbHook hacia el contenedor datos-maritimos en Azure Blob Storage, organizando los archivos bajo una estructura de prefijos virtuales (raw/).

5. Troubleshooting y Registro de Soluciones
Durante el desarrollo se identificaron y resolvieron los siguientes puntos críticos:

Persistencia de Esquemas: Resolución del error UndefinedTable derivado de la volatilidad de los contenedores mediante la correcta implementación de volúmenes persistentes y scripts de inicialización (init_operaciones.sql).

Autenticación Azure: Corrección del error Unable to determine account name mediante el desacoplamiento de credenciales en la interfaz de Airflow. Se reemplazó el uso de cadenas de conexión complejas por la entrada granular de Login (Account Name) y Password (Access Key).

Aislamiento de Tareas: Migración del dag_id para evitar conflictos de metadatos en la base de datos interna de Airflow, permitiendo un seguimiento limpio de las ejecuciones exitosas.

6. Stack Tecnológico
Lenguaje: Python 3.10.

Orquestador: Apache Airflow 2.7.1.

Bases de Datos: PostgreSQL 13.

Cloud: Azure Blob Storage (WasbHook).

Formatos: Parquet (via PyArrow).